# AI Financial Analyst 📈🤖

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688)

A state-of-the-art **Multi-Agent System** designed to analyze **Indian Stock Market (NSE)** data. Powered by **Google Gemini 2.0 Flash**, this AI analyst performs comprehensive fundamental and technical analysis to provide actionable investment recommendations.

## 🚀 Features

*   **Multi-Agent Architecture**: Orchestrated agents specializing in different domains working together.
    *   **Market Data Agent**: Fetches real-time prices, historical data, and company info with caching.
    *   **Fundamental Agent**: Analyzes balance sheets, P&L, cash flow, and financial ratios.
    *   **Technical Agent**: Computes indicators (RSI, MACD, Bollinger Bands), identifies trends, and support/resistance levels.
    *   **Strategy Agent**: Synthesizes all data to generate Buy/Sell/Hold signals with confidence scores and target prices.
*   **LLM-Powered Insights**: Uses **Gemini 2.0** to generate human-readable explanations for complex financial metrics.
*   **Real-time Indian Market Data**: Integrated with `yfinance` and `nsepython` for NSE stocks.
*   **Modern Dashboard**: Premium Next.js frontend with interactive charts (`recharts`), dark mode, and glassmorphism design.
*   **Stock Comparison**: Compare up to 5 stocks side-by-side with key metrics.
*   **Intelligent Caching**: 5-minute TTL cache for market data to improve performance.
*   **Error Handling**: Comprehensive error handling with retry logic and validation.
*   **Logging**: Full application logging for debugging and monitoring.
*   **API Documentation**: Complete API documentation with examples.
*   **Testing**: Unit and integration tests for reliability.

## 🛠️ Tech Stack

### Backend
*   **Framework**: FastAPI
*   **Orchestration**: LangGraph
*   **LLM**: Google Gemini 2.0 Flash (`google-generativeai`)
*   **Data Analysis**: Pandas, Pandas-TA, NumPy
*   **Market Data**: yfinance, nsepython

### Frontend
*   **Framework**: Next.js 14 (App Router)
*   **Language**: TypeScript
*   **Styling**: CSS Modules (Custom Design System)
*   **Visualization**: Recharts, Lucide React

## ⚡ Quick Start

### Prerequisites
*   Python 3.10+
*   Node.js 18+
*   A Google Gemini API Key

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure Environment Variables
# Create a .env file and add your Google API Key
echo "GOOGLE_API_KEY=your_actual_api_key_here" > .env

# Run the server
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

Open `http://localhost:3000` in your browser to start analyzing stocks!

## 🖥️ Screen Usage

1.  Enter an NSE stock symbol (e.g., `RELIANCE.NS`, `TCS.NS`, `INFY.NS`) in the search bar.
2.  View the **Overview** tab for the final AI recommendation and price history.
3.  Explore **Fundamental** and **Technical** tabs for deep-dive metrics and charts.

## 🏗️ Architecture

```mermaid
graph TD
    User[User / Frontend] -->|Request Analysis| Orch[LangGraph Orchestrator]
    Orch -->|1. Fetch Data| Market[Market Data Agent]
    Market -->|Data| Orch
    Orch -->|2. Parallel Analysis| Fund[Fundamental Agent]
    Orch -->|2. Parallel Analysis| Tech[Technical Agent]
    Fund -->|Insights| Orch
    Tech -->|Signals| Orch
    Orch -->|3. Synthesize| Strat[Strategy Agent]
    Strat -->|Recommendation| Orch
    Orch -->|4. Final Response| User
```

## 📚 Documentation

- **[API Documentation](API.md)**: Complete API reference with examples
- **[Developer Guide](DEVELOPER.md)**: Architecture, code style, and contribution guidelines
- **[Deployment Guide](DEPLOYMENT.md)**: Production deployment instructions

## 🧪 Testing

Run backend tests:
```bash
cd backend
pytest tests/ -v

# Run tests excluding slow tests
pytest tests/ -v -m "not slow"

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'add some amazing feature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

See [DEVELOPER.md](DEVELOPER.md) for detailed development guidelines.

## 📄 License

This project is licensed under the MIT License.
