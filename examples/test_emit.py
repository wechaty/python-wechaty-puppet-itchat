from pyee import AsyncIOEventEmitter, EventEmitter  # type: ignore
import asyncio
import types


async def on_test(data):
    print(data)
    print('on testing ...')


class TestCase:
    def __init__(self) -> None:
        self.event_stream = AsyncIOEventEmitter()

    def on(self, event_name: str, caller):
        # self.event_stream[event_name] = caller
        self.event_stream.on(event_name, caller)

    def emit(self, event_name, data):
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(
        #    self.event_stream[event_name](data)
        # )
        self.event_stream.emit(event_name, data)

    def say(self):
        print('say ...')


def run():
    case = TestCase()

    def say(self):
        print('say1 ...')

    case.say = types.MethodType(say, TestCase)

    case.on('test', on_test)
    case.emit('test', {"a": 1})

    case.say()


async def main():
    run()


asyncio.run(main())
