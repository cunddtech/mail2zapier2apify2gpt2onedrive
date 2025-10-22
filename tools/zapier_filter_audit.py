#!/usr/bin/env python3
"""
Zapier Filter Audit Script - Find "Does not start with EMAIL:" conditions

This script uses the Zapier API to:
1. Fetch all Zaps in your account
2. Analyze each Zap's steps
3. Identify Filter steps with "Does not start with EMAIL:" conditions
4. Generate a report of which Zaps need manual fixing

⚠️ LIMITATION: Zapier API does NOT allow editing Filter conditions!
   You must fix them manually in the Zapier UI after this audit.

Requirements:
- Zapier API Key (get from: https://zapier.com/app/settings/api)
- requests library: pip install requests

Usage:
    export ZAPIER_API_KEY="your-api-key-here"
    python zapier_filter_audit.py
"""

import os
import sys
import json
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class ZapFilterIssue:
    """Represents a Zap with filter condition issues"""
    zap_id: str
    zap_name: str
    zap_status: str
    step_number: int
    step_type: str
    filter_logic: Optional[str]
    has_does_not_start_with_email: bool
    issue_details: str
    fix_action: str


class ZapierFilterAuditor:
    """Audit Zapier Zaps for filter condition issues"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.zapier.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
        }
        self.issues: List[ZapFilterIssue] = []
    
    def fetch_all_zaps(self) -> List[Dict[str, Any]]:
        """Fetch all Zaps from Zapier account"""
        print("📡 Fetching all Zaps from Zapier API...")
        
        url = f"{self.base_url}/zaps"
        all_zaps = []
        
        while url:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                print(f"❌ Error fetching Zaps: {response.status_code}")
                print(f"Response: {response.text}")
                sys.exit(1)
            
            data = response.json()
            zaps = data.get("results", [])
            all_zaps.extend(zaps)
            
            # Pagination
            url = data.get("next")
        
        print(f"✅ Found {len(all_zaps)} Zaps\n")
        return all_zaps
    
    def fetch_zap_details(self, zap_id: str) -> Dict[str, Any]:
        """Fetch detailed information about a specific Zap"""
        url = f"{self.base_url}/zaps/{zap_id}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            print(f"⚠️  Warning: Could not fetch details for Zap {zap_id}")
            return {}
        
        return response.json()
    
    def analyze_filter_step(self, zap: Dict[str, Any], step: Dict[str, Any], step_num: int) -> Optional[ZapFilterIssue]:
        """
        Analyze a filter step for problematic conditions
        
        Note: Zapier API does NOT expose filter condition details!
        We can only detect that a Filter step exists, not its exact conditions.
        """
        zap_id = zap.get("id", "unknown")
        zap_name = zap.get("title", "Untitled Zap")
        zap_status = zap.get("state", "unknown")
        
        step_type = step.get("type", "unknown")
        
        # Check if this is a Filter step
        if step_type.lower() != "filter":
            return None
        
        # ⚠️ LIMITATION: Zapier API does NOT expose filter condition details!
        # We can only flag that this Zap HAS a filter step
        issue = ZapFilterIssue(
            zap_id=zap_id,
            zap_name=zap_name,
            zap_status=zap_status,
            step_number=step_num,
            step_type=step_type,
            filter_logic="UNKNOWN - API does not expose details",
            has_does_not_start_with_email=False,  # Cannot detect via API
            issue_details="Filter step found - Manual audit required",
            fix_action="Open Zap in UI → Check Filter step → Change 'Does not start with' to 'Does not contain'"
        )
        
        return issue
    
    def audit_all_zaps(self):
        """Audit all Zaps for filter issues"""
        print("🔍 Starting Zapier Filter Audit...\n")
        print("=" * 80)
        
        zaps = self.fetch_all_zaps()
        
        # Filter for specific Zaps (Outgoing, Rechnungen, etc.)
        relevant_zaps = [
            z for z in zaps
            if any(keyword in z.get("title", "").lower() for keyword in [
                "outgoing", "incoming", "rechnungen", "angebote", 
                "lieferscheine", "catch-all", "railway"
            ])
        ]
        
        print(f"🎯 Analyzing {len(relevant_zaps)} relevant Zaps (Outgoing/Incoming/etc.)\n")
        
        for zap in relevant_zaps:
            zap_id = zap.get("id")
            zap_name = zap.get("title", "Untitled")
            zap_status = zap.get("state", "unknown")
            
            print(f"📋 {zap_name}")
            print(f"   ID: {zap_id} | Status: {zap_status}")
            
            # Fetch detailed Zap structure
            details = self.fetch_zap_details(zap_id)
            steps = details.get("steps", [])
            
            if not steps:
                print(f"   ⚠️  No steps found (API limitation)\n")
                continue
            
            # Analyze each step
            has_filter = False
            for i, step in enumerate(steps, start=1):
                issue = self.analyze_filter_step(zap, step, i)
                if issue:
                    has_filter = True
                    self.issues.append(issue)
                    print(f"   ⚠️  Step {i}: Filter detected - MANUAL AUDIT REQUIRED")
            
            if has_filter:
                print(f"   🔧 Action: Open in UI and check Filter conditions\n")
            else:
                print(f"   ✅ No Filter step found\n")
        
        print("=" * 80)
    
    def generate_report(self) -> str:
        """Generate a detailed audit report"""
        report = []
        report.append("\n" + "=" * 80)
        report.append("📊 ZAPIER FILTER AUDIT REPORT")
        report.append("=" * 80)
        report.append("")
        
        if not self.issues:
            report.append("✅ No Filter steps found in relevant Zaps")
            report.append("")
            report.append("This could mean:")
            report.append("1. No Zaps have Filter steps (unlikely)")
            report.append("2. Zapier API does not expose Filter details (likely)")
            report.append("")
            report.append("⚠️ RECOMMENDATION: Manual audit still required!")
        else:
            report.append(f"⚠️  Found {len(self.issues)} Zaps with Filter steps")
            report.append("")
            report.append("🚨 CRITICAL: Zapier API does NOT expose Filter condition details!")
            report.append("   You MUST manually check each Zap in the Zapier UI.")
            report.append("")
            report.append("-" * 80)
            
            for i, issue in enumerate(self.issues, start=1):
                report.append(f"\n{i}. {issue.zap_name}")
                report.append(f"   Zap ID: {issue.zap_id}")
                report.append(f"   Status: {issue.zap_status}")
                report.append(f"   Filter Step: #{issue.step_number}")
                report.append(f"   Issue: {issue.issue_details}")
                report.append(f"   🔧 Fix: {issue.fix_action}")
                report.append("")
        
        report.append("-" * 80)
        report.append("\n📋 MANUAL AUDIT CHECKLIST:")
        report.append("")
        report.append("For EACH Zap with 'Outgoing' or 'Sent Items' in name:")
        report.append("  [ ] Open Zap in Zapier UI")
        report.append("  [ ] Find Filter step (usually Step 2)")
        report.append("  [ ] Look for condition: 'Subject | Does not start with | EMAIL:'")
        report.append("  [ ] Change to: 'Subject | Does not contain | EMAIL:'")
        report.append("  [ ] Test step (should show 'Filter would not have run')")
        report.append("  [ ] Publish Zap")
        report.append("")
        report.append("For INCOMING Zaps (Rechnungen, Angebote, etc.):")
        report.append("  [ ] Check if Filter has 'Does not start with EMAIL:'")
        report.append("  [ ] If YES: Change to 'Does not contain'")
        report.append("  [ ] If NO: Zap is OK")
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_report(self, filename: str = "zapier_filter_audit_report.txt"):
        """Save the report to a file"""
        report = self.generate_report()
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"\n💾 Report saved to: {filename}")
    
    def print_zap_list(self, zaps: List[Dict[str, Any]]):
        """Print a formatted list of all Zaps"""
        print("\n📋 ALL ZAPS IN YOUR ACCOUNT:")
        print("=" * 80)
        
        for i, zap in enumerate(zaps, start=1):
            zap_id = zap.get("id", "unknown")
            title = zap.get("title", "Untitled Zap")
            status = zap.get("state", "unknown")
            url = zap.get("url", "")
            
            # Emoji for status
            status_emoji = "✅" if status == "on" else "⏸️"
            
            print(f"{i}. {status_emoji} {title}")
            print(f"   ID: {zap_id} | Status: {status}")
            print(f"   URL: {url}")
            print()
        
        print("=" * 80)


def main():
    """Main function"""
    print("🔧 ZAPIER FILTER AUDIT TOOL")
    print("=" * 80)
    print()
    
    # Get API key from environment
    api_key = os.getenv("ZAPIER_API_KEY")
    
    if not api_key:
        print("❌ Error: ZAPIER_API_KEY environment variable not set!")
        print()
        print("To get your API key:")
        print("1. Go to: https://zapier.com/app/settings/api")
        print("2. Click 'Generate API Key'")
        print("3. Export it:")
        print("   export ZAPIER_API_KEY='your-key-here'")
        print()
        sys.exit(1)
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-10:]}")
    print()
    
    # Create auditor
    auditor = ZapierFilterAuditor(api_key)
    
    # Fetch all Zaps first (to show the list)
    all_zaps = auditor.fetch_all_zaps()
    auditor.print_zap_list(all_zaps)
    
    # Perform audit
    auditor.audit_all_zaps()
    
    # Generate and print report
    report = auditor.generate_report()
    print(report)
    
    # Save report to file
    auditor.save_report()
    
    # Save JSON data for further analysis
    json_filename = "zapier_filter_audit_data.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump([asdict(issue) for issue in auditor.issues], f, indent=2)
    
    print(f"💾 JSON data saved to: {json_filename}")
    print()
    print("🎯 NEXT STEPS:")
    print("1. Review the report above")
    print("2. Open each Zap with Filter steps in Zapier UI")
    print("3. Check for 'Does not start with EMAIL:' conditions")
    print("4. Change to 'Does not contain EMAIL:'")
    print("5. Test & Publish")
    print()


if __name__ == "__main__":
    main()
