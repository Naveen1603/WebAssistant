from langchain.agents import AgentType, initialize_agent, create_structured_chat_agent, AgentExecutor
from langchain_community.chat_models import ChatOpenAI

from app.llm.ollama_llm import LLAMA_MODEL, LLAMA_CHAT_MODEL
from app.playwright.tools import BrowserToolkit
from langchain import hub
# Get the prompt to use - you can modify this!
prompt = hub.pull("hwchase17/structured-chat-agent")
# from langchain_anthropic import ChatAnthropic
#
# llm = ChatAnthropic(
#     model_name="claude-3-haiku-20240307", temperature=0
# )
print(prompt)
toolkit = BrowserToolkit()

# llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-1106")

agent_chain = create_structured_chat_agent(
    LLAMA_CHAT_MODEL,
    toolkit.get_tools(),
    prompt
)

# Create an agent executor by passing in the agent and tools
agent_executor = AgentExecutor(
    agent=agent_chain, tools=toolkit.tools, verbose=True, handle_parsing_errors=True
)

