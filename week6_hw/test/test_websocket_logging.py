#!/usr/bin/env python3
"""
测试WebSocket日志功能
通过WebSocket连接触发代码生成和执行日志
"""
import asyncio
import websockets
import json
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_websocket_logging():
    """测试WebSocket日志功能"""
    print("🔌 Testing WebSocket Logging")
    print("=" * 50)
    
    try:
        # 连接到WebSocket
        uri = "ws://localhost:8000/ws/chat"
        print(f"1. Connecting to WebSocket: {uri}")
        
        async with websockets.connect(uri) as websocket:
            print("   ✅ WebSocket connected")
            
            # 发送测试消息
            test_message = {
                "type": "text",
                "content": "分析产品销量数据"
            }
            
            print("2. Sending test message...")
            await websocket.send(json.dumps(test_message))
            print("   ✅ Message sent")
            
            # 接收响应
            print("3. Receiving responses...")
            response_count = 0
            while response_count < 10:  # 限制响应数量
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    data = json.loads(response)
                    response_count += 1
                    
                    print(f"   📨 Response {response_count}: {data.get('type', 'unknown')}")
                    
                    if data.get('type') == 'analysis_complete':
                        print("   ✅ Analysis completed successfully")
                        break
                    elif data.get('type') == 'error':
                        print(f"   ❌ Error: {data.get('content', 'Unknown error')}")
                        break
                        
                except asyncio.TimeoutError:
                    print("   ⏰ Timeout waiting for response")
                    break
                except Exception as e:
                    print(f"   ❌ Error receiving response: {e}")
                    break
            
            print("4. WebSocket test completed")
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_websocket_logging())
    if success:
        print("\\n✅ WebSocket logging test completed!")
    else:
        print("\\n❌ WebSocket logging test failed!")
        sys.exit(1)
