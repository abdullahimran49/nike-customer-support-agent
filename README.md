# 🏃‍♂️ Nike Store Chat Assistant

> **An enterprise-grade multi-agent AI customer support system leveraging Google Gemini API and intelligent agent orchestration**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-View%20App-blue?style=for-the-badge)](https://nike-support-agent.up.railway.app)
[![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python)](https://www.python.org/)
[![Gemini API](https://img.shields.io/badge/Google-Gemini%202.0%20Flash-orange?style=for-the-badge&logo=google)](https://gemini.google.com/)
[![Chainlit](https://img.shields.io/badge/Chainlit-Streaming-purple?style=for-the-badge)](https://chainlit.io/)

---

## 📋 Project Overview

The **Nike Store Chat Assistant** is a sophisticated AI-powered system built using **Google Gemini 2.0 Flash API** and a **multi-agent architecture**. It is designed to handle customer queries for Nike store operations with real-time streaming, intelligent routing, and robust safety guardrails.

**Key Highlights:**

- 6 specialized agents with intelligent orchestration
- Async token-by-token streaming responses via Chainlit
- Production deployment on Railway
- Input validation and safety guardrails
- SQLite-powered order management

---

## 🚀 Technical Architecture

### 🤖 Multi-Agent System

| Agent | Function | Implementation | Tools & Capabilities |
|-------|---------|----------------|-------------------|
| **Orchestrator Agent** | Query analysis & routing | Intent classification via Gemini API | Delegates to specialized agents using context |
| **Products Agent** | Product info & availability | External API integration | `get_products_info()` with caching |
| **Order Tracking Agent** | Order status queries | SQLite database operations | `get_order_status()` by customer or order ID |
| **Returns Agent** | Returns & refunds | File system integration | `get_return_policy()` with step-by-step guidance |
| **Inquiry Agent** | General FAQs | Text-based FAQ management | `get_faqs()` with structured Q&A |
| **Escalation Agent** | Complex issue handling | Human handoff protocols | Summarizes cases for human support |

---

### 🛠️ Technology Stack

```python
# Core Technologies
Google Gemini 2.0 Flash API    # Advanced LLM understanding
AsyncOpenAI Client             # Async API communication
Chainlit Framework             # Real-time chat streaming
SQLite Database                # Order management
Pydantic Models                # Data validation & type safety
Python-dotenv                  # Environment configuration


```

# 🔧 Key Features

- **Async Processing:** Fully asynchronous query handling  
- **Streaming Responses:** Real-time token-by-token display  
- **Session Management:** Stores last 20 messages per user  
- **Function Tools:** Decorator-based agent tools with type safety  
- **Input Validation:** Pydantic models for structured input  
- **Error Recovery:** Graceful fallback and exception handling  
- **Guardrails:** Content safety and inappropriate request blocking


# 🔄 Agent Workflow
mermaid
graph TD
    A[User Query] --> B[Orchestrator Agent]
    B --> C{Query Analysis}
    C -->|Product Info| D[Products Agent]
    C -->|Order Status| E[Order Tracking Agent]
    C -->|Returns/Refunds| F[Returns Agent]
    C -->|General Questions| G[Inquiry Agent]
    C -->|Complex Issues| H[Escalation Agent]
    D --> I[Response + Handoff Options]
    E --> I
    F --> I
    G --> I
    H --> J[Human Support]
    I --> K[User Response]

# 🛒 Sample Orders

| Order ID | Customer | Product                     | Status      | Scenario               |
|----------|----------|-----------------------------|------------|-----------------------|
| 1        | Ali      | Nike Air Force 1 Mid '07    | Shipped     | ✅ Standard inquiry    |
| 2        | Sara     | Adidas Ultraboost 22        | Processing  | ⏳ In-progress         |
| 3        | John     | Puma Running Shoes          | Delivered   | ✅ Completed           |
| 4        | Emma     | Reebok Classic Leather      | Cancelled   | ❌ Cancellation        |


# 🔍 Test Queries

## Product Queries
- "Show me Nike Air Force 1 details"  
- "Compare Nike and Adidas shoes"  
- "Which Nike shoes are in stock?"  

## Order Tracking
- "Check order status for Ali"  
- "What's the status of order 2?"  
- "Check order for David"  
## Returns
- "How do I return defective shoes?"  
- "What's your refund policy?"  
- "I want to cancel my recent order"  

## Store Info
- "What are your store hours?"  
- "Do you deliver to Karachi?"  
- "What payment methods do you accept?"  

## Escalation
- "Your delivery service is terrible, I want compensation"  


# 🛡️ Guardrails & Safety

- Blocks unsafe or inappropriate content automatically  
- Validates input with Pydantic models  
- Provides fallback responses for unrecognized queries  

# 🌐 Live Demo

Try the app online: [Nike Support Agent](https://nike-support-agent.up.railway.app)


# Clone the repository
git clone https://github.com/your-username/nike-customer-support-agent.git
cd nike-customer-support-agent

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Update API keys and configuration in .env
Make env file and add GEMINI_API_KEY=YOURAPIKEY
# 📝 License

This project is **MIT Licensed** – see `LICENSE` for details.




