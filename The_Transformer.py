import asyncio
import websockets
import json

NODE_C_URI = "ws://nodo-c:8083"
NODE_B_HOST = "0.0.0.0"
NODE_B_PORT = 8082

async def send_to_node_c(message):
    while True:
        try:
            async with websockets.connect(NODE_C_URI) as websocket:
                print("Connection to Node C established.")
                await websocket.send(json.dumps(message))
                print(f"Sent to Node C: {message}")
                return
        except (OSError, websockets.exceptions.ConnectionClosed) as e:
            print(f"Connection to Node C failed: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)

async def start_node_b_server(websocket, path=None):
    if path is None:
        print("Node A connected to Node B.")
    else:
        print(f"Node A connected to Node B. Path: {path}")
    async for message_str in websocket:
        message = json.loads(message_str)
        print(f"Received from Node A: {message}")
        
        power_level = message.get("power_level", 0)
        
        if power_level % 2 == 0:
            message["power_level"] *= 2
        else:
            message["power_level"] += 1
            
        message["audit_trail"].append("B_processed")
        
        await send_to_node_c(message)

async def main():
    server = await websockets.serve(start_node_b_server, NODE_B_HOST, NODE_B_PORT)
    print(f"Node B WebSocket Server listening on ws://{NODE_B_HOST}:{NODE_B_PORT}")
    await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
