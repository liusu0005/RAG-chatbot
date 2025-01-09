from openai import AsyncOpenAI
import asyncio
from datetime import datetime

client = AsyncOpenAI()

# Construct the system prompt
system_prompt_template = """You are Bobby, a virtual assistant work in a hospital. 
Today is {today}. You will continuously ask questions to patients, getting information from the conversation, which finally help to get ASA classification.

...

<context>
{context}
</context>
"""

with open("doc_asa.txt") as in_file:
    context_content = in_file.read()

system_prompt = system_prompt_template.format(
    context=context_content, 
    today=datetime.today().strftime('%Y-%m-%d')
)

async def chat_func(history):

    result = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system_prompt}] + history,
        max_tokens=256,
        temperature=0.5,
        stream=True,
    )

    buffer = ""
    async for r in result:
        next_token = r.choices[0].delta.content
        if next_token:
            print(next_token, flush=True, end="")
            buffer += next_token

    print("\n", flush=True)

    return buffer

async def continous_chat():
    greeting = "Hi I am Bobby, the AI assistant tracking your daily health status. How are you feeling today?"
    history = [{"role": "system", "content": greeting}]
    print(greeting)
    # Loop to receive user input continously
    while(True):
        user_input = input("> ")
        if user_input == "exit":
            history.append({"role": "user", "content": "What is my ASA classification today, based on all the information you collected?"})
            bot_response = await chat_func(history)
            history.append({"role": "assistant", "content": bot_response})
            break

        history.append({"role": "user", "content": user_input})

        # notice every time we call the chat function
        # we pass all the history to the API
        bot_response = await chat_func(history)

        history.append({"role": "assistant", "content": bot_response})

asyncio.run(continous_chat())

