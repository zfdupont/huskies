import mergeDataGA
import mergeDataIL
import mergeDataNY
import asyncio

async def main():
    print("writing files...")
    await asyncio.gather(
        mergeDataGA.merge(),
        mergeDataIL.merge(),
        mergeDataNY.merge()
    )
    print("done!")

if __name__ == '__main__':
    asyncio.run(main())