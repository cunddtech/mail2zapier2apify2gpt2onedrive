# Datei: modules/gpt/precheck_scan.py

from modules.gpt.prompts.scan_precheck_prompt import build_scan_precheck_prompt
from modules.gpt.run_gpt_prompt import run_gpt_prompt
from modules.utils.debug_log import debug_log

def precheck_scan_with_gpt(ocr_text: str) -> str:
    debug_log("💬 Starte Precheck-Analyse des OCR-Textes...")

    prompt = build_scan_precheck_prompt(ocr_text)

    response = run_gpt_prompt(prompt)

    debug_log("✅ Precheck-Analyse abgeschlossen.")

    return response