import asyncio
import websockets
import json
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer

NODE_B_URI = "ws://nodo-b:8082"
NODE_A_HOST = "0.0.0.0"
NODE_A_WS_PORT = 8081
NODE_A_HTTP_PORT = 8080

async def send_to_node_b(message):
    while True:
        try:
            async with websockets.connect(NODE_B_URI) as websocket:
                print(f"Connection to Node B established.")
                await websocket.send(json.dumps(message))
                print(f"Sent to Node B: {message}")
                return
        except (OSError, websockets.exceptions.ConnectionClosed) as e:
            print(f"Connection to Node B failed: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)

async def start_node_a_server(websocket, path=None):
    if path is None:
        print("WebSocket client connected to Node A.")
    else:
        print(f"WebSocket client connected to Node A. Path: {path}")
    message_str = await websocket.recv()
    message = json.loads(message_str)
    power_level = message.get("power_level", "N/A")
    print(f"CICLO COMPLETADO: {power_level}")
    print(f"Final message received: {message}")

class TriggerHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            power_level = int(post_data.decode('utf-8'))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Process initiated")
            
            message = {
                "_id": str(uuid.uuid4()),
                "power_level": power_level,
                "audit_trail": ["A_initiated"]
            }
            
            asyncio.run_coroutine_threadsafe(send_to_node_b(message), asyncio.get_event_loop())

        except ValueError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid power level. Please send an integer.")

def run_http_server(loop):
    asyncio.set_event_loop(loop)
    server_address = (NODE_A_HOST, NODE_A_HTTP_PORT)
    httpd = HTTPServer(server_address, TriggerHandler)
    print(f"Node A HTTP Trigger listening on http://{NODE_A_HOST}:{NODE_A_HTTP_PORT}")
    httpd.serve_forever()

async def main():
    # Start the WebSocket server
    ws_server = await websockets.serve(start_node_a_server, NODE_A_HOST, NODE_A_WS_PORT)
    print(f"Node A WebSocket Server listening on ws://{NODE_A_HOST}:{NODE_A_WS_PORT}")

    # Start the HTTP server in a separate thread
    loop = asyncio.get_running_loop()
    import threading
    http_thread = threading.Thread(target=run_http_server, args=(loop,))
    http_thread.daemon = True
    http_thread.start()

    await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
