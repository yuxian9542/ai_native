#!/usr/bin/env python3
"""
调试WebSocket连接问题
"""
import asyncio
import websockets
import json
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


async def debug_websocket():
    """调试WebSocket连接"""
    print("🔍 Debugging WebSocket Connection")
    print("=" * 50)
    
    # 测试不同的WebSocket URL
    urls_to_test = [
        "ws://localhost:8000/ws/chat",
        "ws://127.0.0.1:8000/ws/chat",
        "ws://localhost:8000/ws/chat/",
    ]
    
    for url in urls_to_test:
        print(f"\n🔗 Testing URL: {url}")
        try:
            # 连接WebSocket（不使用timeout参数）
            async with websockets.connect(url) as websocket:
                print(f"   ✅ Connected successfully!")
                
                # 发送简单消息
                test_message = {"type": "text", "content": "test"}
                await websocket.send(json.dumps(test_message))
                print(f"   ✅ Message sent")
                
                # 尝试接收响应
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    print(f"   ✅ Response received: {response[:100]}...")
                    break  # 如果成功，跳出循环
                except asyncio.TimeoutError:
                    print(f"   ⏰ Timeout waiting for response")
                except Exception as e:
                    print(f"   ❌ Error receiving response: {e}")
                    
        except websockets.exceptions.InvalidURI as e:
            print(f"   ❌ Invalid URI: {e}")
        except websockets.exceptions.ConnectionClosed as e:
            print(f"   ❌ Connection closed: {e}")
        except asyncio.TimeoutError:
            print(f"   ⏰ Connection timeout")
        except Exception as e:
            print(f"   ❌ Connection error: {e}")
    
    # 测试HTTP端点
    print(f"\n🌐 Testing HTTP endpoints...")
    try:
        import requests
        response = requests.get("http://localhost:8000/")
        print(f"   ✅ Root endpoint: {response.status_code}")
        print(f"   📄 Response: {response.json()}")
        
        response = requests.get("http://localhost:8000/api/health")
        print(f"   ✅ Health endpoint: {response.status_code}")
        print(f"   📄 Response: {response.json()}")
        
    except Exception as e:
        print(f"   ❌ HTTP test failed: {e}")


if __name__ == "__main__":
    asyncio.run(debug_websocket())
