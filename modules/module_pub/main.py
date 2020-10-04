import asyncio
import zmq.asyncio
from zmq.asyncio import Context


class MessagePublisher:
    def __init__(self):
        ctx = Context.instance()
        self.socket = ctx.socket(zmq.PUB)
        url = "tcp://0.0.0.0:5555"
        self.socket.bind(url)
        print(f"Pub bound to: {url}")

    async def send_msg(self):
        # (project case) use local files
        i = 1
        while True:
            msg = str(i)
            print(f"Sending msg: {msg}")
            await self.socket.send(msg.encode('ascii'))  # (i.to_bytes(i.bit_length() + 7 // 8, 'big'))
            i += 1
            await asyncio.sleep(1)


if __name__ == '__main__':
    sender = MessagePublisher()
    asyncio.get_event_loop().run_until_complete(asyncio.wait([sender.send_msg()]))
