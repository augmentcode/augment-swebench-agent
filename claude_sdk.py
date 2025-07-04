import anyio
from claude_code_sdk import query, ClaudeCodeOptions, Message


async def main():
    messages: list[Message] = []

    async for message in query(
        prompt="Write a haiku about foo.py", options=ClaudeCodeOptions(max_turns=3)
    ):
        messages.append(message)

    print(messages)


anyio.run(main)
