import asyncio


async def a():
    i = 0
    while i < 10:
        i = i + 1
        print(f"A: {i}")
        await asyncio.sleep(1.5)


async def b():
    ii = 0
    while ii < 10:
        ii = ii + 1
        print(f"b: {ii}")
        await asyncio.sleep(1)


async def main():
    # await (a())
    await asyncio.gather(a(), b())


asyncio.run(main())
