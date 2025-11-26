import asyncio
import websockets
import json

NODE_A_URI = "ws://nodo-a:8081"
NODE_C_HOST = "0.0.0.0"
NODE_C_PORT = 8083

async def send_to_node_a(message):
    while True:
        try:
            async with websockets.connect(NODE_A_URI) as websocket:
                print("Connection to Node A established.")
                await websocket.send(json.dumps(message))
                print(f"Sent to Node A: {message}")
                return
        except (OSError, websockets.exceptions.ConnectionClosed) as e:
            print(f"Connection to Node A failed: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)

async def start_node_c_server(websocket, path=None):
    if path is None:
        print("Node B connected to Node C.")
    else:
        print(f"Node B connected to Node C. Path: {path}")
    async for message_str in websocket:
        message = json.loads(message_str)
        print(f"Received from Node B: {message}")
        
        message["power_level"] -= 5
        message["audit_trail"].append("C_verified")
        
        await send_to_node_a(message)

async def main():
    server = await websockets.serve(start_node_c_server, NODE_C_HOST, NODE_C_PORT)
    print(f"Node C WebSocket Server listening on ws://{NODE_C_HOST}:{NODE_C_PORT}")
    await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
