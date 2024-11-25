import asyncio

import chainlit as cl

from app.agent.browser_agent import agent_executor


@cl.on_chat_start
async def quey_llm():


    cl.user_session.set("agent_executor", agent_executor)

    await cl.Message("I'm an autonomous agent bot to help with USER queries").send()


@cl.on_message
async def query_llm(message: cl.Message):
    agent_executor = cl.user_session.get("agent_executor")

    response = agent_executor.ainvoke( {"input": message.content})

    # print("Chainlit response :", response)
    await cl.Message(response['output']).send()