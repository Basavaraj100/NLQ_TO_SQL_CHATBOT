from langchain_openai import ChatOpenAI

def get_llm_model() -> ChatOpenAI:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    return llm
