import asyncio
import zmq.asyncio
from zmq.asyncio import Context


class MessageSubscriber:
    def __init__(self):
        ctx = Context.instance()
        self.socket = ctx.socket(zmq.SUB)
        url = "tcp://0.0.0.0:5555"
        self.socket.connect(url)
        self.socket.setsockopt(zmq.SUBSCRIBE, ''.encode('ascii'))  # any topic
        print(f"Sub connected to: {url}")

    async def receive_msg(self):
        # (project case) use local files
        while True:
            msg = await self.socket.recv()
            print(f"Received msg: {msg.decode('ascii')}")


if __name__ == '__main__':
    sender = MessageSubscriber()
    asyncio.get_event_loop().run_until_complete(asyncio.wait([sender.receive_msg()]))
