import asyncio
import socketio

SOCKET_IP = "https://api.status.meshmonitors.io"
sio = socketio.AsyncClient()

token = None
authErr = False

try:
    loop = asyncio.get_running_loop()
except RuntimeError:  # if cleanup: 'RuntimeError: There is no current event loop..'
    loop = None



class Bot:
    global token

    def __init__(self, **args):
        global SOCKET_IP
        if args.get("test"):
            SOCKET_IP = "http://localhost:3000"
        self._listeners = {}
        self.sio = sio
        self.headers = {'Accept': 'text/plain',
                        'authorization': token,
                        'Content-Type': 'application/json;charset=utf-8'}

    def _get_sio(self):
        return self.sio

    async def main(self, new_token):
        await self.sio.connect(SOCKET_IP, namespaces=['/'], transports=['websocket'])
        authErr = False
        print("Connecting to MeshStatus")
        await sio.emit("connection")
        await sio.emit('authentication', {'token': new_token})


        @sio.event
        async def auth_err(data):
            global authErr
            print(data)
            authErr = True
            await sio.disconnect()

        @sio.event
        async def alive_status(data):
            await sio.emit("alive_status_return", "alive")

        @sio.on('connected')
        async def on_connect(data):
            print("Connected to MeshStatus")

        @sio.event
        async def on_disconnect(data):
            if data == "transport close":
                print("Server has been restarted! Trying to reconnect")
            elif not authErr:
                print("Disconnected, trying to reconnect")
                await self.sio.connect(SOCKET_IP, namespaces=['/'], transports=['websocket'])
                await sio.emit('authentication', {'token': new_token})

        await sio.wait()

    async def login(self, new_token):
        global token
        token = new_token
        await self.main(new_token)
