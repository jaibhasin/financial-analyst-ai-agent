'use client';

import { useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import { Search, TrendingUp, BarChart3, Brain, Zap } from 'lucide-react';

export default function Home() {
  const [ticker, setTicker] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!ticker.trim()) return;
    
    setIsLoading(true);
    router.push(`/analysis/${ticker.toUpperCase()}`);
  };

  const popularStocks = [
    { ticker: 'RELIANCE', name: 'Reliance Industries' },
    { ticker: 'TCS', name: 'Tata Consultancy Services' },
    { ticker: 'INFY', name: 'Infosys Ltd' },
    { ticker: 'HDFCBANK', name: 'HDFC Bank' },
    { ticker: 'TATAMOTORS', name: 'Tata Motors' },
    { ticker: 'WIPRO', name: 'Wipro Ltd' }
  ];

  return (
    <main>
      {/* Navigation */}
      <nav className="navbar">
        <div className="container navbar-content">
          <div className="logo">
            <Brain size={32} />
            AI Financial Analyst
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <h1>AI-Powered Stock Analysis</h1>
          <p>
            Get comprehensive analysis of Indian stocks using multi-agent AI. 
            Fundamental, technical, and sentiment analysis at your fingertips.
          </p>

          {/* Search Box */}
          <div className="search-container">
            <form className="search-box" onSubmit={handleSubmit}>
              <input
                type="text"
                className="input input-lg"
                placeholder="Enter stock ticker (e.g., RELIANCE, TCS)"
                value={ticker}
                onChange={(e) => setTicker(e.target.value.toUpperCase())}
              />
              <button 
                type="submit" 
                className="btn btn-primary btn-lg"
                disabled={isLoading}
              >
                {isLoading ? (
                  <div className="spinner" style={{ width: 24, height: 24, borderWidth: 2 }} />
                ) : (
                  <>
                    <Search size={20} />
                    Analyze
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Popular Stocks */}
          <div className="mt-4">
            <p className="text-muted mb-2">Popular Stocks</p>
            <div className="flex justify-center gap-2" style={{ flexWrap: 'wrap' }}>
              {popularStocks.map((stock) => (
                <button
                  key={stock.ticker}
                  className="btn btn-secondary"
                  onClick={() => {
                    setTicker(stock.ticker);
                    router.push(`/analysis/${stock.ticker}`);
                  }}
                >
                  {stock.ticker}
                </button>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mt-4">
        <div className="analysis-grid">
          <div className="card card-glass">
            <div className="flex items-center gap-2 mb-2">
              <BarChart3 size={24} className="text-success" />
              <h3>Fundamental Analysis</h3>
            </div>
            <p className="text-muted">
              Deep dive into financial statements, profitability ratios, debt levels, 
              and growth metrics. Understand the company's true value.
            </p>
          </div>

          <div className="card card-glass">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp size={24} style={{ color: '#8b5cf6' }} />
              <h3>Technical Analysis</h3>
            </div>
            <p className="text-muted">
              Chart patterns, RSI, MACD, Bollinger Bands, and more. 
              Get actionable signals based on price action.
            </p>
          </div>

          <div className="card card-glass">
            <div className="flex items-center gap-2 mb-2">
              <Zap size={24} style={{ color: '#f59e0b' }} />
              <h3>AI Recommendations</h3>
            </div>
            <p className="text-muted">
              Multi-agent AI synthesizes all data to provide clear 
              buy/sell/hold recommendations with confidence scores.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="container text-center mt-4 mb-3">
        <p className="text-muted">
          Powered by Multi-Agent AI • Data from NSE/BSE • Not financial advice
        </p>
      </footer>
    </main>
  );
}
