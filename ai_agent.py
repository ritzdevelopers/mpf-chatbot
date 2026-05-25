import os

from dotenv import load_dotenv

from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain_community.vectorstores import Chroma

from langchain_google_genai import ChatGoogleGenerativeAI



load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Create Embeddings 
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Load Chroma Db 
vector_db = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)

print("Chroma DB Loaded Successfully")

retriever = vector_db.as_retriever(
    search_kwargs={"k": 5}
)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3
)



def chat():
    while True:
        query = input("\nAsk Questions: ")

        if query.lower() == "exit":
            print("Chat ended!")
            break

        docs = retriever.invoke(query)

        context = "\n\n".join([
            doc.page_content
            for doc in docs
        ])

        prompt = f"""
        You are a helpful AI real estate assistant for MyPropertyFact.

        Answer ONLY from the provided context.

        If information is not available in context,
        say:
        "I could not find relevant property information."

        Context:
        {context}

        Question:
        {query}
        """

        response = llm.invoke(prompt)

        # OUTPUT
        print("\nAI Response:\n")
        print(response.content)