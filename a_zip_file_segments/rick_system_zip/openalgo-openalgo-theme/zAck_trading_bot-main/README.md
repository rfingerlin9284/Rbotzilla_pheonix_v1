zAck Trading Bot 3.0: An AI-Powered Algorithmic Trading System
zAck Trading Bot is a sophisticated, event-driven, and modular algorithmic trading application designed for the Indian stock market (NIFTY 50). It leverages modern AI, including Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG), to make intelligent, data-driven trading decisions.

Key Features
Automated F&O Trading: Fully automates the process of analyzing market data, generating trade signals, and executing F&O (Futures & Options) orders via the Zerodha Kite Connect API.

Multi-Strategy Framework: Comes with a library of over 10 pre-built trading strategies, from classic trend-following (Supertrend, MACD) to advanced reversal and volatility-based strategies.

AI-Powered Strategy Selection: Utilizes Google's Gemini LLM to analyze real-time market conditions (VIX, IV, economic events) and select the most suitable trading strategy for the day.

Retrieval-Augmented Generation (RAG): The bot's decision-making is enhanced by a RAG pipeline that retrieves historical performance data from its own trade logs, providing the AI with data-driven context. I have not added this rag_service.py to this code repository, but you can build your own RAG logic, placeholders are kept for you. In case you want to run the bot without this file, keep rag_usage flag in config.yaml as false. PS. I want to keep my RAG logic personal. 

Natural Language Prompting: Allows the user to provide a natural language prompt (e.g., "market looks choppy, prefer breakout strategies") at startup, which the AI considers during strategy selection.

Dynamic Strategy Reassessment: If no trade signal is generated for a configurable period, the bot automatically re-evaluates market conditions and can switch to a more appropriate strategy mid-day.

Real-Time Sentiment Analysis: Fetches and analyzes the latest financial news using the News API and TextBlob to determine market sentiment, from "Very Bearish" to "Very Bullish".

Economic Event Awareness: Scrapes data on upcoming economic events (e.g., Fed and RBI meetings) to factor into its market condition analysis.

Paper Trading Mode: Includes a fully-featured paper trading mode to test strategies and bot performance without risking real capital.

Automated Email Reporting: Sends detailed daily and monthly performance reports via email, segregating live and paper trade P&L.

Architecture Overview
The application is built on a modular, agent-based architecture designed for scalability and resilience.

Orchestrator (trading_bot.py): The central brain of the application. It manages the main event loop, state transitions (e.g., AWAITING_SIGNAL, IN_POSITION), and coordinates all other agents.

Agents (agents.py):

OrderExecutionAgent: Handles all aspects of order placement, sizing, and communication with the Kite API. Implements the "Isolated Worker Pattern" to ensure thread-safe order execution.

PositionManagementAgent: Manages active trades, applying stop-loss, trailing stop-loss, and other risk management rules.

Intelligence Layer:

langgraph_agent.py: Interfaces with the Gemini LLM to select strategies.

sentiment_agent.py: Fetches and analyzes news to determine market sentiment.

market_context.py: Identifies current market conditions (VIX, IV, etc.).

rag_service.py: The RAG engine that retrieves historical performance from logs to augment the AI's prompts.

Strategy & Indicators:

strategy_factory.py: A library of all trading strategies.

indicator_calculator.py & indicators.py: Calculate all necessary technical indicators.

Reporting & Persistence:

reporting.py: Manages the generation and emailing of performance reports.

output/: Directory where trade logs and backtest results are stored.

Setup and Installation
Prerequisites
Python: Python 3.9 or higher.

TA-Lib: The TA-Lib library must be installed on your system before you can install the Python wrapper. This is a critical step.

macOS (using Homebrew):

brew install ta-lib

Ubuntu/Debian:

sudo apt-get install -y ta-lib-dev

Windows:
Download ta-lib-0.4.0-msvc.zip from SourceForge, unzip it to C:\ta-lib, and then install the Python wrapper.

Installation Steps
Clone the Repository:

git clone https://github.com/zackakshayy/zAck_trading_bot.git
cd zAck_trading_bot

Create and Activate a Virtual Environment:

# For macOS/Linux
python3 -m venv trade_bot
source trade_bot/bin/activate

# For Windows
python -m venv trade_bot
trade_bot\Scripts\activate

Install Dependencies:
Install all the required Python libraries using the requirements.txt file.

pip install -r requirements.txt

Configure the Bot (config.yaml):
Create a config.yaml file in the root directory. Use the following template and fill in your details. Do not commit this file to GitHub.

zerodha:
  api_key: "YOUR_KITE_API_KEY"
  api_secret: "YOUR_KITE_API_SECRET"
  # The access_token will be populated automatically after the first login
  access_token: ""

google_api:
  api_key: "YOUR_GOOGLE_GEMINI_API_KEY"

news_api:
  api_key: "YOUR_NEWSAPI_API_KEY"

email_settings:
  send_daily_report: true
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
  sender_email: "your_email@gmail.com"
  sender_password: "YOUR_GMAIL_APP_PASSWORD" # Use an App Password for security
  receiver_email: "receiver_email@example.com"

trading_flags:
  underlying_instrument: "NIFTY 50"
  chart_timeframe: "5minute"
  product_type: "MIS" # or "NRML"
  order_variety: "REGULAR"
  risk_per_trade_percent: 1.0 # e.g., 1% of capital
  stop_loss_percent: 15.0 # 15% stop-loss on the option premium
  max_trades_per_day: 5
  paper_trading: true # Set to false for live trading
  enable_gemini_loss_analysis: true
  enable_natural_language_prompt: true
  strategy_reassessment_period_minutes: 60
  use_rag: false
  rag_min_trading_days: 5

How to Run
Activate Your Virtual Environment:

source trade_bot/bin/activate

Run the Main Bot Script:

python trading_bot.py

First-Time Authentication:
The first time you run the script, it will print a Kite login URL in the console.

Copy this URL and paste it into your web browser.

Log in with your Zerodha credentials.

After a successful login, you will be redirected to a blank page. Copy the request_token from the URL in your browser's address bar.

Paste this request_token back into the terminal when prompted.

The bot will then start its setup sequence and begin trading.

Disclaimer
This software is provided for educational and experimental purposes only. Algorithmic trading involves substantial risk and is not suitable for all investors. The authors and contributors are not responsible for any financial losses incurred through the use of this software. Always test thoroughly in paper trading mode before deploying with real capital.