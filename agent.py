import os
from dotenv import load_dotenv
from datetime import datetime

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.tools import DuckDuckGoSearchRun

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool

# =========================
# LOAD ENV
# =========================

load_dotenv()

# =========================
# LLM
# =========================

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3
)

# =========================
# RAG SETUP
# =========================

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_db = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)

retriever = vector_db.as_retriever(search_kwargs={"k": 5})

print("Chroma DB Loaded Successfully")

# =========================
# AGENT TOOLS
# =========================

search_tool = DuckDuckGoSearchRun()

@tool
def get_current_datetime():
    """Returns current date and time"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# =========================
# MEMORY
# =========================

memory = MemorySaver()

agent = create_react_agent(
    model=llm,
    tools=[search_tool, get_current_datetime],
    checkpointer=memory
)

config = {
    "configurable": {
        "thread_id": "user-1"
    }
}

# =========================
# DOMAIN GUARD
# =========================

SYSTEM_RULE = """
You are MyPropertyFact AI Assistant (https://mypropertyfact.in).

RULES:
- Only answer real estate related questions (buy, sell, rent, investment)
- If outside domain, politely refuse
- DO NOT say:
  "Based on the information provided"
  "According to context"
  "As an AI language model"

- Give direct, human-like answers
- Be concise and practical
"""

# =========================
# CHAT SYSTEM (RAG + AGENT ROUTER)
# =========================

def chat():
    while True:
        query = input("\nAsk Question: ")

        if query.lower() == "exit":
            print("Chat ended!")
            break

        # =========================
        # STEP 1: RAG SEARCH
        # =========================
        docs = retriever.invoke(query)
        context = "\n\n".join([d.page_content for d in docs]).strip()

        print("\n=========================")

        # =========================
        # MODE SELECTION
        # =========================
        if context and len(context) > 50:
            print("🔵 MODE: RAG USED")

            prompt = f"""
{SYSTEM_RULE}

Use ONLY the context below.

Context:
{context}

Question:
{query}

IMPORTANT:
- Answer directly
- Do NOT mention context or phrases like "based on"
"""

            response = llm.invoke(prompt)
            answer = response.content

        else:
            print("🟢 MODE: AGENT USED")

            response = agent.invoke(
                {
                    "messages": [
                        ("human", f"{SYSTEM_RULE}\n\n{query}")
                    ]
                },
                config=config
            )

            answer = response["messages"][-1].content

        # =========================
        # OUTPUT
        # =========================
        print("\nAI RESPONSE:\n")
        print(answer)
        print("\n=========================\n")


# =========================
# RUN
# =========================

chat()