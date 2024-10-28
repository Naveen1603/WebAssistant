# This is a sample Python script.
from app.agent.browser_agent import agent_chain, agent_executor
import asyncio

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

def my_func():
    invoke = agent_executor.invoke({"input": "Navigate to amazon.com and search for Iphone 15 then click on the page results to extract device specifications and price"})
    # result = await agent_chain.arun("What are the headers on langchain.com?")
    print(invoke)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    my_func()
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(my_func())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
