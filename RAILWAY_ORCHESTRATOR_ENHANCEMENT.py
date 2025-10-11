# 🚀 Railway Orchestrator Extension - Zapier Notification Integration

# ADD THIS TO YOUR production_langgraph_orchestrator.py

import requests
from typing import Dict, Any

# Configuration
ZAPIER_NOTIFICATION_WEBHOOK = "https://hooks.zapier.com/hooks/catch/17762912/2xh8rlk/"

async def send_final_notification(processing_result: Dict[str, Any], original_request: Dict[str, Any]) -> bool:
    """
    Send final notification to Zapier after successful AI processing
    ADD THIS FUNCTION to production_langgraph_orchestrator.py
    """
    
    try:
        # Build notification payload
        notification_payload = {
            "notification_id": f"notif_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "source": original_request.get("source", "railway_orchestrator"),
            "processing_status": "success" if processing_result.get("success") else "error",
            
            # Customer Information
            "customer_info": {
                "name": original_request.get("customer_name", original_request.get("from", "")),
                "phone": original_request.get("from", ""),
                "scenario_type": original_request.get("scenario_type", ""),
                "anliegen": original_request.get("anliegen", original_request.get("ai_summary", ""))
            },
            
            # Processing Results
            "processing_info": {
                "workflow_path": processing_result.get("workflow_path", ""),
                "tasks_generated": len(processing_result.get("tasks_generated", [])),
                "contact_found": processing_result.get("contact_match", {}).get("found", False),
                "crm_updated": True
            },
            
            # Primary Task (for email template)
            "primary_task": {},
            
            # Contact Details
            "contact_details": {
                "contact_id": processing_result.get("contact_match", {}).get("contact_id"),
                "contact_name": processing_result.get("contact_match", {}).get("contact_name", ""),
                "company": processing_result.get("contact_match", {}).get("company", ""),
                "confidence": processing_result.get("contact_match", {}).get("confidence", 0.0)
            }
        }
        
        # Add primary task details if available
        tasks = processing_result.get("tasks_generated", [])
        if tasks:
            primary_task = tasks[0]
            notification_payload["primary_task"] = {
                "title": primary_task.get("title", ""),
                "description": primary_task.get("description", ""),
                "assigned_to": primary_task.get("assigned_to", ""),
                "priority": primary_task.get("priority", "medium"),
                "due_date": primary_task.get("due_date", "")
            }
        
        # Send to Zapier
        response = requests.post(
            ZAPIER_NOTIFICATION_WEBHOOK,
            json=notification_payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "C&D-Railway-Orchestrator/1.0"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"✅ Final notification sent successfully: {response.json()}")
            return True
        else:
            logger.warning(f"⚠️ Notification failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Notification error: {str(e)}")
        return False


# MODIFY YOUR EXISTING ENDPOINTS:

@app.post("/webhook/ai-call")
async def process_call(request: Request):
    """Process incoming call via webhook - ENHANCED with notification"""
    
    try:
        data = await request.json()
        
        result = await orchestrator.process_communication(
            message_type="call",
            from_contact=data.get("from", data.get("caller", "")),
            content=data.get("transcription", f"Anruf erhalten - Dauer: {data.get('duration', 0)}s"),
            additional_data=data
        )
        
        # NEW: Send final notification
        notification_sent = await send_final_notification(result, data)
        
        # Add notification status to response
        result["final_notification"] = {
            "sent": notification_sent,
            "webhook_url": ZAPIER_NOTIFICATION_WEBHOOK,
            "timestamp": datetime.now().isoformat()
        }
        
        return {"ai_processing": result}
        
    except Exception as e:
        logger.error(f"Call processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/ai-email")
async def process_email(request: Request):
    """Process incoming email via webhook - ENHANCED with notification"""
    
    try:
        data = await request.json()
        
        result = await orchestrator.process_communication(
            message_type="email",
            from_contact=data.get("from", ""),
            content=data.get("content", data.get("subject", "")),
            additional_data=data
        )
        
        # NEW: Send final notification
        notification_sent = await send_final_notification(result, data)
        
        # Add notification status to response
        result["final_notification"] = {
            "sent": notification_sent,
            "webhook_url": ZAPIER_NOTIFICATION_WEBHOOK,
            "timestamp": datetime.now().isoformat()
        }
        
        return {"ai_processing": result}
        
    except Exception as e:
        logger.error(f"Email processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/ai-whatsapp")
async def process_whatsapp(request: Request):
    """Process incoming WhatsApp message via webhook - ENHANCED with notification"""
    
    try:
        data = await request.json()
        
        result = await orchestrator.process_communication(
            message_type="whatsapp",
            from_contact=data.get("from", ""),
            content=data.get("message", data.get("content", "")),
            additional_data=data
        )
        
        # NEW: Send final notification
        notification_sent = await send_final_notification(result, data)
        
        # Add notification status to response
        result["final_notification"] = {
            "sent": notification_sent,
            "webhook_url": ZAPIER_NOTIFICATION_WEBHOOK,
            "timestamp": datetime.now().isoformat()
        }
        
        return {"ai_processing": result}
        
    except Exception as e:
        logger.error(f"WhatsApp processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))