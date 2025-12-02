# Agentic AI Stock Trading System

This project implements an Agentic AI stock trading system, built with a modular multi-agent architecture orchestrated using LangGraph. Each agent contributes specialized reasoning using LLMs such as Mistral, LLaMA, and APIs like Tavily, Gemini, or Selenium for real-world visibility.

## Project Structure

```
/home/projects/viteapp/
├── .env
├── App.jsx
├── build.py
├── create_vite_app.sh
├── directory_tree.py
├── docker-compose.yml
├── Dockerfile
├── GEMINI.md
├── project_export_inline.md
├── README (5).md
├── requirements.txt
├── test_publisher.py
├── backend/
│   ├── __init__.py
│   ├── .env
│   ├── ai_client.py
│   ├── config.py
│   ├── create_agents.py
│   ├── create_analyst.py
│   ├── create1.py
│   ├── Dockerfile.agent
│   ├── Dockerfile.orchestrator
│   ├── Dockerfile.websocket
│   ├── fetch_market_news.py
│   ├── fetch_market_prices.py
│   ├── gemini.py
│   ├── mcp_setup.py
│   ├── requirements.txt
│   ├── wait-for-postgres.sh
│   ├── websocket_server.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── chartanalyst/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py
│   │   │   └── main.py
│   │   ├── macroforecaster/
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   ├── marketdatafetcher/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py
│   │   │   └── main.py
│   │   ├── marketsentinel/
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   ├── platformpilot/
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   ├── riskmanager/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py
│   │   │   └── main.py
│   │   └── tacticbot/
│   │       ├── __init__.py
│   │       └── main.py
│   ├── automation/
│   │   └── mcp_scheduler.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── db_session.py
│   │   └── models.py
│   ├── event_producers/
│   │   └── market_event_publisher.py
│   ├── langgraph_mcp/
│   │   ├── __init__.py
│   │   ├── agent_state.py
│   │   ├── graph.py
│   │   └── nodes/
│   │       ├── __init__.py
│   │       ├── chart_analyst.py
│   │       ├── macro_forecaster.py
│   │       ├── market_sentinel.py
│   │       ├── platform_pilot.py
│   │       ├── risk_manager.py
│   │       └── tactic_bot.py
│   ├── log_config/
│   │   ├── __init__.py
│   │   └── handler.py
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   ├── api.py
│   │   ├── event_bus.py
│   │   ├── fixed_chartanalys.py
│   │   ├── main.py
│   │   ├── market_event_publisher.py
│   │   ├── mcp_graph.py
│   │   ├── models.py
│   │   ├── run_agents.py
│   │   ├── run_all_agents.py
│   │   ├── run_chartanalyst.py
│   │   ├── run_macroforecaster.py
│   │   ├── run_marketsentinel.py
│   │   ├── run_platformpilot.py
│   │   ├── run_riskmanager.py
│   │   ├── run_tacticbot.py
│   │   ├── trigger_graph.py
│   │   └── trigger_script.py
│   ├── scripts/
│   │   └── __init__.py
│   ├── utils/
│   │   └── redis_publisher.py
│   └── websocket/
│       └── websocket_server.py
└── frontend/
    ├── .env
    ├── .gitignore
    ├── Dockerfile
    ├── eslint.config.js
    ├── index.html
    ├── nginx.conf
    ├── package-lock.json
    ├── package.json
    ├── postcss.config.js
    ├── README.md
    ├── tailwind.config.js
    ├── tsconfig.app.json
    ├── tsconfig.json
    ├── tsconfig.node.json
    ├── vite.config.ts
    ├── public/
    │   └── vite.svg
    └── src/
        ├── App.jsx
        ├── index.css
        ├── main.jsx
        ├── vite-env.d.ts
        ├── assets/
        ├── components/
        │   ├── dashboard/
        │   │   ├── ActiveTrades.tsx
        │   │   ├── AgentStatusGrid.tsx
        │   │   ├── DonutChart.tsx
        │   │   ├── Header.tsx
        │   │   ├── MarketOverview.tsx
        │   │   ├── Navbar.tsx
        │   │   ├── PerformanceMetrics.tsx
        │   │   └── RecentSignals.tsx
        │   ├── Layout.tsx
        │   └── NeonButton.tsx
        ├── pages/
        │   └── Dashboard.tsx
        ├── services/
        │   ├── api.ts
        │   ├── socket.ts
        │   └── websocket.ts
        ├── store/
        │   └── useDashboardStore.ts
        └── styles/
            └── global.css
```

## Frontend Application

The frontend application is a React-based dashboard built with Tailwind CSS for styling and Framer Motion for animations. It provides a real-time overview of the multi-agent trading system, including agent status, trading analytics, and recent signals.

### Installation and Setup

To run the frontend application:

1.  **Navigate to the `frontend` directory:**
    ```bash
    cd frontend
    ```
2.  **Install dependencies:**
    ```bash
    npm install
    ```
3.  **Start the development server:**
    ```bash
    npm run dev
    ```

The application should now be running at `http://localhost:3001`.

### Key Features

*   **Agent Dashboard:** Real-time monitoring of all AI trading agents, including their status, P&L, and open positions.
*   **Trading Analytics:** Visualizations of monthly performance, total P&L, total trades, win rate, and agent signal distribution.
*   **Real-time Alerts:** Displays critical alerts from the system.
*   **Responsive Design:** Adapts to different screen sizes.

### Technologies Used

*   **React:** Frontend JavaScript library.
*   **Tailwind CSS:** Utility-first CSS framework for rapid UI development.
*   **Framer Motion:** Library for production-ready animations.
*   **Lucide React:** Beautifully simple and customizable open-source icons.
*   **Recharts:** Redefined chart library built with React and D3.
*   **Zustand:** A small, fast, and scalable bearbones state-management solution.
*   **TypeScript:** Strongly typed superset of JavaScript.
*   **Vite:** Next-generation frontend tooling.

## Backend Integration

The frontend communicates with the backend services (WebSocket server and Orchestrator API) via environment variables configured in `docker-compose.yml`.

*   **WebSocket Connection:** The frontend connects to the `websocket_server` on port `8008` for real-time updates on market events, agent signals, and trade executions. The `REACT_APP_WS_URL` environment variable is used to configure the WebSocket URL.
*   **Orchestrator API:** The frontend can interact with the `orchestrator` service on port `8007` for triggering MCP pipelines or fetching other data.

## Docker Deployment

The entire system can be deployed using Docker Compose. Refer to the `docker-compose.yml` file for service definitions and environment configurations.

To build and run the Docker containers:

1.  **Ensure Docker and Docker Compose are installed.**
2.  **Navigate to the project root directory:**
    ```bash
    cd /home/projects/viteapp
    ```
3.  **Build and start the services:**
    ```bash
    docker-compose up --build
    ```

This will build all necessary images and start the Redis, PostgreSQL, WebSocket Server, Orchestrator, Frontend, and all agent services.