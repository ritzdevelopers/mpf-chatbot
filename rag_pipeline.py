import json
import os

from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from langchain_google_genai import ChatGoogleGenerativeAI


# =========================
# LOAD ENV
# =========================

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


# =========================
# LOAD JSON DATA
# =========================

with open("data/property_data.json", "r", encoding="utf-8") as f:
    properties = json.load(f)

with open("data/cities.json", "r", encoding="utf-8") as f:
    cities = json.load(f)


# =========================
# CREATE DOCUMENTS
# =========================

documents = []


# CITY DOCUMENTS

for city in cities:

    metadata = {
        "type": "city",
        "metaTitle": city.get("metaTitle"),
        "metaKeywords": city.get("metaKeywords"),
        "metaDescription": city.get("metaDescription"),
        "cityName": city.get("cityName"),
        "stateName": city.get("stateName"),
        "countryName": city.get("countryName")
    }

    content = str(city.get("cityDescription", "")).strip()

    if not content:
        continue

    doc = Document(
        page_content=content,
        metadata=metadata
    )

    documents.append(doc)


# PROPERTY DOCUMENTS

extract_cols = [
    "metaTitle",
    "metaKeyword",
    "projectName",
    "projectLocality",
    "projectConfiguration",
    "state",
    "city",
    "country",
    "propertyTypeName"
]

for item in properties:

    metadata = {
        col: item.get(col)
        for col in extract_cols
    }

    metadata["type"] = "property"

    content = str(item.get("final_content", "")).strip()

    if not content:
        continue

    doc = Document(
        page_content=content,
        metadata=metadata
    )

    documents.append(doc)


print(f"Total Documents: {len(documents)}")

# =========================
# CHUNKING
# =========================

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = splitter.split_documents(documents)

print(f"Total Chunks: {len(chunks)}")


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# =========================
# CREATE VECTOR DB
# =========================

vector_db = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"
)

print("Vector DB Created Successfully")
