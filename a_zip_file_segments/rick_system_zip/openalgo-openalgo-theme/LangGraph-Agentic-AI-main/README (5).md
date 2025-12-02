### 📈 Agentic AI Trading Agents (LangGraph Orchestrated)
![Alt Text](copilot_image_1754130941070.jpeg).
This project implements an **Agentic AI stock trading system**, built with a modular multi-agent architecture orchestrated using [LangGraph](https://github.com/langchain-ai/langgraph). Each agent contributes specialized reasoning using LLMs such as **Mistral**, **LLaMA**, and APIs like **Tavily** or **Selenium** for real-world visibility.

---

## 🚀 Features

- **Microservice AI Agents:** Each agent (ChartAnalyst, RiskManager, MacroForecaster, etc.) is a containerized FastAPI service.
- **Event Bus Architecture:** Agents communicate and coordinate via Redis Pub/Sub for low-latency, event-driven workflows.
- **Central Orchestrator:** Aggregates agent signals, applies business logic, logs outcomes, and triggers platform actions.
- **Full Logging & Analytics:** PostgreSQL (or TimescaleDB) stores all predictions, agent outputs, and trade outcomes for analytics and dashboards.
- **Real-time Frontend:** Modern React dashboard with live signals, reasonings, TradingView overlays, and outcome analytics.
- **DevOps-Ready:** Docker Compose for easy orchestration and local dev; supports CI/CD and scaling.
- **Extendable & Explainable:** Add new agents, swap LLMs, and audit all agent decisions with clear reasoning chains.

---
---

## 🏗️ Process Architecture

```mermaid
graph TD
    A[Market Event/Price Tick] --> B[ChartAnalyst]
    A --> C[MarketSentinel]
    A --> D[MacroForecaster]
    B --> E[RiskManager]
    C --> E
    D --> E
    E --> F[TacticBot]
    F --> G[PlatformPilot]
    G --> H[PostgreSQL DB]
    G --> I[Frontend Dashboard]
```


**Flow:**  
1. New market event → published to event bus  
2. Specialist agents analyze and emit signals  
3. RiskManager aggregates and evaluates  
4. TacticBot decides entry/exit  
5. PlatformPilot triggers trade, logs, and updates frontend

---

### ⚙️ Architecture Overview

```
               ┌──────────────────────┐
               │   Frontend    │
               │   (React)     │
               └─────┌────────┘
                      │
               ┌─────│─────────┐
               │  Orchestrator │ <──── REST & WebSocket API (FastAPI)
               │ (LangGraph)   │
               └────│────────┘
                    │
        ┌─────────┬────────────────────────────┐
        ▼           ▼                       ▼
   chart_analyst   risk_manager      market_sentinel
     (LLMs +         (logic +             (news/
   chart data)      thresholds)       event scanner)

                      ...
        (additional agents plugged into LangGraph)

```

---

### 🧠 Agents Overview

Each agent lives in `backend/agents/<agent_name>/`, and uses:

* **LLMs (Mistral/LLaMA via OpenRouter)** for reasoning
* **Tavily API** or **Selenium** for real-time intelligence
* **Shared Event Bus (Redis)** for coordination
* **Postgres DB** to persist signals and outcomes


---
## 🧠 Agents & Their Roles

| Agent              | Model Example      | Description                                                                 |
|--------------------|-------------------|-----------------------------------------------------------------------------|
| ChartAnalyst       | Mistral, Llama    | Analyzes price charts, detects patterns/zones, publishes technical signals  |
| RiskManager        | Kimi K2, Claude   | Consumes signals, applies risk logic, outputs sizes/stop-loss/risk metrics  |
| MarketSentinel     | Qwen3, GPT-4      | Monitors volatility, news, market regimes, raises alerts                    |
| MacroForecaster    | TNG Chimera       | Assesses macro/news impact, forecasts directional bias                      |
| TacticBot          | GLM, Horizon      | Aggregates all signals, triggers entry/exit, encodes trade tactics          |
| PlatformPilot      | Kimi Dev 72B      | Logs actions, triggers platform automation, serves as audit & automation    |

**Each agent is a REST API container with a clear JSON contract.**

---


## 🔗 Event Bus Flow

- All agent communication is via Redis Pub/Sub (or Kafka).
- New market event → bus → specialist agents consume → output signals → bus → downstream agents consume (event loop).
- Orchestrator listens, aggregates, and finalizes trade actions.

Example event channels:
- `market_events`, `chartanalyst_out`, `riskmanager_out`, `final_signals`, etc.

---
**PostgreSQL (or TimescaleDB)**

- `agents`: Registered agents, models, status
- `trade_signals`: Each agent’s signal, raw and processed
- `trade_outcomes`: Actual trade results, PnL, success
- `macro_events`: Global news/context per signal

---


### 🚀 Quickstart

#### 1. Clone the repository

```bash
git clone https://github.com/your-org/agentic-ai-trading-system.git
cd agentic-ai-trading-system/agentic-trading
```

#### 2. Fill in `.env` (already present)

Ensure your `.env` has valid API keys:

```
OPENROUTER_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
DATABASE_URL=postgresql://postgres:password@postgres:5432/agentic_trading
...
```

#### 3. Build and run with Docker Compose

```bash
docker-compose up -d --build
```

Access services:

* **API Docs**: [http://localhost:8007/docs](http://localhost:8007/docs)
* **Frontend UI**: [http://localhost:3000](http://localhost:3000)

#### 4. Run the MCP (Multi-Agent Control Protocol)

```bash
curl -X POST http://localhost:8007/run_mcp \
  -H "Content-Type: application/json" \
  -d '{"symbol": "EURUSD", "timeframe": "1h"}'
```

---

### 🔪 Testing a Single Agent (e.g. `chart_analyst`)

```bash
cd backend
python3 -m agents.chartanalyst.test
```

Make sure `__init__.py` files are present in all relevant folders.

---

### 📙 LangGraph MCP Setup

The orchestration graph is defined in:

```
backend/orchestrator/mcp_graph.py
```

It uses LangGraph’s `StateGraph` to build the reasoning flow across agents. You can visualize or extend the graph from here.

---

### 📂 Project Structure

```
agentic-trading/
├── backend/
│   ├── agents/                # Individual agent folders
│   ├── db/                    # DB models and init
│   └── orchestrator/
│       ├── api.py             # FastAPI orchestrator
│       ├── mcp_graph.py       # LangGraph setup
│       └── event_bus.py       # Redis PubSub
└── frontend/                  # React UI (built with react-scripts)

+ .env, docker-compose.yml, etc.
```

---

### 🛠️ Tech Stack

* **LangGraph** for agent graph orchestration
* **FastAPI** + **Uvicorn** for REST + WebSocket
* **React** for dashboard
* **PostgreSQL** as primary DB
* **Redis** for event messaging
* **OpenRouter LLMs** (Mistral, LLaMA, etc.)
* **Tavily / Selenium** for external visibility

---

### 📊 Coming Soon

* ✅ Graph visualization endpoint
* ✅ Per-agent logs and trace UI
* ⟳ Retraining agents on feedback
* 📈 Agent performance dashboards
* 🧠 Auto-improving agents using outcomes

---

## 🙋 FAQ

**Q: Can I use my own LLMs/Quant libraries?**  
A: Yes, just update agent logic.

**Q: Can it run on the cloud?**  
A: Yes, deploy each service as a container on any cloud infra.

**Q: Can I add more agents?**  
A: Yes! The architecture is designed for modular growth.

---

## 🤝 Credits

Built by [martin861101](https://github.com/martin861101) and contributors.

---

**Questions? PRs? Feature Requests? [Open an issue!](https://github.com/martin861101/agentic-ai-trading-system/issues)**

---

This README is ready for production and onboarding contributors.  
Copy, edit, and enjoy building your agentic AI trading platform!
