# 🚀 Railway Orchestrator - Final Notification Extension

import requests
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
ZAPIER_NOTIFICATION_WEBHOOK = os.environ.get(
    'ZAPIER_NOTIFICATION_WEBHOOK', 
    'https://hooks.zapier.com/hooks/catch/17762912/2xh8rlk/'
)
NOTIFICATION_ENABLED = os.environ.get('NOTIFICATION_ENABLED', 'true').lower() == 'true'

class FinalNotificationHandler:
    """
    C&D Technologies Lead Management - Final Notification Handler
    Sendet finale Benachrichtigungen nach erfolgreicher Task-Generierung
    """
    
    def __init__(self):
        self.webhook_url = ZAPIER_NOTIFICATION_WEBHOOK
        self.enabled = NOTIFICATION_ENABLED
        
    def build_notification_payload(self, processing_result: Dict[str, Any], 
                                  original_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Erstellt Notification Payload basierend auf Railway Processing Result
        """
        
        ai_processing = processing_result.get("ai_processing", {})
        tasks_generated = ai_processing.get("tasks_generated", [])
        contact_match = ai_processing.get("contact_match", {})
        workflow_path = ai_processing.get("workflow_path", "")
        
        # Extract source information
        source = original_request.get("source", "unknown")
        scenario_type = original_request.get("scenario_type", "")
        customer_name = original_request.get("customer_name", "")
        customer_phone = original_request.get("from", "")
        anliegen = original_request.get("anliegen", original_request.get("ai_summary", ""))
        
        # Build comprehensive notification
        notification = {
            # Metadata
            "notification_id": f"notif_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "processing_status": "success" if ai_processing.get("success") else "error",
            
            # Customer Information
            "customer_info": {
                "name": customer_name,
                "phone": customer_phone,
                "scenario_type": scenario_type,
                "anliegen": anliegen
            },
            
            # Processing Results
            "processing_info": {
                "workflow_path": workflow_path,
                "tasks_generated": len(tasks_generated),
                "contact_found": contact_match.get("found", False),
                "crm_updated": True
            },
            
            # Primary Task (for email template)
            "primary_task": {},
            
            # Contact Details
            "contact_details": {
                "contact_id": contact_match.get("contact_id"),
                "contact_name": contact_match.get("contact_name", customer_name),
                "company": contact_match.get("company", ""),
                "confidence": contact_match.get("confidence", 0.0)
            }
        }
        
        # Add primary task details if available
        if tasks_generated:
            primary_task = tasks_generated[0]
            notification["primary_task"] = {
                "title": primary_task.get("title", ""),
                "description": primary_task.get("description", ""),
                "assigned_to": primary_task.get("assigned_to", ""),
                "priority": primary_task.get("priority", "medium"),
                "due_date": primary_task.get("due_date", ""),
                "task_type": primary_task.get("task_type", "")
            }
            
        # Add scenario-specific information
        if scenario_type:
            notification["scenario_info"] = {
                "type": scenario_type,
                "priority_mapping": self._get_scenario_priority(scenario_type),
                "department": self._get_scenario_department(scenario_type)
            }
            
        return notification
    
    def _get_scenario_priority(self, scenario_type: str) -> str:
        """Mapping von Frontdesk Szenarien zu Prioritäten"""
        priority_mapping = {
            "Angebotsanfrage": "high",
            "Beratung": "medium", 
            "Reklamation": "urgent",
            "Sonstiges": "low"
        }
        return priority_mapping.get(scenario_type, "medium")
    
    def _get_scenario_department(self, scenario_type: str) -> str:
        """Mapping von Frontdesk Szenarien zu Abteilungen"""
        department_mapping = {
            "Angebotsanfrage": "sales_team",
            "Beratung": "service_team",
            "Reklamation": "service_lead", 
            "Sonstiges": "customer_service"
        }
        return department_mapping.get(scenario_type, "sales_team")
    
    def send_notification(self, notification_payload: Dict[str, Any]) -> bool:
        """
        Sendet finale Benachrichtigung an Zapier Webhook
        """
        
        if not self.enabled:
            print("ℹ️ Notification disabled via environment variable")
            return False
            
        if not self.webhook_url:
            print("⚠️ No Zapier webhook URL configured")
            return False
            
        try:
            print(f"📧 Sending final notification to Zapier...")
            
            response = requests.post(
                self.webhook_url,
                json=notification_payload,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "C&D-Railway-Orchestrator/1.0",
                    "X-Notification-Type": "task_completion"
                },
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Notification sent successfully: {result.get('status', 'ok')}")
                return True
            else:
                print(f"⚠️ Notification failed: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            print("⏰ Notification timeout - continuing anyway")
            return False
        except Exception as e:
            print(f"❌ Notification error: {str(e)}")
            return False
    
    def process_and_notify(self, processing_result: Dict[str, Any], 
                          original_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method: Process result and send notification
        """
        
        # Build notification payload
        notification_payload = self.build_notification_payload(
            processing_result, 
            original_request
        )
        
        # Send notification
        notification_sent = self.send_notification(notification_payload)
        
        # Add notification status to processing result
        processing_result["final_notification"] = {
            "sent": notification_sent,
            "webhook_url": self.webhook_url,
            "timestamp": datetime.now().isoformat(),
            "payload_size": len(json.dumps(notification_payload))
        }
        
        return processing_result

# Global instance
notification_handler = FinalNotificationHandler()

def enhance_orchestrator_response(processing_result: Dict[str, Any], 
                                original_request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main function to be called after task generation
    
    Usage in Railway Orchestrator:
    
    # After successful AI processing and task generation:
    enhanced_result = enhance_orchestrator_response(result, original_request)
    return enhanced_result
    """
    
    return notification_handler.process_and_notify(processing_result, original_request)

# Environment Variables for Railway:
"""
Required Environment Variables:

ZAPIER_NOTIFICATION_WEBHOOK=https://hooks.zapier.com/hooks/catch/17762912/2xh8rlk/
NOTIFICATION_ENABLED=true

Optional:
NOTIFICATION_TIMEOUT=15
NOTIFICATION_RETRY_COUNT=3
"""

# Integration Example:
"""
# In your existing Railway orchestrator endpoint:

@app.post("/webhook/ai-call")
async def process_call(request_data: dict):
    
    # Existing processing...
    result = await process_ai_call(request_data)
    
    # NEW: Add final notification
    enhanced_result = enhance_orchestrator_response(result, request_data)
    
    return enhanced_result
"""