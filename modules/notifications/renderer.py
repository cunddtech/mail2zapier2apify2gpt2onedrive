"""Unified notification renderer for Railway orchestrator emails."""

from __future__ import annotations

import html
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pytz

from modules.auth.button_tokens import create_button_url
from modules.pricing.estimate_from_call import ProjectEstimate, format_estimate_for_email

BERLIN_TZ = pytz.timezone("Europe/Berlin")
logger = logging.getLogger(__name__)


def now_berlin() -> datetime:
    """Return current datetime in Berlin timezone."""

    return datetime.now(BERLIN_TZ)


def escape_braces(value: Optional[Any]) -> str:
    """Escape curly braces so f-strings can safely interpolate the value."""

    if value is None:
        return ""
    return str(value).replace("{", "{{").replace("}", "}}")


def compact_dict(payload: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Remove empty values while keeping falsy-but-valid entries like 0 or False."""

    if not isinstance(payload, dict):
        return {}

    cleaned: Dict[str, Any] = {}
    for key, value in payload.items():
        if value is None:
            continue
        if isinstance(value, str) and value.strip() == "":
            continue
        if isinstance(value, (list, tuple, set, dict)) and len(value) == 0:
            continue
        cleaned[key] = value
    return cleaned


def format_size(size: Optional[int]) -> str:
    """Human readable file size representation."""

    if not isinstance(size, (int, float)) or size < 0:
        return "unbekannt"
    if size >= 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"
    if size >= 1024:
        return f"{size / 1024:.1f} KB"
    return f"{int(size)} B"


class NotificationRenderer:
    """Render unified notification HTML for WEG A/B workflows."""

    BUTTON_CLASS_MAP = {
        "create_contact": "btn-create",
        "create_supplier": "btn-supplier",
        "add_to_existing": "btn-primary",
        "assign_to_existing": "btn-primary",
        "mark_private": "btn-private",
        "mark_spam": "btn-spam",
        "request_info": "btn-info",
        "data_good": "btn-success",
        "data_error": "btn-warning",
        "report_issue": "btn-secondary",
        "view_in_crm": "btn-info",
        "schedule_appointment": "btn-primary",
        "create_quote": "btn-success",
        "call_customer": "btn-info",
        "create_order": "btn-create",
        "order_supplier": "btn-info",
        "send_order_confirmation": "btn-primary",
        "create_advance_invoice": "btn-success",
        "schedule_installation": "btn-warning",
        "urgent_response": "btn-warning",
        "complete_task": "btn-secondary",
        "primary": "btn-primary",
        "success": "btn-success",
        "info": "btn-info",
        "warning": "btn-warning",
        "secondary": "btn-secondary",
        "create": "btn-create",
        "btn-primary": "btn-primary",
        "btn-success": "btn-success",
        "btn-info": "btn-info",
        "btn-warning": "btn-warning",
        "btn-secondary": "btn-secondary",
        "btn-create": "btn-create",
        "btn-supplier": "btn-supplier",
        "btn-private": "btn-private",
        "btn-spam": "btn-spam",
    }

    URGENCY_THEME = {
        "urgent": {"color": "#FF1744", "background": "#FFEBEE"},
        "high": {"color": "#FB8C00", "background": "#FFF3E0"},
        "medium": {"color": "#FFC107", "background": "#FFF8E1"},
        "low": {"color": "#26A69A", "background": "#E0F2F1"},
    }

    PRIORITY_EMOJI = {
        "urgent": "🔴",
        "high": "🔴",
        "medium": "🟡",
        "low": "🟢",
    }

    def __init__(
        self,
        notification_data: Dict[str, Any],
        base_url: str,
        communication_uuid: str,
        email_message_id: str,
    ) -> None:
        self.data = notification_data
        self.base_url = base_url
        self.communication_uuid = communication_uuid
        self.email_message_id = email_message_id
        self.now = now_berlin()

        self.notification_type = self.data.get("notification_type", "unknown_contact_action_required")
        self.is_known_contact = self.notification_type == "known_contact_enhanced"
        self.channel = self.data.get("channel") or self.data.get("message_type") or "email"

        self.intelligence = self._extract_intelligence()
        self.ai_analysis = self.data.get("ai_analysis") or {}
        self.smart_notification = self.data.get("smart_notification") or {}

        self.contact_prefill = self._build_contact_prefill()
        self.contact_match = self.data.get("contact_match") or {}
        self.contact_id = self.contact_match.get("contact_id")
        self.opportunity_stage = self.data.get("opportunity_stage") or self.ai_analysis.get("opportunity_stage")
        self.opportunity_id = self.data.get("opportunity_id")
        self.probability = self.data.get("opportunity_probability")

        self.urgency = self._determine_urgency()
        self.summary_text = self._resolve_summary()
        self.body_preview = str(
            self.data.get("body_preview")
            or self.data.get("content_preview")
            or self.data.get("body_plain")
            or ""
        )

        self.tasks_generated = self.data.get("tasks_generated") or []
        self.action_options = self.data.get("action_options") or []

        self.attachments = self.data.get("attachment_results") or []
        self.attachments_count = self.data.get("attachments_count", len(self.attachments))
        self.onedrive_links = self.data.get("onedrive_links") or []

        self.price_estimate = self.data.get("price_estimate")
        self.has_price_estimate = self.data.get("has_price_estimate") or (
            isinstance(self.price_estimate, dict) and self.price_estimate.get("found")
        )

        self.sender_display = (
            self.data.get("sender_display")
            or self.data.get("sender")
            or self.data.get("from")
            or "Unbekannt"
        )
        self.received_time = self.data.get("received_time") or self.data.get("timestamp")
        self.subject = self.data.get("subject", "")

    # ------------------------------------------------------------------ helpers
    def _extract_intelligence(self) -> Dict[str, Any]:
        candidate = self.data.get("intelligence_analysis")
        if isinstance(candidate, dict):
            return candidate

        ai_block = self.data.get("ai_analysis")
        if isinstance(ai_block, dict):
            nested = ai_block.get("intelligence_analysis")
            if isinstance(nested, dict):
                return nested

        additional = self.data.get("additional_data")
        if isinstance(additional, dict):
            nested = additional.get("intelligence_analysis")
            if isinstance(nested, dict):
                return nested

        return {}

    def _build_contact_prefill(self) -> Dict[str, Any]:
        prefill: Dict[str, Any] = {}
        if isinstance(self.intelligence, dict):
            candidate = self.intelligence.get("contact_prefill")
            if isinstance(candidate, dict):
                prefill.update(candidate)
        candidate_prefill = self.data.get("contact_prefill")
        if isinstance(candidate_prefill, dict):
            prefill.update(candidate_prefill)
        return prefill

    def _determine_urgency(self) -> Dict[str, Any]:
        urgency: Optional[Dict[str, Any]] = None
        if isinstance(self.intelligence, dict):
            candidate = self.intelligence.get("urgency")
            if isinstance(candidate, dict):
                urgency = candidate

        if urgency is None:
            ai_urgency = self.ai_analysis.get("urgency")
            if isinstance(ai_urgency, dict):
                urgency = ai_urgency
            elif isinstance(ai_urgency, str):
                urgency = {"level": ai_urgency, "reason": self.ai_analysis.get("urgency_reason", "")}

        if urgency is None:
            urgency = {"level": "medium", "reason": "Standard-Priorität"}

        level = (urgency.get("level") or "medium").lower()
        theme = self.URGENCY_THEME.get(level, self.URGENCY_THEME["medium"])

        return {
            "level": level,
            "label": level.upper(),
            "reason": urgency.get("reason") or urgency.get("details") or "",
            "score": urgency.get("score"),
            "color": theme["color"],
            "background": theme["background"],
        }

    def _resolve_summary(self) -> str:
        for candidate in (
            self.data.get("summary"),
            self.smart_notification.get("summary"),
            self.ai_analysis.get("summary"),
            self.intelligence.get("summary"),
        ):
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()

        preview = self.body_preview.strip()
        if len(preview) > 280:
            preview = preview[:277] + "..."
        return preview

    def _collect_tasks(self) -> List[Dict[str, Any]]:
        tasks: List[Dict[str, Any]] = []

        for task in self.tasks_generated:
            title = task.get("title") or task.get("label")
            if not title:
                continue
            tasks.append(
                {
                    "title": title,
                    "priority": (task.get("priority") or "medium").lower(),
                    "deadline": self._parse_deadline(task.get("deadline"), task.get("deadline_hours")),
                }
            )

        suggested = []
        if isinstance(self.intelligence, dict):
            suggested = self.intelligence.get("suggested_actions") or []

        for action in suggested:
            label = action.get("label") or action.get("action")
            if not label:
                continue
            tasks.append(
                {
                    "title": label,
                    "priority": (action.get("priority") or "medium").lower(),
                    "deadline": self._parse_deadline(action.get("deadline"), action.get("deadline_hours")),
                }
            )

        return tasks

    def _parse_deadline(
        self,
        explicit_deadline: Optional[Any],
        deadline_hours: Optional[Any],
    ) -> Optional[str]:
        if deadline_hours:
            try:
                hours_value = float(deadline_hours)
                deadline_dt = self.now + timedelta(hours=hours_value)
                return deadline_dt.strftime("%d.%m.%Y %H:%M Uhr")
            except Exception:
                pass

        if explicit_deadline:
            return str(explicit_deadline)
        return None

    def _collect_onedrive_links(self) -> List[Dict[str, str]]:
        links: List[Dict[str, str]] = []
        seen = set()

        for result in self.attachments:
            link = result.get("onedrive_sharing_link") or result.get("onedrive_web_url")
            if not link:
                continue
            key = (link, result.get("filename"))
            if key in seen:
                continue
            seen.add(key)
            links.append({"filename": result.get("filename") or "Datei", "link": link})

        for info in self.onedrive_links:
            if not isinstance(info, dict):
                continue
            link = info.get("sharing_link") or info.get("web_url") or info.get("link")
            if not link:
                continue
            key = (link, info.get("filename"))
            if key in seen:
                continue
            seen.add(key)
            links.append({"filename": info.get("filename") or "Datei", "link": link})

        return links

    def _contact_payload(self) -> Dict[str, Any]:
        payload = {
            "name": self.contact_prefill.get("customer_name") or self.contact_match.get("contact_name"),
            "email": self.contact_prefill.get("email") or self.data.get("sender") or self.data.get("from"),
            "phone": self.contact_prefill.get("phone") or self.contact_match.get("phone"),
            "company": self.contact_prefill.get("company_name") or self.contact_match.get("company"),
            "address": self.contact_prefill.get("address"),
        }
        return compact_dict(payload)

    # ---------------------------------------------------------------- rendering
    def render(self) -> str:
        sections: List[str] = []
        sections.extend(
            filter(
                None,
                [
                    self._build_summary_section(),
                    self._build_contact_section(),
                    self._build_intelligence_section(),
                    self._build_tasks_section(),
                    self._build_attachments_section(),
                    self._build_onedrive_section(),
                    self._build_dashboard_section(),
                    self._build_price_section(),
                    self._build_buttons_section(),
                ],
            )
        )

        content_html = "\n".join(sections)
        header_html = self._build_header_html()
        footer_html = self._build_footer_html()

        return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #F5F7FA; margin: 0; padding: 20px; color: #2C3E50; }}
    .container {{ max-width: 720px; margin: 0 auto; background: #FFFFFF; border-radius: 18px; box-shadow: 0 12px 35px rgba(31, 45, 61, 0.08); overflow: hidden; }}
    .header {{ background: linear-gradient(135deg, #485563 0%, #29323C 100%); padding: 32px; color: white; text-align: center; }}
    .header h2 {{ margin: 0 0 10px 0; font-size: 24px; letter-spacing: 0.5px; }}
    .header p {{ margin: 0; font-size: 14px; opacity: 0.8; }}
    .badge {{ display: inline-block; margin-left: 8px; padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; }}
    .content {{ padding: 28px 32px 34px 32px; }}
    .section {{ margin-bottom: 24px; border-radius: 12px; padding: 20px; background: #F9FAFB; border: 1px solid #E5E9F2; }}
    .section h3 {{ margin-top: 0; font-size: 18px; display: flex; align-items: center; gap: 8px; color: #1F2D3D; }}
    .summary-main {{ font-weight: 600; margin-bottom: 12px; }}
    .message-preview {{ background: #FFFFFF; border: 1px solid #E5E9F2; border-radius: 10px; padding: 16px; font-size: 14px; color: #34495E; }}
    .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px 18px; margin: 0; padding: 0; list-style: none; }}
    .summary-grid dt {{ font-weight: 600; font-size: 13px; color: #5C7080; }}
    .summary-grid dd {{ margin: 0; font-size: 14px; color: #1F2D3D; }}
    .task-list {{ list-style: none; padding-left: 0; margin: 0; }}
    .task-list li {{ margin-bottom: 10px; font-size: 14px; line-height: 1.5; }}
    .task-meta {{ display: inline-block; font-size: 12px; color: #7F8C8D; margin-left: 8px; }}
    .attachments ul, .links ul {{ list-style: none; padding: 0; margin: 0; }}
    .attachments li, .links li {{ padding: 10px 0; border-bottom: 1px solid #E5E9F2; font-size: 14px; }}
    .attachments li:last-child, .links li:last-child {{ border-bottom: none; }}
    .attachment-meta {{ display: block; font-size: 12px; color: #7F8C8D; margin-left: 22px; line-height: 1.4; }}
    .buttons {{ display: flex; flex-direction: column; gap: 14px; }}
    .button-wrapper {{ text-align: center; }}
    .button {{ display: inline-block; padding: 13px 28px; border-radius: 30px; font-weight: 600; text-decoration: none; color: white; transition: transform 0.2s ease, box-shadow 0.2s ease; box-shadow: 0 6px 18px rgba(41, 128, 185, 0.15); }}
    .button:hover {{ transform: translateY(-2px); box-shadow: 0 10px 24px rgba(41, 128, 185, 0.25); }}
    .button-desc {{ margin: 8px 0 0 0; font-size: 12px; color: #5C7080; }}
    .btn-primary {{ background: linear-gradient(135deg, #3498DB 0%, #2980B9 100%); }}
    .btn-success {{ background: linear-gradient(135deg, #2ECC71 0%, #27AE60 100%); }}
    .btn-warning {{ background: linear-gradient(135deg, #F39C12 0%, #D35400 100%); }}
    .btn-secondary {{ background: linear-gradient(135deg, #95A5A6 0%, #7F8C8D 100%); }}
    .btn-info {{ background: linear-gradient(135deg, #74B9FF 0%, #0984E3 100%); }}
    .btn-create {{ background: linear-gradient(135deg, #52C234 0%, #047857 100%); }}
    .btn-supplier {{ background: linear-gradient(135deg, #FD79A8 0%, #E84393 100%); }}
    .btn-private {{ background: linear-gradient(135deg, #A29BFE 0%, #6C5CE7 100%); }}
    .btn-spam {{ background: linear-gradient(135deg, #FF7675 0%, #D63031 100%); }}
    .footer {{ background: #F1F3F6; padding: 18px 32px; font-size: 12px; color: #60718B; border-top: 1px solid #E5E9F2; }}
    .footer p {{ margin: 4px 0; }}
</style>
</head>
<body>
<div class="container">
{header_html}
<div class="content">
{content_html}
</div>
{footer_html}
</div>
</body>
</html>
"""

    def _build_header_html(self) -> str:
        icon = "📧" if self.channel == "email" else "📞" if self.channel == "call" else "💬" if self.channel == "whatsapp" else "🆕"
        if self.is_known_contact:
            icon = "✅"
        title = "Unbekannter Kontakt – Aktion erforderlich" if not self.is_known_contact else "Kontakt erkannt"
        if self.is_known_contact and self.opportunity_stage:
            title += f" · Phase {self.opportunity_stage}"
        subtitle_parts: List[str] = [self.channel.upper()]
        if self.is_known_contact and self.probability is not None:
            subtitle_parts.append(f"Wahrscheinlichkeit {self.probability}%")
        if self.received_time:
            subtitle_parts.append(self._format_received_time())
        subtitle = " | ".join(part for part in subtitle_parts if part)
        badge = (
            f"<span class='badge' style='background:{self.urgency['background']};color:{self.urgency['color']};'>"
            f"{self.urgency['label']}</span>"
        )
        return (
            "<div class=\"header\">"
            f"<h2>{escape_braces(f'{icon} {title}')} {badge}</h2>"
            f"<p>{escape_braces(subtitle)}</p>"
            "</div>"
        )

    def _format_received_time(self) -> str:
        try:
            dt = datetime.fromisoformat(str(self.received_time).replace("Z", "+00:00"))
            dt_berlin = dt.astimezone(BERLIN_TZ)
            return dt_berlin.strftime("%d.%m.%Y %H:%M Uhr")
        except Exception:
            return str(self.received_time)

    def _build_summary_section(self) -> str:
        if not self.summary_text and not self.body_preview:
            return ""
        parts: List[str] = []
        if self.summary_text:
            parts.append(f"<p class='summary-main'>{self._format_multiline(self.summary_text)}</p>")
        if self.body_preview:
            parts.append(f"<div class='message-preview'>{self._format_multiline(self.body_preview)}</div>")
        if self.urgency.get("reason"):
            parts.append(
                f"<p style='font-size:13px;color:#7F8C8D;margin-top:12px;'>⚡ {escape_braces(self.urgency['reason'])}</p>"
            )
        content = "".join(parts)
        return f"<div class='section summary'><h3>📝 Zusammenfassung</h3>{content}</div>"

    def _build_contact_section(self) -> str:
        rows: List[str] = []
        if self.is_known_contact:
            if self.contact_match.get("contact_name"):
                rows.append(self._summary_row("Kontakt", self.contact_match.get("contact_name")))
            if self.contact_match.get("company"):
                rows.append(self._summary_row("Firma", self.contact_match.get("company")))
            if self.contact_id:
                rows.append(self._summary_row("WeClapp-ID", self.contact_id))
            if self.opportunity_id:
                rows.append(self._summary_row("Opportunity-ID", self.opportunity_id))
            if self.opportunity_stage:
                stage_text = self.opportunity_stage
                if self.probability is not None:
                    stage_text += f" ({self.probability}%)"
                rows.append(self._summary_row("Phase", stage_text))
        else:
            rows.append(self._summary_row("Absender", self.sender_display))
            rows.append(self._summary_row("Adresse", self.data.get("sender") or self.data.get("from") or "N/A"))
            rows.append(self._summary_row("Kanal", self.channel.upper()))
        if self.contact_prefill.get("phone"):
            rows.append(self._summary_row("Telefon", self.contact_prefill.get("phone")))
        if self.contact_prefill.get("email") and not self.is_known_contact:
            rows.append(self._summary_row("Email", self.contact_prefill.get("email")))
        if self.contact_prefill.get("project_type"):
            rows.append(self._summary_row("Projekt", self.contact_prefill.get("project_type")))
        if not rows:
            return ""
        rows_html = "".join(rows)
        return f"<div class='section contact'><h3>👤 Basisinformationen</h3><dl class='summary-grid'>{rows_html}</dl></div>"

    def _summary_row(self, label: Any, value: Any) -> str:
        return f"<div><dt>{escape_braces(label)}</dt><dd>{escape_braces(value)}</dd></div>"

    def _build_intelligence_section(self) -> str:
        intent_data = None
        if isinstance(self.intelligence, dict):
            intent_data = self.intelligence.get("intent")
        if not isinstance(intent_data, dict):
            intent = self.ai_analysis.get("intent")
            if isinstance(intent, dict):
                intent_data = intent

        sentiment = self.ai_analysis.get("sentiment")
        key_topics = self.ai_analysis.get("key_topics") or self.smart_notification.get("key_topics") or []

        rows: List[str] = []
        if isinstance(intent_data, dict):
            intent_label = intent_data.get("primary") or intent_data.get("label")
            confidence = intent_data.get("confidence")
            intent_text = intent_label or "unbekannt"
            if confidence is not None:
                intent_text += f" ({confidence*100:.0f}%)"
            rows.append(self._summary_row("Absicht", intent_text))
        if sentiment:
            rows.append(self._summary_row("Stimmung", sentiment))
        if key_topics:
            rows.append(self._summary_row("Schwerpunkte", ", ".join(key_topics[:5])))
        if self.urgency.get("reason"):
            rows.append(
                self._summary_row(
                    "Dringlichkeit",
                    f"{self.urgency['label']} – {self.urgency['reason']}",
                )
            )
        if not rows:
            return ""
        rows_html = "".join(rows)
        return f"<div class='section intelligence'><h3>🧠 KI-Analyse</h3><dl class='summary-grid'>{rows_html}</dl></div>"

    def _build_tasks_section(self) -> str:
        tasks = self._collect_tasks()
        if not tasks:
            return ""
        items = []
        for task in tasks:
            emoji = self.PRIORITY_EMOJI.get(task["priority"], "🟢")
            text = f"{emoji} {escape_braces(task['title'])}"
            if task["deadline"]:
                text += f"<span class='task-meta'>(bis {escape_braces(task['deadline'])})</span>"
            items.append(f"<li>{text}</li>")
        items_html = "".join(items)
        return f"<div class='section tasks'><h3>✅ Aufgaben & ToDos</h3><ul class='task-list'>{items_html}</ul></div>"

    def _build_attachments_section(self) -> str:
        if self.attachments_count == 0:
            return ""
        if not self.attachments:
            info = escape_braces(f"{self.attachments_count} Datei(en) verarbeitet")
            return f"<div class='section attachments'><h3>📎 Anhänge</h3><p>{info}</p></div>"
        items = []
        for attachment in self.attachments:
            name = attachment.get("filename") or "Unbekannt"
            size = format_size(attachment.get("size") or attachment.get("size_bytes"))
            doc_type = attachment.get("document_type") or attachment.get("classified_as") or "unbekannt"
            route = attachment.get("ocr_route") or "none"
            parts = [f"<strong>{escape_braces(name)}</strong> ({escape_braces(size)})"]
            parts.append(f"<span class='attachment-meta'>🏷️ Typ: {escape_braces(doc_type)}</span>")
            parts.append(f"<span class='attachment-meta'>🔍 Verarbeitung: {escape_braces(route)}</span>")
            ocr_text = attachment.get("ocr_text")
            if ocr_text and not ocr_text.startswith("[OCR Placeholder"):
                preview = ocr_text.strip()
                if len(preview) > 200:
                    preview = preview[:197] + "..."
                parts.append(f"<span class='attachment-meta'>📝 {escape_braces(preview)}</span>")
            structured = attachment.get("structured_data") or {}
            if structured.get("invoice_number"):
                parts.append(f"<span class='attachment-meta'>🔢 Rechnungs-Nr: {escape_braces(structured['invoice_number'])}</span>")
            if structured.get("total_amount"):
                parts.append(f"<span class='attachment-meta'>💰 Betrag: {escape_braces(structured['total_amount'])}</span>")
            if structured.get("vendor_name"):
                parts.append(f"<span class='attachment-meta'>🏢 Lieferant: {escape_braces(structured['vendor_name'])}</span>")
            if structured.get("invoice_date"):
                parts.append(f"<span class='attachment-meta'>📅 Rechnungsdatum: {escape_braces(structured['invoice_date'])}</span>")
            if structured.get("due_date"):
                parts.append(f"<span class='attachment-meta'>⏰ Fällig am: {escape_braces(structured['due_date'])}</span>")
            if structured.get("direction"):
                direction_icon = "📥" if structured["direction"] == "incoming" else "📤"
                direction_text = "Eingang (AN uns)" if structured["direction"] == "incoming" else "Ausgang (VON uns)"
                parts.append(f"<span class='attachment-meta'>{direction_icon} {direction_text}</span>")
            link = attachment.get("onedrive_sharing_link") or attachment.get("onedrive_web_url")
            if link:
                parts.append(f"<span class='attachment-meta'>🔗 <a href='{link}' target='_blank'>OneDrive öffnen</a></span>")
            path = attachment.get("onedrive_path")
            if path:
                parts.append(f"<span class='attachment-meta'>📂 Ablage: {escape_braces(path)}</span>")
            items.append(f"<li>{''.join(parts)}</li>")
        items_html = "".join(items)
        return f"<div class='section attachments'><h3>📎 Anhänge ({self.attachments_count})</h3><ul>{items_html}</ul></div>"

    def _build_onedrive_section(self) -> str:
        links = self._collect_onedrive_links()
        if not links:
            return ""
        items = [
            f"<li>☁️ <a href='{link['link']}' target='_blank'>{escape_braces(link['filename'])}</a></li>"
            for link in links
        ]
        items_html = "".join(items)
        return f"<div class='section links'><h3>☁️ OneDrive & Ablagen</h3><ul>{items_html}</ul></div>"

    def _build_dashboard_section(self) -> str:
        links: List[str] = []
        invoice_id = self.data.get("invoice_id") or self.data.get("invoice_number")
        opportunity_id = self.opportunity_id
        if invoice_id:
            invoice_number = self.data.get("invoice_number") or invoice_id
            links.append(
                f"📄 <a href='{self.base_url}/api/invoice/{invoice_number}' target='_blank'>Rechnung {escape_braces(invoice_number)} öffnen</a>"
            )
        if opportunity_id:
            title = self.data.get("opportunity_title") or f"Opportunity #{opportunity_id}"
            links.append(
                f"💼 <a href='{self.base_url}/api/opportunity/{opportunity_id}' target='_blank'>{escape_braces(title)}</a>"
            )
        links.append("📊 <a href='http://localhost:3000' target='_blank'>Invoice & Payment Dashboard</a>")
        links.append("💰 <a href='http://localhost:3000/sales-pipeline' target='_blank'>Sales Pipeline Dashboard</a>")
        links_html = "<br>".join(links)
        return f"<div class='section dashboards'><h3>🔗 Relevante Links</h3><p>{links_html}</p></div>"

    def _build_price_section(self) -> str:
        if not self.has_price_estimate or not isinstance(self.price_estimate, dict):
            return ""
        try:
            estimate_dict = self.price_estimate
            if estimate_dict.get("found") is False:
                return ""
            estimate = ProjectEstimate(
                found=estimate_dict.get("found", True),
                project_type=estimate_dict.get("project_type", ""),
                area_sqm=estimate_dict.get("area_sqm"),
                material=estimate_dict.get("material", ""),
                work_type=estimate_dict.get("work_type", ""),
                material_cost=estimate_dict.get("material_cost", 0.0),
                labor_cost=estimate_dict.get("labor_cost", 0.0),
                additional_cost=estimate_dict.get("additional_cost", 0.0),
                total_cost=estimate_dict.get("total_cost", 0.0),
                confidence=estimate_dict.get("confidence", 0.0),
                calculation_basis=estimate_dict.get("calculation_basis", []),
                additional_services=estimate_dict.get("additional_services", []),
                notes=estimate_dict.get("notes", ""),
            )
            estimate_html = format_estimate_for_email(estimate)
            return f"<div class='section price'><h3>💶 Automatische Preisschätzung</h3>{estimate_html}</div>"
        except Exception as exc:
            logger.warning("⚠️ Could not render price estimate: %s", exc)
            return ""

    def _build_buttons_section(self) -> str:
        button_html = []
        for option in self.action_options:
            rendered = self._render_button(option)
            if rendered:
                button_html.append(rendered)
        if not button_html:
            return ""
        return (
            "<div class='section actions'><h3>🎯 Empfohlene Aktionen</h3>"
            f"<div class='buttons'>{''.join(button_html)}</div>"
            "</div>"
        )

    def _render_button(self, option: Optional[Dict[str, Any]]) -> Optional[str]:
        if not isinstance(option, dict):
            return None
        action = option.get("action") or option.get("action_type") or "action"
        label = option.get("label") or option.get("title") or action
        description = option.get("description") or ""
        color_key = option.get("color") or action
        css_class = self.BUTTON_CLASS_MAP.get(color_key, self.BUTTON_CLASS_MAP.get(action, "btn-primary"))
        url = option.get("url")

        if not url:
            action_config = self._build_action_config(option, description)
            url = create_button_url(
                base_url=self.base_url,
                action_type=action,
                email_message_id=self.email_message_id,
                communication_uuid=self.communication_uuid,
                action_config=action_config,
                action_label=label,
                button_color=css_class,
            )

        return (
            "<div class='button-wrapper'>"
            f"<a href='{url}' class='button {css_class}' target='_blank'>{escape_braces(label)}</a>"
            f"<p class='button-desc'>{escape_braces(description)}</p>"
            "</div>"
        )

    def _build_action_config(self, option: Dict[str, Any], description: str) -> Dict[str, Any]:
        config: Dict[str, Any] = {}
        if self.is_known_contact:
            config.update(
                {
                    "contact_id": self.contact_id,
                    "contact_name": self.contact_match.get("contact_name"),
                    "opportunity_id": self.opportunity_id,
                    "opportunity_stage": self.opportunity_stage,
                    "description": description,
                    "channel": self.channel,
                }
            )
        else:
            config.update(
                {
                    "sender": self.data.get("sender") or self.data.get("from"),
                    "email_id": self.data.get("email_id") or self.data.get("message_id"),
                    "subject": self.subject,
                    "body_preview": self.body_preview,
                    "description": description,
                    "channel": self.channel,
                }
            )

        contact_payload = self._contact_payload()
        if contact_payload:
            config.setdefault("contact_payload", contact_payload)
        if self.contact_prefill:
            config.setdefault("contact_prefill", self.contact_prefill)
        if isinstance(self.intelligence, dict) and self.intelligence:
            config.setdefault("intelligence_analysis", self.intelligence)

        # Enrich for specific actions
        action = option.get("action") or option.get("action_type")
        if not self.is_known_contact and action == "create_contact":
            notes = self.data.get("message_preview") or self.body_preview
            config.update(
                {
                    "name": contact_payload.get("name") or self.data.get("sender_name") or self.data.get("from_name"),
                    "email": contact_payload.get("email") or self.data.get("sender"),
                    "phone": contact_payload.get("phone") or self.data.get("sender_phone"),
                    "company": contact_payload.get("company") or self.ai_analysis.get("company"),
                    "address": contact_payload.get("address") or self.ai_analysis.get("address"),
                    "notes": notes,
                    "inquiry": self.body_preview,
                    "message": self.body_preview,
                }
            )
        elif not self.is_known_contact and action == "create_supplier":
            notes = self.data.get("message_preview") or self.body_preview
            config.update(
                {
                    "contact_name": contact_payload.get("name") or self.data.get("sender_name"),
                    "contact_email": contact_payload.get("email") or self.data.get("sender"),
                    "contact_phone": contact_payload.get("phone") or self.data.get("sender_phone"),
                    "company": contact_payload.get("company") or self.ai_analysis.get("company"),
                    "supplier_name": contact_payload.get("company") or self.ai_analysis.get("supplier"),
                    "address": contact_payload.get("address") or self.ai_analysis.get("address"),
                    "notes": notes,
                }
            )

        option_config = option.get("config")
        if isinstance(option_config, dict):
            config.update(option_config)

        for key in ("intelligence_metadata", "metadata"):
            meta = option.get(key)
            if isinstance(meta, dict):
                config.setdefault("intelligence_metadata", meta)

        return compact_dict(config)

    def _build_footer_html(self) -> str:
        details = [
            f"UUID: {self.communication_uuid}",
            f"Message-ID: {self.email_message_id}",
            f"Generiert am {self.now.strftime('%d.%m.%Y %H:%M')} Uhr",
        ]
        detail_html = " | ".join(escape_braces(part) for part in details)
        return (
            "<div class='footer'>"
            f"<p>{detail_html}</p>"
            "<p>🤖 Automatisch generiert vom C&amp;D Lead Management System</p>"
            "</div>"
        )

    def _format_multiline(self, value: str) -> str:
        escaped = html.escape(value)
        return escape_braces(escaped).replace("\n", "<br>")


def render_notification_html(
    notification_data: Dict[str, Any],
    base_url: str,
    communication_uuid: str,
    email_message_id: str,
) -> str:
    """Render notification HTML for the orchestrator."""

    renderer = NotificationRenderer(
        notification_data=notification_data,
        base_url=base_url,
        communication_uuid=communication_uuid,
        email_message_id=email_message_id,
    )
    return renderer.render()
