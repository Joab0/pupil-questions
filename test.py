import asyncio

from rich import print

from src.services.questions import generate_questions


async def main():
    print(await generate_questions(topic="Equipamentos rede de computadores", count=2))


asyncio.run(main())
