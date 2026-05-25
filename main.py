import os
from datetime import datetime
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

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
# FASTAPI
# =========================

app = FastAPI()

# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# LLM
# =========================

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3
)

# =========================
# EMBEDDINGS
# =========================

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# =========================
# CHROMA DB
# =========================

vector_db = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)

retriever = vector_db.as_retriever(
    search_kwargs={"k": 5}
)

print("✅ Chroma DB Loaded Successfully")

# =========================
# TOOLS
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
    tools=[
        search_tool,
        get_current_datetime
    ],
    checkpointer=memory
)

# =========================
# CUSTOM CHAT MEMORY
# =========================

chat_histories = {}

# =========================
# SYSTEM RULE
# =========================

SYSTEM_RULE = """
You are MyPropertyFact AI Assistant.

Website:
https://mypropertyfact.in

RULES:
- Only answer real estate related questions
- Help users with:
  property buying
  selling
  renting
  investment
  projects
  builders
  pricing
  locations
  real estate trends

- If user asks unrelated questions,
  politely refuse.

- NEVER say:
  "Based on the provided context"
  "According to the context"
  "As an AI language model"

- Talk naturally like a real property advisor.
- Understand previous conversation references.
- Keep answers concise and practical.
"""

# =========================
# REQUEST MODEL
# =========================

class ChatRequest(BaseModel):
    message: str
    user_id: str = "default-user"

# =========================
# HOME ROUTE
# =========================

@app.get("/api")
def home():
    return {
        "message": "MyPropertyFact AI Running"
    }

# =========================
# CHAT ROUTE
# =========================

@app.post("/chat")
def chat(req: ChatRequest):

    query = req.message
    user_id = req.user_id

    print("\n=========================")
    print(f"👤 USER: {query}")

    # =========================
    # USER MEMORY INIT
    # =========================

    if user_id not in chat_histories:
        chat_histories[user_id] = []

    # =========================
    # PREVIOUS CHAT HISTORY
    # =========================

    previous_conversation = "\n".join(
        chat_histories[user_id]
    )

    # =========================
    # ENHANCED QUERY
    # =========================

    enhanced_query = f"""
Previous Conversation:
{previous_conversation}

Current User Question:
{query}
"""

    # =========================
    # RAG SEARCH
    # =========================

    docs = retriever.invoke(enhanced_query)

    context = "\n\n".join([
        d.page_content
        for d in docs
    ]).strip()

    # =========================
    # RAG MODE
    # =========================

    if context and len(context) > 50:

        print("🔵 MODE: RAG USED")

        prompt = f"""
{SYSTEM_RULE}

Conversation History:
{previous_conversation}

Context:
{context}

Question:
{query}

IMPORTANT:
- Understand references from previous chat
- Answer directly
- Be conversational
- No robotic sentences
"""

        response = llm.invoke(prompt)

        answer = response.content

        # =========================
        # SAVE MEMORY
        # =========================

        chat_histories[user_id].append(
            f"User: {query}"
        )

        chat_histories[user_id].append(
            f"Assistant: {answer}"
        )

        # Keep last 10 entries
        chat_histories[user_id] = (
            chat_histories[user_id][-10:]
        )

        print("✅ RESPONSE GENERATED")

        return {
            "mode": "rag",
            "response": answer
        }

    # =========================
    # AGENT MODE
    # =========================

    else:

        print("🟢 MODE: AGENT USED")

        config = {
            "configurable": {
                "thread_id": user_id
            }
        }

        response = agent.invoke(
            {
                "messages": [
                    (
                        "human",
                        f"""
{SYSTEM_RULE}

Conversation History:
{previous_conversation}

Current User Question:
{query}

IMPORTANT:
- Understand previous references
- Stay inside real estate domain
- Use tools if needed
"""
                    )
                ]
            },
            config=config
        )

        answer = response["messages"][-1].content

        # =========================
        # SAVE MEMORY
        # =========================

        chat_histories[user_id].append(
            f"User: {query}"
        )

        chat_histories[user_id].append(
            f"Assistant: {answer}"
        )

        # Keep last 10 entries
        chat_histories[user_id] = (
            chat_histories[user_id][-10:]
        )

        print("✅ RESPONSE GENERATED")

        return {
            "mode": "agent",
            "response": answer
        }

# =========================
# STATIC FILES
# =========================

os.makedirs("static", exist_ok=True)

# =========================
# CREATE INDEX.HTML
# =========================

index_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>MyPropertyFact — Your Real Estate Intelligence</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700;900&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/style.css">
</head>
<body>

<!-- ========== HERO SECTION ========== -->
<header class="hero">

  <nav class="nav">
    <div class="nav-logo">
      <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
        <path d="M16 2L2 12V30H12V20H20V30H30V12L16 2Z" fill="#C9A84C" stroke="#C9A84C" stroke-width="1" stroke-linejoin="round"/>
        <rect x="13" y="20" width="6" height="10" fill="#0A1628"/>
      </svg>
      <span>MyPropertyFact</span>
    </div>
    <ul class="nav-links">
      <li><a href="#">Buy</a></li>
      <li><a href="#">Sell</a></li>
      <li><a href="#">Rent</a></li>
      <li><a href="#">Invest</a></li>
      <li><a href="https://mypropertyfact.in" target="_blank" class="nav-cta">Visit Site</a></li>
    </ul>
  </nav>

  <div class="hero-content">
    <div class="hero-text">
      <p class="hero-eyebrow">AI-Powered Property Intelligence</p>
      <h1 class="hero-title">Find Your<br/><em>Perfect Property</em><br/>With Confidence</h1>
      <p class="hero-sub">MyPropertyFact brings you verified real estate insights, live market trends, and an intelligent AI advisor — all in one place.</p>
      <div class="hero-actions">
        <button class="btn-primary" onclick="openChat()">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
          Ask AI Advisor
        </button>
        <a href="https://mypropertyfact.in" target="_blank" class="btn-secondary">Explore Properties →</a>
      </div>
      <div class="hero-stats">
        <div class="stat"><span class="stat-num">10K+</span><span class="stat-label">Properties Listed</span></div>
        <div class="stat-divider"></div>
        <div class="stat"><span class="stat-num">50+</span><span class="stat-label">Cities Covered</span></div>
        <div class="stat-divider"></div>
        <div class="stat"><span class="stat-num">98%</span><span class="stat-label">Client Satisfaction</span></div>
      </div>
    </div>

    <div class="hero-visual">
      <!-- Luxury Building SVG -->
      <svg class="svg-building" viewBox="0 0 340 420" fill="none" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="bldg" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#1a2f5a"/>
            <stop offset="100%" stop-color="#0d1b35"/>
          </linearGradient>
          <linearGradient id="gold" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#e8c96a"/>
            <stop offset="100%" stop-color="#b8932a"/>
          </linearGradient>
          <linearGradient id="glass" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#4a7fc1" stop-opacity="0.9"/>
            <stop offset="100%" stop-color="#1e4d8c" stop-opacity="0.6"/>
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="blur"/>
            <feComposite in="SourceGraphic" in2="blur" operator="over"/>
          </filter>
        </defs>
        <!-- Ground -->
        <rect x="0" y="390" width="340" height="30" fill="#0a1628"/>
        <rect x="20" y="388" width="300" height="4" fill="url(#gold)" rx="2"/>

        <!-- Main Tower -->
        <rect x="110" y="80" width="120" height="310" fill="url(#bldg)" rx="4"/>
        <!-- Tower accent lines -->
        <rect x="110" y="80" width="3" height="310" fill="url(#gold)" opacity="0.6"/>
        <rect x="227" y="80" width="3" height="310" fill="url(#gold)" opacity="0.6"/>

        <!-- Tower Top Spire -->
        <polygon points="170,10 155,80 185,80" fill="url(#gold)"/>
        <rect x="168" y="10" width="4" height="15" fill="url(#gold)"/>
        <!-- Spire glow -->
        <circle cx="170" cy="12" r="5" fill="#e8c96a" opacity="0.8" filter="url(#glow)"/>

        <!-- Tower Windows - Left column -->
        <rect x="122" y="100" width="20" height="28" fill="url(#glass)" rx="2"/>
        <rect x="122" y="140" width="20" height="28" fill="url(#glass)" rx="2"/>
        <rect x="122" y="180" width="20" height="28" fill="url(#glass)" rx="2"/>
        <rect x="122" y="220" width="20" height="28" fill="url(#glass)" rx="2"/>
        <rect x="122" y="260" width="20" height="28" fill="url(#glass)" rx="2"/>
        <rect x="122" y="300" width="20" height="28" fill="url(#glass)" rx="2"/>

        <!-- Tower Windows - Center column -->
        <rect x="150" y="100" width="40" height="28" fill="url(#glass)" rx="2" opacity="0.9"/>
        <rect x="150" y="140" width="40" height="28" fill="url(#glass)" rx="2"/>
        <rect x="150" y="180" width="40" height="28" fill="url(#glass)" rx="2" opacity="0.9"/>
        <rect x="150" y="220" width="40" height="28" fill="url(#glass)" rx="2"/>
        <rect x="150" y="260" width="40" height="28" fill="url(#glass)" rx="2" opacity="0.9"/>
        <rect x="150" y="300" width="40" height="28" fill="url(#glass)" rx="2"/>

        <!-- Tower Windows - Right column -->
        <rect x="198" y="100" width="20" height="28" fill="url(#glass)" rx="2"/>
        <rect x="198" y="140" width="20" height="28" fill="url(#glass)" rx="2" opacity="0.9"/>
        <rect x="198" y="180" width="20" height="28" fill="url(#glass)" rx="2"/>
        <rect x="198" y="220" width="20" height="28" fill="url(#glass)" rx="2" opacity="0.9"/>
        <rect x="198" y="260" width="20" height="28" fill="url(#glass)" rx="2"/>
        <rect x="198" y="300" width="20" height="28" fill="url(#glass)" rx="2" opacity="0.9"/>

        <!-- Left Wing Building -->
        <rect x="30" y="160" width="80" height="230" fill="#122040" rx="3"/>
        <rect x="30" y="160" width="2" height="230" fill="#C9A84C" opacity="0.4"/>
        <rect x="108" y="160" width="2" height="230" fill="#C9A84C" opacity="0.4"/>
        <!-- Left Wing Windows -->
        <rect x="40" y="175" width="16" height="22" fill="url(#glass)" rx="1" opacity="0.7"/>
        <rect x="62" y="175" width="16" height="22" fill="url(#glass)" rx="1" opacity="0.5"/>
        <rect x="84" y="175" width="16" height="22" fill="url(#glass)" rx="1" opacity="0.7"/>
        <rect x="40" y="210" width="16" height="22" fill="url(#glass)" rx="1" opacity="0.5"/>
        <rect x="62" y="210" width="16" height="22" fill="url(#glass)" rx="1" opacity="0.8"/>
        <rect x="84" y="210" width="16" height="22" fill="url(#glass)" rx="1" opacity="0.5"/>
        <rect x="40" y="245" width="16" height="22" fill="url(#glass)" rx="1" opacity="0.7"/>
        <rect x="62" y="245" width="16" height="22" fill="url(#glass)" rx="1" opacity="0.5"/>
        <rect x="84" y="245" width="16" height="22" fill="url(#glass)" rx="1" opacity="0.9"/>
        <rect x="40" y="280" width="16" height="22" fill="url(#glass)" rx="1" opacity="0.5"/>
        <rect x="62" y="280" width="16" height="22" fill="url(#glass)" rx="1" opacity="0.7"/>
        <rect x="84" y="280" width="16" height="22" fill="url(#glass)" rx="1" opacity="0.5"/>

        <!-- Right Wing Building -->
        <rect x="230" y="180" width="80" height="210" fill="#0f1c38" rx="3"/>
        <rect x="230" y="180" width="2" height="210" fill="#C9A84C" opacity="0.4"/>
        <rect x="308" y="180" width="2" height="210" fill="#C9A84C" opacity="0.4"/>
        <!-- Right Wing Windows -->
        <rect x="240" y="195" width="16" height="22" fill="url(#glass)" rx="1" opacity="0.6"/>
        <rect x="262" y="195" width="16" height="22" fill="url(#glass)" rx="1" opacity="0.8"/>
        <rect x="284" y="195" width="16" height="22" fill="url(#glass)" rx="1" opacity="0.5"/>
        <rect x="240" y="230" width="16" height="22" fill="url(#glass)" rx="1" opacity="0.8"/>
        <rect x="262" y="230" width="16" height="22" fill="url(#glass)" rx="1" opacity="0.5"/>
        <rect x="284" y="230" width="16" height="22" fill="url(#glass)" rx="1" opacity="0.7"/>
        <rect x="240" y="265" width="16" height="22" fill="url(#glass)" rx="1" opacity="0.5"/>
        <rect x="262" y="265" width="16" height="22" fill="url(#glass)" rx="1" opacity="0.7"/>
        <rect x="284" y="265" width="16" height="22" fill="url(#glass)" rx="1" opacity="0.9"/>
        <rect x="240" y="300" width="16" height="22" fill="url(#glass)" rx="1" opacity="0.7"/>
        <rect x="262" y="300" width="16" height="22" fill="url(#glass)" rx="1" opacity="0.5"/>
        <rect x="284" y="300" width="16" height="22" fill="url(#glass)" rx="1" opacity="0.6"/>

        <!-- Lobby / Entrance -->
        <rect x="145" y="345" width="50" height="45" fill="#1e3a6e" rx="2"/>
        <rect x="155" y="350" width="14" height="40" fill="url(#glass)" rx="1"/>
        <rect x="171" y="350" width="14" height="40" fill="url(#glass)" rx="1"/>
        <!-- Door frame gold -->
        <rect x="143" y="343" width="54" height="4" fill="url(#gold)" rx="1"/>

        <!-- Stars / sky dots -->
        <circle cx="50" cy="40" r="1.5" fill="#e8c96a" opacity="0.8"/>
        <circle cx="80" cy="20" r="1" fill="white" opacity="0.6"/>
        <circle cx="260" cy="30" r="1.5" fill="white" opacity="0.7"/>
        <circle cx="295" cy="55" r="1" fill="#e8c96a" opacity="0.9"/>
        <circle cx="20" cy="70" r="1" fill="white" opacity="0.5"/>
        <circle cx="315" cy="15" r="1.5" fill="white" opacity="0.6"/>
      </svg>

      <!-- Floating property cards -->
      <div class="float-card card-1">
        <div class="card-icon">🏠</div>
        <div>
          <div class="card-title">3 BHK Apartment</div>
          <div class="card-price">₹1.2 Cr · Gurugram</div>
        </div>
      </div>
      <div class="float-card card-2">
        <div class="card-icon">📈</div>
        <div>
          <div class="card-title">Market Trend</div>
          <div class="card-price">+12% YoY Growth</div>
        </div>
      </div>
      <div class="float-card card-3">
        <div class="card-icon">✅</div>
        <div>
          <div class="card-title">Verified Listing</div>
          <div class="card-price">RERA Approved</div>
        </div>
      </div>
    </div>
  </div>

  <!-- Scroll indicator -->
  <div class="scroll-hint">
    <span>Scroll to explore</span>
    <div class="scroll-arrow"></div>
  </div>
</header>

<!-- ========== FEATURES SECTION ========== -->
<section class="features">
  <div class="features-inner">
    <p class="section-eyebrow">Why MyPropertyFact</p>
    <h2 class="section-title">Everything You Need to Make<br/>the Right Property Decision</h2>
    <div class="feature-grid">

      <div class="feature-card">
        <div class="feature-icon">
          <svg viewBox="0 0 48 48" fill="none" width="48" height="48">
            <circle cx="24" cy="24" r="22" fill="#C9A84C" opacity="0.12"/>
            <path d="M24 10L10 20V38H20V28H28V38H38V20L24 10Z" fill="#C9A84C" stroke="#C9A84C" stroke-width="1.5" stroke-linejoin="round"/>
          </svg>
        </div>
        <h3>10,000+ Properties</h3>
        <p>Verified listings across 50+ Indian cities with accurate pricing and RERA compliance.</p>
      </div>

      <div class="feature-card">
        <div class="feature-icon">
          <svg viewBox="0 0 48 48" fill="none" width="48" height="48">
            <circle cx="24" cy="24" r="22" fill="#C9A84C" opacity="0.12"/>
            <circle cx="24" cy="24" r="10" stroke="#C9A84C" stroke-width="2"/>
            <path d="M24 18V24L28 28" stroke="#C9A84C" stroke-width="2" stroke-linecap="round"/>
            <path d="M14 14L10 10M34 14L38 10M14 34L10 38M34 34L38 38" stroke="#C9A84C" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </div>
        <h3>Real-Time Market Data</h3>
        <p>Live pricing trends, locality reports, and investment forecasts updated daily.</p>
      </div>

      <div class="feature-card">
        <div class="feature-icon">
          <svg viewBox="0 0 48 48" fill="none" width="48" height="48">
            <circle cx="24" cy="24" r="22" fill="#C9A84C" opacity="0.12"/>
            <rect x="12" y="16" width="24" height="18" rx="3" stroke="#C9A84C" stroke-width="2"/>
            <path d="M12 22H36" stroke="#C9A84C" stroke-width="1.5"/>
            <circle cx="24" cy="30" r="2.5" fill="#C9A84C"/>
            <path d="M24 10V16" stroke="#C9A84C" stroke-width="2" stroke-linecap="round"/>
            <path d="M17 10V14M31 10V14" stroke="#C9A84C" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </div>
        <h3>AI Property Advisor</h3>
        <p>Ask our AI anything — from locality comparisons to EMI calculations and investment ROI.</p>
      </div>

      <div class="feature-card">
        <div class="feature-icon">
          <svg viewBox="0 0 48 48" fill="none" width="48" height="48">
            <circle cx="24" cy="24" r="22" fill="#C9A84C" opacity="0.12"/>
            <path d="M24 12C18.48 12 14 16.48 14 22C14 29 24 38 24 38C24 38 34 29 34 22C34 16.48 29.52 12 24 12Z" stroke="#C9A84C" stroke-width="2"/>
            <circle cx="24" cy="22" r="4" fill="#C9A84C"/>
          </svg>
        </div>
        <h3>Locality Intelligence</h3>
        <p>Deep-dive into neighbourhood scores, connectivity, schools, hospitals, and future growth.</p>
      </div>

    </div>
  </div>
</section>

<!-- ========== FLOATING CHAT BUTTON ========== -->
<button class="chat-fab" id="chatFab" onclick="openChat()" title="Chat with AI Advisor">
  <span class="fab-pulse"></span>
  <svg class="fab-icon fab-open" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
  </svg>
  <svg class="fab-icon fab-close" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round">
    <line x1="18" y1="6" x2="6" y2="18"/>
    <line x1="6" y1="6" x2="18" y2="18"/>
  </svg>
  <span class="fab-label">AI Advisor</span>
</button>

<!-- ========== CHAT WINDOW ========== -->
<div class="chat-window" id="chatWindow">
  <div class="chat-header">
    <div class="chat-header-left">
      <div class="chat-avatar">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
          <path d="M12 2L2 8V20H8V14H16V20H22V8L12 2Z" fill="white" opacity="0.9"/>
        </svg>
      </div>
      <div>
        <div class="chat-name">MyPropertyFact AI</div>
        <div class="chat-status"><span class="status-dot"></span>Online — Property Advisor</div>
      </div>
    </div>
    <button class="chat-close" onclick="closeChat()">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
        <line x1="18" y1="6" x2="6" y2="18"/>
        <line x1="6" y1="6" x2="18" y2="18"/>
      </svg>
    </button>
  </div>

  <div class="chat-messages" id="chatMessages">
    <div class="chat-welcome">
      <div class="welcome-icon">🏡</div>
      <p class="welcome-title">Hello! I'm your AI Property Advisor</p>
      <p class="welcome-sub">Ask me anything about buying, selling, renting, or investing in real estate across India.</p>
    </div>
    <div class="quick-chips">
      <button class="chip" onclick="sendQuick('What are the best areas to invest in Bangalore?')">Bangalore Investment</button>
      <button class="chip" onclick="sendQuick('What is the current price trend in Mumbai?')">Mumbai Trends</button>
      <button class="chip" onclick="sendQuick('How to check RERA registration?')">RERA Guide</button>
      <button class="chip" onclick="sendQuick('Help me calculate home loan EMI')">EMI Calculator</button>
    </div>
  </div>

  <div class="chat-input-area">
    <div class="chat-input-row">
      <input type="text" id="chatInput" placeholder="Ask about any property…" autocomplete="off"/>
      <button class="send-btn" id="sendBtn" onclick="sendMessage()">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="22" y1="2" x2="11" y2="13"/>
          <polygon points="22 2 15 22 11 13 2 9 22 2"/>
        </svg>
      </button>
    </div>
    <p class="chat-footer-note">Powered by <a href="https://mypropertyfact.in" target="_blank">mypropertyfact.in</a></p>
  </div>
</div>

<!-- Overlay -->
<div class="chat-overlay" id="chatOverlay" onclick="closeChat()"></div>

<script src="/script.js"></script>
</body>
</html>
"""

# =========================
# CREATE STYLE.CSS
# =========================

style_css = """
/* ========== RESET & BASE ========== */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --gold: #C9A84C;
  --gold-light: #e8c96a;
  --gold-dim: rgba(201,168,76,0.15);
  --navy: #050d1f;
  --navy-mid: #0A1628;
  --navy-card: #0d1e38;
  --navy-border: rgba(201,168,76,0.2);
  --text: #e8e6e0;
  --text-muted: #8a9ab5;
  --white: #ffffff;
  --radius: 16px;
  --shadow: 0 24px 64px rgba(0,0,0,0.5);
}

html { scroll-behavior: smooth; }

body {
  font-family: 'DM Sans', sans-serif;
  background: var(--navy);
  color: var(--text);
  min-height: 100vh;
  overflow-x: hidden;
}

/* ========== NAV ========== */
.nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 60px;
  position: relative;
  z-index: 10;
}

.nav-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: 'Playfair Display', serif;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--white);
  letter-spacing: 0.02em;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 36px;
  list-style: none;
}

.nav-links a {
  color: var(--text-muted);
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  letter-spacing: 0.03em;
  transition: color 0.2s;
}

.nav-links a:hover { color: var(--gold); }

.nav-cta {
  background: var(--gold-dim);
  color: var(--gold) !important;
  border: 1px solid var(--navy-border);
  padding: 8px 20px;
  border-radius: 50px;
  transition: background 0.2s, border-color 0.2s !important;
}

.nav-cta:hover {
  background: rgba(201,168,76,0.25) !important;
  border-color: var(--gold) !important;
}

/* ========== HERO ========== */
.hero {
  min-height: 100vh;
  background: radial-gradient(ellipse at 60% 0%, #0d2248 0%, var(--navy) 60%);
  position: relative;
  overflow: hidden;
}

.hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 20% 80%, rgba(201,168,76,0.06) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(74,127,193,0.08) 0%, transparent 50%);
  pointer-events: none;
}

/* subtle grid texture */
.hero::after {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(201,168,76,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(201,168,76,0.03) 1px, transparent 1px);
  background-size: 60px 60px;
  pointer-events: none;
}

.hero-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 60px 60px 40px;
  gap: 40px;
  position: relative;
  z-index: 2;
}

.hero-text {
  max-width: 540px;
  animation: fadeUp 0.8s ease forwards;
}

.hero-eyebrow {
  font-size: 0.78rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--gold);
  margin-bottom: 20px;
  font-weight: 500;
}

.hero-title {
  font-family: 'Playfair Display', serif;
  font-size: clamp(2.6rem, 4vw, 3.8rem);
  font-weight: 900;
  line-height: 1.1;
  color: var(--white);
  margin-bottom: 24px;
}

.hero-title em {
  font-style: italic;
  background: linear-gradient(135deg, var(--gold-light), var(--gold));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-sub {
  color: var(--text-muted);
  font-size: 1.05rem;
  line-height: 1.7;
  margin-bottom: 36px;
  font-weight: 300;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 48px;
  flex-wrap: wrap;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, var(--gold-light), var(--gold));
  color: var(--navy);
  border: none;
  padding: 14px 28px;
  border-radius: 50px;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 8px 24px rgba(201,168,76,0.35);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(201,168,76,0.5);
}

.btn-secondary {
  color: var(--text-muted);
  text-decoration: none;
  font-size: 0.95rem;
  font-weight: 500;
  transition: color 0.2s;
  letter-spacing: 0.02em;
}

.btn-secondary:hover { color: var(--gold); }

.hero-stats {
  display: flex;
  align-items: center;
  gap: 28px;
}

.stat { display: flex; flex-direction: column; gap: 4px; }

.stat-num {
  font-family: 'Playfair Display', serif;
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--gold);
}

.stat-label {
  font-size: 0.78rem;
  color: var(--text-muted);
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: var(--navy-border);
}

/* ========== HERO VISUAL ========== */
.hero-visual {
  position: relative;
  flex-shrink: 0;
  animation: fadeRight 0.9s ease forwards;
}

.svg-building {
  width: 340px;
  height: 420px;
  filter: drop-shadow(0 20px 60px rgba(0,0,0,0.6));
}

.float-card {
  position: absolute;
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(13, 30, 56, 0.92);
  border: 1px solid var(--navy-border);
  border-radius: 14px;
  padding: 12px 16px;
  backdrop-filter: blur(16px);
  white-space: nowrap;
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}

.card-icon { font-size: 1.4rem; }

.card-title {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--white);
  margin-bottom: 2px;
}

.card-price {
  font-size: 0.72rem;
  color: var(--gold);
  font-weight: 500;
}

.card-1 {
  top: 30px;
  left: -90px;
  animation: floatA 4s ease-in-out infinite;
}

.card-2 {
  top: 160px;
  right: -80px;
  animation: floatB 5s ease-in-out infinite;
}

.card-3 {
  bottom: 80px;
  left: -80px;
  animation: floatA 4.5s ease-in-out infinite 1s;
}

/* ========== SCROLL HINT ========== */
.scroll-hint {
  position: absolute;
  bottom: 32px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: var(--text-muted);
  font-size: 0.75rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  z-index: 2;
}

.scroll-arrow {
  width: 1px;
  height: 32px;
  background: linear-gradient(to bottom, var(--gold), transparent);
  animation: scrollPulse 2s ease-in-out infinite;
}

/* ========== FEATURES ========== */
.features {
  padding: 100px 60px;
  background: var(--navy-mid);
  position: relative;
}

.features::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--gold), transparent);
}

.features-inner { max-width: 1100px; margin: 0 auto; }

.section-eyebrow {
  font-size: 0.75rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--gold);
  margin-bottom: 14px;
  text-align: center;
}

.section-title {
  font-family: 'Playfair Display', serif;
  font-size: clamp(1.8rem, 3vw, 2.6rem);
  font-weight: 700;
  text-align: center;
  color: var(--white);
  line-height: 1.2;
  margin-bottom: 56px;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 24px;
}

.feature-card {
  background: var(--navy-card);
  border: 1px solid var(--navy-border);
  border-radius: var(--radius);
  padding: 32px 28px;
  transition: transform 0.25s, border-color 0.25s, box-shadow 0.25s;
}

.feature-card:hover {
  transform: translateY(-6px);
  border-color: rgba(201,168,76,0.5);
  box-shadow: 0 16px 40px rgba(201,168,76,0.1);
}

.feature-icon { margin-bottom: 20px; }

.feature-card h3 {
  font-family: 'Playfair Display', serif;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--white);
  margin-bottom: 12px;
}

.feature-card p {
  font-size: 0.9rem;
  color: var(--text-muted);
  line-height: 1.65;
}

/* ========== FAB BUTTON ========== */
.chat-fab {
  position: fixed;
  bottom: 32px;
  right: 32px;
  z-index: 1000;
  display: flex;
  align-items: center;
  gap: 10px;
  background: linear-gradient(135deg, var(--gold-light), #b8932a);
  color: var(--navy);
  border: none;
  border-radius: 50px;
  padding: 14px 22px 14px 18px;
  cursor: pointer;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.9rem;
  font-weight: 700;
  box-shadow: 0 8px 32px rgba(201,168,76,0.5);
  transition: transform 0.2s, box-shadow 0.2s;
}

.chat-fab:hover {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 0 14px 40px rgba(201,168,76,0.65);
}

.fab-pulse {
  position: absolute;
  top: -4px; right: -4px;
  width: 14px; height: 14px;
  background: #2ecc71;
  border-radius: 50%;
  border: 2px solid var(--navy);
  animation: pulse 2.5s ease-in-out infinite;
}

.fab-icon { transition: opacity 0.2s, transform 0.2s; }
.fab-close { display: none; }
.fab-label { color: var(--navy); }

.chat-fab.open .fab-open { display: none; }
.chat-fab.open .fab-close { display: block; }

/* ========== CHAT WINDOW ========== */
.chat-window {
  position: fixed;
  bottom: 104px;
  right: 32px;
  z-index: 999;
  width: 380px;
  max-height: 600px;
  background: var(--navy-mid);
  border: 1px solid var(--navy-border);
  border-radius: 24px;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow);
  transform: scale(0.85) translateY(20px);
  transform-origin: bottom right;
  opacity: 0;
  pointer-events: none;
  transition: transform 0.3s cubic-bezier(0.34,1.56,0.64,1), opacity 0.25s ease;
  overflow: hidden;
}

.chat-window.open {
  opacity: 1;
  transform: scale(1) translateY(0);
  pointer-events: all;
}

/* Header */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px;
  background: linear-gradient(135deg, #0d2248, #122040);
  border-bottom: 1px solid var(--navy-border);
  flex-shrink: 0;
}

.chat-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chat-avatar {
  width: 40px; height: 40px;
  background: linear-gradient(135deg, var(--gold-light), var(--gold));
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-name {
  font-family: 'Playfair Display', serif;
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--white);
}

.chat-status {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.72rem;
  color: var(--text-muted);
}

.status-dot {
  width: 7px; height: 7px;
  background: #2ecc71;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.chat-close {
  background: rgba(255,255,255,0.07);
  border: none;
  border-radius: 8px;
  width: 32px; height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-muted);
  transition: background 0.2s, color 0.2s;
}

.chat-close:hover { background: rgba(255,255,255,0.14); color: var(--white); }

/* Messages */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  scroll-behavior: smooth;
}

.chat-messages::-webkit-scrollbar { width: 4px; }
.chat-messages::-webkit-scrollbar-track { background: transparent; }
.chat-messages::-webkit-scrollbar-thumb { background: rgba(201,168,76,0.3); border-radius: 4px; }

.chat-welcome {
  text-align: center;
  padding: 12px 8px 4px;
}

.welcome-icon { font-size: 2.2rem; margin-bottom: 10px; }

.welcome-title {
  font-family: 'Playfair Display', serif;
  font-size: 0.95rem;
  color: var(--white);
  margin-bottom: 8px;
  font-weight: 600;
}

.welcome-sub {
  font-size: 0.8rem;
  color: var(--text-muted);
  line-height: 1.55;
}

.quick-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 4px;
}

.chip {
  background: var(--navy-card);
  border: 1px solid var(--navy-border);
  color: var(--gold);
  font-family: 'DM Sans', sans-serif;
  font-size: 0.76rem;
  font-weight: 500;
  padding: 7px 12px;
  border-radius: 50px;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
  white-space: nowrap;
}

.chip:hover {
  background: var(--gold-dim);
  border-color: var(--gold);
}

/* Message bubbles */
.msg {
  display: flex;
  flex-direction: column;
  gap: 2px;
  animation: fadeUp 0.3s ease forwards;
}

.msg.user { align-items: flex-end; }
.msg.bot { align-items: flex-start; }

.msg-bubble {
  max-width: 88%;
  padding: 11px 15px;
  border-radius: 16px;
  font-size: 0.86rem;
  line-height: 1.55;
}

.msg.user .msg-bubble {
  background: linear-gradient(135deg, var(--gold-light), var(--gold));
  color: var(--navy);
  font-weight: 500;
  border-bottom-right-radius: 4px;
}

.msg.bot .msg-bubble {
  background: var(--navy-card);
  color: var(--text);
  border: 1px solid var(--navy-border);
  border-bottom-left-radius: 4px;
}

.msg-time {
  font-size: 0.68rem;
  color: var(--text-muted);
  padding: 0 4px;
}

/* Typing indicator */
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 13px 16px;
  background: var(--navy-card);
  border: 1px solid var(--navy-border);
  border-radius: 16px;
  border-bottom-left-radius: 4px;
  width: fit-content;
}

.typing-dot {
  width: 7px; height: 7px;
  background: var(--gold);
  border-radius: 50%;
  animation: typingBounce 1.2s ease-in-out infinite;
}

.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

/* Input area */
.chat-input-area {
  padding: 14px 16px 12px;
  border-top: 1px solid var(--navy-border);
  background: var(--navy-mid);
  flex-shrink: 0;
}

.chat-input-row {
  display: flex;
  gap: 10px;
  align-items: center;
}

#chatInput {
  flex: 1;
  background: var(--navy-card);
  border: 1px solid var(--navy-border);
  border-radius: 50px;
  padding: 11px 18px;
  color: var(--white);
  font-family: 'DM Sans', sans-serif;
  font-size: 0.88rem;
  outline: none;
  transition: border-color 0.2s;
}

#chatInput::placeholder { color: var(--text-muted); }
#chatInput:focus { border-color: rgba(201,168,76,0.5); }

.send-btn {
  width: 42px; height: 42px;
  background: linear-gradient(135deg, var(--gold-light), var(--gold));
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: transform 0.2s, box-shadow 0.2s;
}

.send-btn:hover {
  transform: scale(1.08);
  box-shadow: 0 4px 14px rgba(201,168,76,0.5);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.chat-footer-note {
  text-align: center;
  font-size: 0.7rem;
  color: var(--text-muted);
  margin-top: 8px;
}

.chat-footer-note a {
  color: var(--gold);
  text-decoration: none;
}

/* Overlay for mobile */
.chat-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  z-index: 998;
  backdrop-filter: blur(2px);
}

.chat-overlay.active { display: block; }

/* ========== ANIMATIONS ========== */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}

@keyframes fadeRight {
  from { opacity: 0; transform: translateX(40px); }
  to   { opacity: 1; transform: translateX(0); }
}

@keyframes floatA {
  0%, 100% { transform: translateY(0px); }
  50%       { transform: translateY(-12px); }
}

@keyframes floatB {
  0%, 100% { transform: translateY(0px); }
  50%       { transform: translateY(10px); }
}

@keyframes scrollPulse {
  0%, 100% { opacity: 0.3; }
  50%       { opacity: 1; }
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%       { opacity: 0.6; transform: scale(1.2); }
}

@keyframes typingBounce {
  0%, 80%, 100% { transform: scale(1); opacity: 0.4; }
  40%            { transform: scale(1.4); opacity: 1; }
}

/* ========== RESPONSIVE ========== */
@media (max-width: 900px) {
  .nav { padding: 20px 24px; }
  .nav-links { display: none; }
  .hero-content { flex-direction: column; padding: 40px 24px 60px; text-align: center; }
  .hero-actions { justify-content: center; }
  .hero-stats { justify-content: center; }
  .hero-visual { order: -1; }
  .svg-building { width: 260px; height: 320px; }
  .card-1, .card-2, .card-3 { display: none; }
  .features { padding: 60px 24px; }
  .chat-window { width: calc(100vw - 32px); right: 16px; bottom: 90px; }
  .chat-fab { right: 20px; bottom: 20px; }
}
"""

# =========================
# CREATE SCRIPT.JS
# =========================

script_js = """
const USER_ID = 'user_' + Date.now();
let chatOpen = false;

// ---- Open / Close ----

function openChat() {
  chatOpen = true;
  document.getElementById('chatWindow').classList.add('open');
  document.getElementById('chatFab').classList.add('open');
  document.getElementById('chatOverlay').classList.add('active');
  setTimeout(() => document.getElementById('chatInput').focus(), 350);
}

function closeChat() {
  chatOpen = false;
  document.getElementById('chatWindow').classList.remove('open');
  document.getElementById('chatFab').classList.remove('open');
  document.getElementById('chatOverlay').classList.remove('active');
}

// ---- Utilities ----

function getTime() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function scrollToBottom() {
  const el = document.getElementById('chatMessages');
  el.scrollTop = el.scrollHeight;
}

function appendMessage(role, text) {
  const msgs = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = 'msg ' + role;
  div.innerHTML = `
    <div class="msg-bubble">${formatText(text)}</div>
    <span class="msg-time">${getTime()}</span>
  `;
  msgs.appendChild(div);
  scrollToBottom();
}

function formatText(text) {
  return text
    .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
    .replace(/\\n/g, '<br/>');
}

function showTyping() {
  const msgs = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.id = 'typingIndicator';
  div.className = 'msg bot';
  div.innerHTML = `
    <div class="typing-indicator">
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    </div>
  `;
  msgs.appendChild(div);
  scrollToBottom();
}

function removeTyping() {
  const el = document.getElementById('typingIndicator');
  if (el) el.remove();
}

// ---- Send ----

async function sendMessage() {
  const input = document.getElementById('chatInput');
  const btn = document.getElementById('sendBtn');
  const message = input.value.trim();
  if (!message) return;

  // Hide quick chips after first message
  const chips = document.querySelector('.quick-chips');
  if (chips) chips.style.display = 'none';

  input.value = '';
  btn.disabled = true;
  appendMessage('user', message);
  showTyping();

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, user_id: USER_ID })
    });
    const data = await res.json();
    removeTyping();
    appendMessage('bot', data.response);
  } catch (err) {
    removeTyping();
    appendMessage('bot', '⚠️ Sorry, I could not connect. Please try again.');
  } finally {
    btn.disabled = false;
    input.focus();
  }
}

function sendQuick(text) {
  document.getElementById('chatInput').value = text;
  sendMessage();
}

// ---- Enter key ----
document.getElementById('chatInput').addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) sendMessage();
});
"""

# =========================
# SAVE STATIC FILES
# =========================

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(index_html)

with open("static/style.css", "w", encoding="utf-8") as f:
    f.write(style_css)

with open("static/script.js", "w", encoding="utf-8") as f:
    f.write(script_js)

print("✅ Static files created")

# =========================
# MOUNT STATIC FILES
# =========================

app.mount("/", StaticFiles(directory="static", html=True), name="static")

# =========================
# RUN SERVER
# =========================

# Run:
# uvicorn main:app --reload