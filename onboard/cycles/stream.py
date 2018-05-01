import asyncio
import copy
from datetime import timedelta
import json
import websockets

def websocket_server(calc, ws_host, ws_port, send_every=None):
    """Run the websocket server in it's own thread for sanity"""

    send_every = send_every if send_every is not None else timedelta(seconds=0.5)

    ws_clients = set()
    async def telemetry_server(websocket, path):
        """Websocket server handler, called on ws connection"""

        ws_clients.add(websocket)

        while True:
            try:
                telem = json_telemetry(calc.stats())
                await asyncio.wait([websocket.send(telem)])
                await asyncio.sleep(send_every.total_seconds())
            except:
                ws_clients.remove(websocket)
                break

    # Setup the event-loop (creating a new one for this thread)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_ws = websockets.serve(telemetry_server, ws_host, ws_port)
    loop.run_until_complete(start_ws)

    loop.run_forever()
    loop.close()


def json_telemetry(stats):
    # TODO: Pretty sure python is pass-by-value.. test it
    telemetry = copy.copy(stats)

    telemetry['pace'] = telemetry['pace'].total_seconds()

    return json.dumps({'telemetry': telemetry})

