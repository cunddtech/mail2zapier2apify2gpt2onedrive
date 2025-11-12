#!/usr/bin/env python3
"""
🧪 UUID ACTION SYSTEM TESTER

Testet das neue UUID-basierte Button/Action System:
1. Datenbank-Tabellen erstellt?
2. Button Registration funktioniert?
3. Button Info Lookup funktioniert?
4. Action Execution Logging funktioniert?
5. Workflow State Management funktioniert?
"""

import sys
import sqlite3
from datetime import datetime, timedelta

# Import modules
from modules.database.email_tracking_db import get_email_tracking_db, EmailTrackingDB


def print_section(title: str):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def test_database_schema():
    """Test 1: Sind alle 6 neuen Tabellen vorhanden?"""
    print_section("TEST 1: Database Schema Check")
    
    db = get_email_tracking_db()
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    # Check for new tables
    expected_tables = [
        'user_communications',
        'action_buttons',
        'action_history',
        'workflow_states',
        'task_queue',
        'trip_opportunity_links'
    ]
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    all_tables = [row[0] for row in cursor.fetchall()]
    
    print(f"📊 Gefundene Tabellen: {len(all_tables)}")
    
    results = {}
    for table in expected_tables:
        exists = table in all_tables
        results[table] = exists
        status = "✅" if exists else "❌"
        print(f"  {status} {table}")
    
    conn.close()
    
    all_good = all(results.values())
    print(f"\n{'✅ Schema Test PASSED' if all_good else '❌ Schema Test FAILED'}")
    return all_good


def test_button_registration():
    """Test 2: Button Registration funktioniert?"""
    print_section("TEST 2: Button Registration")
    
    db = get_email_tracking_db()
    
    # First, register a test email in processed_emails
    import uuid
    test_email_id = f"test-{int(datetime.now().timestamp())}@example.com"
    
    print(f"📧 Registering test email in processed_emails...")
    print(f"   Message ID: {test_email_id}")
    
    # Save email to processed_emails table
    db.save_email(
        message_id=test_email_id,
        user_email="test@cdtechnologies.de",
        from_address="sender@example.com",
        subject="Test Email",
        body="Test email body content",
        received_date=datetime.now().isoformat(),
        workflow_path="WEG_A",
        ai_analysis={"intent": "test", "urgency": "low"}
    )
    
    print("✅ Test email registered in processed_emails")
    
    # Register a test communication
    comm_uuid = str(uuid.uuid4())
    
    print(f"\n📧 Creating test communication...")
    print(f"   Communication UUID: {comm_uuid}")
    print(f"   Email Message ID: {test_email_id}")
    
    success = db.register_communication(
        communication_uuid=comm_uuid,
        email_message_id=test_email_id,
        notification_type="test_notification",
        sent_via="test",
        recipient_email="test@example.com",
        subject="Test Notification"
    )
    
    if not success:
        print("❌ Communication registration failed")
        return False
    
    print("✅ Communication registered")
    
    # Register test buttons
    button_uuid_1 = str(uuid.uuid4())
    button_uuid_2 = str(uuid.uuid4())
    
    print(f"\n🔘 Registering test buttons...")
    
    success1 = db.register_button(
        button_uuid=button_uuid_1,
        communication_uuid=comm_uuid,
        email_message_id=test_email_id,
        action_type="create_contact",
        action_label="Kontakt erstellen",
        action_config={"contact_data": {"name": "Test User"}},
        button_color="btn-success"
    )
    
    success2 = db.register_button(
        button_uuid=button_uuid_2,
        communication_uuid=comm_uuid,
        email_message_id=test_email_id,
        action_type="schedule_appointment",
        action_label="Termin vereinbaren",
        action_config={"appointment_type": "meeting"},
        button_color="btn-primary"
    )
    
    if not (success1 and success2):
        print("❌ Button registration failed")
        return False
    
    print(f"✅ Button 1 (create_contact): {button_uuid_1[:8]}...")
    print(f"✅ Button 2 (schedule_appointment): {button_uuid_2[:8]}...")
    
    # Verify buttons exist
    button_info_1 = db.get_button_info(button_uuid_1)
    button_info_2 = db.get_button_info(button_uuid_2)
    
    if not (button_info_1 and button_info_2):
        print("❌ Button lookup failed")
        return False
    
    print(f"\n✅ Button lookup successful")
    print(f"   Button 1 Type: {button_info_1['action_type']}")
    print(f"   Button 2 Type: {button_info_2['action_type']}")
    
    # Store for later tests
    test_button_registration.button_uuid = button_uuid_1
    test_button_registration.email_message_id = test_email_id
    
    print(f"\n✅ Registration Test PASSED")
    return True


def test_action_execution_logging():
    """Test 3: Action Execution Logging funktioniert?"""
    print_section("TEST 3: Action Execution Logging")
    
    if not hasattr(test_button_registration, 'button_uuid'):
        print("⚠️ Skipping (requires previous test)")
        return False
    
    db = get_email_tracking_db()
    button_uuid = test_button_registration.button_uuid
    
    print(f"🔘 Logging test execution for button: {button_uuid[:8]}...")
    
    # Log successful execution
    execution_uuid = db.log_action_execution(
        button_uuid=button_uuid,
        execution_status="success",
        execution_result='{"weclapp_party_id": "test-123"}',
        processing_time=0.42,
        side_effects={"weclapp_party_created": "test-123"},
        executed_by="test_user"
    )
    
    if not execution_uuid:
        print("❌ Execution logging failed")
        return False
    
    print(f"✅ Execution logged: {execution_uuid[:8]}...")
    
    # Get execution history
    history = db.get_execution_history(button_uuid=button_uuid)
    
    if not history or len(history) == 0:
        print("❌ Execution history empty")
        return False
    
    print(f"✅ Execution history retrieved: {len(history)} entries")
    print(f"   Latest Status: {history[0]['execution_status']}")
    print(f"   Action Type: {history[0]['action_type']}")
    
    print(f"\n✅ Execution Logging Test PASSED")
    return True


def test_workflow_management():
    """Test 4: Workflow State Management funktioniert?"""
    print_section("TEST 4: Workflow State Management")
    
    if not hasattr(test_button_registration, 'email_message_id'):
        print("⚠️ Skipping (requires previous test)")
        return False
    
    db = get_email_tracking_db()
    email_message_id = test_button_registration.email_message_id
    
    print(f"📊 Creating test workflow...")
    
    # Create workflow
    workflow_uuid = db.create_workflow(
        email_message_id=email_message_id,
        workflow_type="lead_qualification",
        initial_stage="new",
        workflow_data={"lead_source": "email", "priority": "high"}
    )
    
    if not workflow_uuid:
        print("❌ Workflow creation failed")
        return False
    
    print(f"✅ Workflow created: {workflow_uuid[:8]}...")
    
    # Update workflow state
    success = db.update_workflow_state(
        workflow_uuid=workflow_uuid,
        new_stage="contacted",
        status="active",
        workflow_data={"last_contact": datetime.now().isoformat()}
    )
    
    if not success:
        print("❌ Workflow update failed")
        return False
    
    print(f"✅ Workflow updated to stage: contacted")
    
    # Complete workflow
    success = db.update_workflow_state(
        workflow_uuid=workflow_uuid,
        status="completed"
    )
    
    if not success:
        print("❌ Workflow completion failed")
        return False
    
    print(f"✅ Workflow completed")
    
    print(f"\n✅ Workflow Management Test PASSED")
    return True


def test_task_queue():
    """Test 5: Task Queue funktioniert?"""
    print_section("TEST 5: Task Queue Management")
    
    db = get_email_tracking_db()
    
    print(f"📋 Queueing test tasks...")
    
    # Queue tasks with different priorities and times
    execute_after_now = datetime.now().isoformat()
    execute_after_future = (datetime.now() + timedelta(hours=1)).isoformat()
    
    task_uuid_1 = db.queue_task(
        task_type="send_followup",
        execute_after=execute_after_now,
        task_data={"recipient": "test@example.com"},
        priority=5
    )
    
    task_uuid_2 = db.queue_task(
        task_type="update_crm",
        execute_after=execute_after_future,
        task_data={"contact_id": "123"},
        priority=3
    )
    
    if not (task_uuid_1 and task_uuid_2):
        print("❌ Task queueing failed")
        return False
    
    print(f"✅ Task 1 (send_followup): {task_uuid_1[:8]}... [Priority 5, Execute Now]")
    print(f"✅ Task 2 (update_crm): {task_uuid_2[:8]}... [Priority 3, Execute +1h]")
    
    # Get pending tasks
    pending = db.get_pending_tasks(limit=10)
    
    if not pending or len(pending) == 0:
        print("❌ No pending tasks found")
        return False
    
    print(f"\n✅ Pending tasks retrieved: {len(pending)} tasks")
    for task in pending:
        print(f"   - {task['task_type']} (Priority {task['priority']}, Status: {task['status']})")
    
    # Update task status
    success = db.update_task_status(
        task_uuid=task_uuid_1,
        status="completed"
    )
    
    if not success:
        print("❌ Task status update failed")
        return False
    
    print(f"\n✅ Task status updated to: completed")
    
    print(f"\n✅ Task Queue Test PASSED")
    return True


def test_trip_opportunity_linking():
    """Test 6: Fahrtenbuch-Opportunity Linking funktioniert?"""
    print_section("TEST 6: Trip-Opportunity Linking")
    
    db = get_email_tracking_db()
    
    print(f"🚗 Linking test trip to opportunity...")
    
    link_uuid = db.link_trip_to_opportunity(
        trip_id="trip-12345",
        opportunity_id="opp-67890",
        link_type="manual",
        linked_by="test_user",
        metadata={"note": "Test linking"}
    )
    
    if not link_uuid:
        print("❌ Trip-Opportunity linking failed")
        return False
    
    print(f"✅ Link created: {link_uuid[:8]}...")
    print(f"   Trip ID: trip-12345")
    print(f"   Opportunity ID: opp-67890")
    print(f"   Link Type: manual")
    
    print(f"\n✅ Trip-Opportunity Linking Test PASSED")
    return True


def print_summary(results):
    """Print test summary"""
    print_section("🎯 TEST SUMMARY")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {test_name}")
    
    print(f"\n📊 Total: {total} tests, {passed} passed, {failed} failed")
    
    if failed == 0:
        print(f"\n🎉 ALL TESTS PASSED! UUID Action System fully functional! 🎉")
        return True
    else:
        print(f"\n⚠️ {failed} test(s) failed - review errors above")
        return False


def main():
    """Run all tests"""
    print("\n🧪 UUID ACTION SYSTEM TEST SUITE")
    print("="*80)
    print("Testing new database tables, button registration, and action handlers")
    print("="*80)
    
    results = {}
    
    try:
        results["Database Schema"] = test_database_schema()
        results["Button Registration"] = test_button_registration()
        results["Action Execution Logging"] = test_action_execution_logging()
        results["Workflow Management"] = test_workflow_management()
        results["Task Queue"] = test_task_queue()
        results["Trip-Opportunity Linking"] = test_trip_opportunity_linking()
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    all_passed = print_summary(results)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
