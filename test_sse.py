#!/usr/bin/env python3
"""
Test MCP SSE connection like Archestra would
"""

import asyncio
import httpx
import json
from datetime import datetime


async def test_sse_connection():
    """Test SSE connection to MCP server"""
    url = "http://localhost:9001/sse"
    
    print(f"🔗 Connecting to {url}")
    print()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        async with client.stream("GET", url, headers={"Accept": "text/event-stream"}) as response:
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            print()
            print("📡 Listening for events...")
            print()
            
            async for line in response.aiter_lines():
                if line:
                    print(f"  {datetime.now().strftime('%H:%M:%S')} | {line}")
                    
                    # If we get some data, that's good enough for the test
                    if line.startswith("data:") or line.startswith("event:"):
                        print()
                        print("✅ Server is sending SSE events!")
                        break


if __name__ == "__main__":
    try:
        asyncio.run(test_sse_connection())
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
