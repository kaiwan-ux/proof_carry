import asyncio,json
async def main():
    from agent_framework import InMemoryCheckpointStorage
    s=InMemoryCheckpointStorage(); print(json.dumps({'framework':'maf','checkpoint_storage':'InMemoryCheckpointStorage','available':True}))
asyncio.run(main())
