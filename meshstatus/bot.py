import asyncio
import socketio

SOCKET_IP = "https://status.meshmonitors.io"
sio = socketio.AsyncClient()

token = None


class Bot:
    global token

    def __init__(self, **args):
        global SOCKET_IP
        if args.get("test"):
            SOCKET_IP = "http://server.localtest.me"
        self._listeners = {}
        self.sio = sio
        self.headers = {'Accept': 'text/plain',
                        'authorization': token,
                        'Content-Type': 'application/json;charset=utf-8'}

    def _get_sio(self):
        return self.sio

    async def main(self, new_token):
        await self.sio.connect(SOCKET_IP, namespaces=['/'], transports=['websocket'])
        await sio.emit('authentication', {'token': new_token})

        @sio.event
        def auth_err(data):
            print("Invalid Token")

        await sio.wait()

    def login(self, new_token):
        global token
        token = new_token
        self.http.set_token(token)
        asyncio.run(self.main(new_token))

        return self.sio

    def on(self, event, handler=None, namespace=None):
        namespace = namespace or '/'

        def set_handler(handler):
            if namespace not in self.sio.handlers:
                self.sio.handlers[namespace] = {}
            self.sio.handlers[namespace][event] = handler
            return handler

        if handler is None:
            return set_handler
        set_handler(handler)

    def event(self, *args):
        return self.on(args[0].__name__)(args[0])
