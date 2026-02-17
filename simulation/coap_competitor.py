import asyncio
import time
import random
import logging
from aiocoap import *
import aiocoap.resource as resource

# Configuration
HOST = "127.0.0.1"
PORT = 5683


# --- 1. THE STANDARD IOT SERVER (Receiver) ---
class IoTResource(resource.Resource):
    """
    A standard CoAP resource that accepts sensor data (PUT) 
    and returns an acknowledgment (2.04 Changed).
    """

    async def render_put(self, request):
        # We accept the data and say "OK" (2.04 Changed)
        # This is what a real IoT Hub does.
        return Message(code=CHANGED, payload=b"")


async def start_coap_server():
    """Starts a real local CoAP server."""
    root = resource.Site()
    root.add_resource(['sensors', 'temp'], IoTResource())

    # Create server context
    server_context = await Context.create_server_context(root, bind=(HOST, PORT))
    return server_context


# --- 2. THE HELPER TO MEASURE SIZE ---
def measure_packet_size(msg):
    """
    Accurately measures the byte size of a CoAP packet 
    by temporarily assigning a dummy ID.
    """
    # Create a clone/copy logic just for measurement
    # We assign a dummy MID because .encode() requires it
    msg.mid = 1234
    size = len(msg.encode())
    msg.mid = None  # Reset so the real sender can assign its own
    return size


# --- 3. THE STANDARD IOT CLIENT (Sender) ---
async def run_coap_standard_device(n_readings=20):
    print(f"\n[CoAP] Starting Full Stack Simulation (Server + Client)...")

    # A. Start the Server
    server = await start_coap_server()

    # B. Start the Client
    client = await Context.create_client_context()

    total_bytes = 0
    start_time = time.time()

    print(f"[CoAP] Sending {n_readings} readings to coap://{HOST}:{PORT}/sensors/temp")

    for i in range(n_readings):
        payload = f"TEMP:{20 + i}".encode('utf-8')

        # Standard Confirmable (CON) PUT request
        request = Message(code=PUT, payload=payload, uri=f"coap://{HOST}:{PORT}/sensors/temp")
        request.mtype = CON

        # 1. Measure Size (Before sending)
        packet_size = measure_packet_size(request)

        try:
            # 2. Real Transmission
            # This will actually go to the server, get processed, and get an ACK back.
            response = await client.request(request).response

            # If we are here, we got an ACK!
            # Total = Outgoing Packet + Incoming ACK (approx 4 bytes)
            total_bytes += packet_size + 4

        except Exception as e:
            print(f"    [CoAP] Error: {e}")
            total_bytes += packet_size  # We still paid the energy to send it

        # Simulation Speed (Fast forward)
        await asyncio.sleep(0.05)

    duration = time.time() - start_time
    print(f"[CoAP] Test Complete. Traffic: {total_bytes} bytes in {duration:.2f}s")

    # C. Teardown
    await server.shutdown()
    await client.shutdown()

    return total_bytes, n_readings