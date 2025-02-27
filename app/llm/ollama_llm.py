from langchain_ollama import ChatOllama
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

LLAMA_MODEL = OllamaLLM(model="llama3.2")
LLAMA_CHAT_MODEL = ChatOllama(
                model = "gemma2:9b",
                temperature = 0.5,
                num_predict = 256,
                # other params ...
            )


if __name__ == '__main__':
    template = """Question: {question}
    
    Answer: Let's think step by step."""

    prompt = ChatPromptTemplate.from_template(template)

    model = OllamaLLM(model="llama3.2")

    chain = prompt | model

    res = chain.invoke({"question": "Navigate to amazon.com and extract all text"})
    print(res)
