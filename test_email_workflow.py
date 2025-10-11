#!/usr/bin/env python3
"""
Test Email Processing Workflow
"""

import sys
import os
import json
import asyncio

# Setup path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from dotenv import load_dotenv
load_dotenv()

async def test_email_workflow():
    """Test the email processing workflow"""
    print("=" * 60)
    print("🧪 Testing Email Processing Workflow")
    print("=" * 60)
    
    # Load test input
    with open('/Users/cdtechgmbh/mail2zapier2apify2gpt2onedrive/test_email_input.json', 'r') as f:
        test_email = json.load(f)
    
    print(f"\n📧 Test Email:")
    print(f"   From: {test_email['from_email_address_name']} <{test_email['from_email_address_address']}>")
    print(f"   Subject: {test_email['subject']}")
    print(f"   Body: {test_email['body_content'][:50]}...")
    
    try:
        # Get Graph API tokens
        from modules.auth.get_graph_token_mail import get_graph_token_mail
        from modules.auth.get_graph_token_onedrive import get_graph_token_onedrive
        from modules.mail.process_email_workflow import process_email_workflow
        from modules.utils.debug_log import debug_log
        
        print("\n� Getting access tokens...")
        access_token_mail = await get_graph_token_mail()
        access_token_onedrive = await get_graph_token_onedrive()
        
        if not access_token_mail or not access_token_onedrive:
            print("❌ Failed to get access tokens")
            return False
        
        print("✅ Access tokens obtained")
        print("\n�🔄 Starting email processing...")
        
        # Process email with correct parameters
        context = {
            "input_data": test_email,
            "weclapp_data": None,
            "gpt_result": None,
            "zapier_webhook": os.getenv('EMAIL_RECEIVER_ZAPIER', 'zapier-weclapp@cdtechnologies.de')
        }
        
        public_link = "https://test-link.example.com"  # Mock public link for test
        
        result = await process_email_workflow(
            public_link=public_link,
            input_data=test_email,
            access_token_mail=access_token_mail,
            access_token_onedrive=access_token_onedrive,
            context=context
        )
        
        print("\n✅ Email processing completed!")
        print(f"\n📊 Results:")
        print(json.dumps(result, indent=2, default=str))
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during email processing: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    """Run the test"""
    try:
        success = asyncio.run(test_email_workflow())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
