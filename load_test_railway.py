#!/usr/bin/env python3
"""
🧪 Railway Production Load Testing
===================================

Tests concurrent requests to validate:
- Performance under load
- Response times
- Error rates
- Concurrent processing
"""

import asyncio
import aiohttp
import time
from datetime import datetime
import json

BASE_URL = "https://my-langgraph-agent-production.up.railway.app"

# Test payloads
TEST_EMAILS = [
    {
        "sender": f"test{i}@example.com",
        "sender_name": f"Test User {i}",
        "subject": f"Load Test Email {i}",
        "body": f"This is load test email number {i}. Testing concurrent processing.",
        "received_at": datetime.utcnow().isoformat() + "Z"
    }
    for i in range(10)
]

TEST_CALLS = [
    {
        "event": "newCall",
        "from": f"+491511234567{i}",
        "to": "+49301234567",
        "callId": f"load-test-{i}-{int(time.time())}",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    for i in range(10)
]


async def send_request(session, url, payload, request_id):
    """Send single request and measure time"""
    start_time = time.time()
    
    try:
        async with session.post(url, json=payload) as response:
            duration = time.time() - start_time
            status = response.status
            
            if status == 200:
                data = await response.json()
                success = data.get("ai_processing", {}).get("success", False)
                return {
                    "request_id": request_id,
                    "status": status,
                    "success": success,
                    "duration": duration,
                    "error": None
                }
            else:
                return {
                    "request_id": request_id,
                    "status": status,
                    "success": False,
                    "duration": duration,
                    "error": f"HTTP {status}"
                }
    except Exception as e:
        duration = time.time() - start_time
        return {
            "request_id": request_id,
            "status": 0,
            "success": False,
            "duration": duration,
            "error": str(e)
        }


async def load_test_email(concurrent_requests=5):
    """Load test email endpoint"""
    print(f"\n📧 LOAD TEST: Email Endpoint ({concurrent_requests} concurrent requests)")
    print("=" * 70)
    
    url = f"{BASE_URL}/webhook/ai-email"
    
    async with aiohttp.ClientSession() as session:
        tasks = [
            send_request(session, url, TEST_EMAILS[i % len(TEST_EMAILS)], i)
            for i in range(concurrent_requests)
        ]
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_duration = time.time() - start_time
        
        # Analyze results
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        avg_duration = sum(r["duration"] for r in results) / len(results)
        max_duration = max(r["duration"] for r in results)
        min_duration = min(r["duration"] for r in results)
        
        print(f"\n📊 Results:")
        print(f"   Total Requests: {len(results)}")
        print(f"   Successful: {successful} ({successful/len(results)*100:.1f}%)")
        print(f"   Failed: {failed}")
        print(f"   Total Time: {total_duration:.2f}s")
        print(f"   Avg Response Time: {avg_duration:.2f}s")
        print(f"   Min Response Time: {min_duration:.2f}s")
        print(f"   Max Response Time: {max_duration:.2f}s")
        print(f"   Requests/Second: {len(results)/total_duration:.2f}")
        
        # Show errors if any
        errors = [r for r in results if r["error"]]
        if errors:
            print(f"\n❌ Errors:")
            for err in errors[:5]:
                print(f"   Request {err['request_id']}: {err['error']}")
        
        return {
            "endpoint": "email",
            "total": len(results),
            "successful": successful,
            "failed": failed,
            "avg_duration": avg_duration,
            "total_duration": total_duration
        }


async def load_test_call(concurrent_requests=5):
    """Load test call endpoint"""
    print(f"\n📞 LOAD TEST: Call Endpoint ({concurrent_requests} concurrent requests)")
    print("=" * 70)
    
    url = f"{BASE_URL}/webhook/ai-call"
    
    async with aiohttp.ClientSession() as session:
        tasks = [
            send_request(session, url, TEST_CALLS[i % len(TEST_CALLS)], i)
            for i in range(concurrent_requests)
        ]
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_duration = time.time() - start_time
        
        # Analyze results
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        avg_duration = sum(r["duration"] for r in results) / len(results)
        max_duration = max(r["duration"] for r in results)
        min_duration = min(r["duration"] for r in results)
        
        print(f"\n📊 Results:")
        print(f"   Total Requests: {len(results)}")
        print(f"   Successful: {successful} ({successful/len(results)*100:.1f}%)")
        print(f"   Failed: {failed}")
        print(f"   Total Time: {total_duration:.2f}s")
        print(f"   Avg Response Time: {avg_duration:.2f}s")
        print(f"   Min Response Time: {min_duration:.2f}s")
        print(f"   Max Response Time: {max_duration:.2f}s")
        print(f"   Requests/Second: {len(results)/total_duration:.2f}")
        
        return {
            "endpoint": "call",
            "total": len(results),
            "successful": successful,
            "failed": failed,
            "avg_duration": avg_duration,
            "total_duration": total_duration
        }


async def main():
    """Run all load tests"""
    print("\n🚀 RAILWAY PRODUCTION LOAD TESTING")
    print("=" * 70)
    print(f"Target: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test scenarios
    scenarios = [
        ("Light Load", 5),
        ("Medium Load", 10),
        ("Heavy Load", 20),
    ]
    
    all_results = []
    
    for scenario_name, concurrent in scenarios:
        print(f"\n\n🔥 {scenario_name} Test ({concurrent} concurrent requests)")
        print("=" * 70)
        
        # Test email endpoint
        email_results = await load_test_email(concurrent)
        all_results.append(email_results)
        
        # Wait between tests
        await asyncio.sleep(3)
        
        # Test call endpoint
        call_results = await load_test_call(concurrent)
        all_results.append(call_results)
        
        # Wait before next scenario
        await asyncio.sleep(5)
    
    # Final summary
    print("\n\n📋 LOAD TEST SUMMARY")
    print("=" * 70)
    for result in all_results:
        print(f"\n{result['endpoint'].upper()} Endpoint:")
        print(f"   Total Requests: {result['total']}")
        print(f"   Success Rate: {result['successful']/result['total']*100:.1f}%")
        print(f"   Avg Response: {result['avg_duration']:.2f}s")
        print(f"   Total Duration: {result['total_duration']:.2f}s")
    
    print("\n✅ Load testing complete!")


if __name__ == "__main__":
    asyncio.run(main())
