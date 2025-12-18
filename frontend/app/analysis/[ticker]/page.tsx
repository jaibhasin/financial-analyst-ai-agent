'use client';

import { useState, useEffect, use } from 'react';
import Link from 'next/link';
import {
    ArrowLeft, TrendingUp, TrendingDown, BarChart3,
    Target, AlertTriangle, CheckCircle, XCircle,
    Brain, Activity, PieChart, DollarSign
} from 'lucide-react';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
    ResponsiveContainer, AreaChart, Area, BarChart, Bar
} from 'recharts';

interface AnalysisData {
    ticker: string;
    name: string;
    market_data: any;
    fundamental_analysis: any;
    technical_analysis: any;
    recommendation: any;
    generated_at: string;
}

export default function AnalysisPage({ params }: { params: Promise<{ ticker: string }> }) {
    const { ticker } = use(params);
    const [data, setData] = useState<AnalysisData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [activeTab, setActiveTab] = useState('overview');

    useEffect(() => {
        fetchAnalysis();
    }, [ticker]);

    const fetchAnalysis = async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch(`http://localhost:8000/analyze/${ticker}`);
            if (!response.ok) {
                throw new Error('Failed to fetch analysis');
            }
            const result = await response.json();
            setData(result);
        } catch (err) {
            setError('Unable to fetch analysis. Make sure the backend server is running.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <main>
                <nav className="navbar">
                    <div className="container navbar-content">
                        <Link href="/" className="logo">
                            <Brain size={32} />
                            AI Financial Analyst
                        </Link>
                    </div>
                </nav>
                <div className="loading">
                    <div className="spinner" />
                    <p className="loading-text">Analyzing {ticker}...</p>
                    <p className="text-muted">Our AI agents are working on it</p>
                </div>
            </main>
        );
    }

    if (error || !data) {
        return (
            <main>
                <nav className="navbar">
                    <div className="container navbar-content">
                        <Link href="/" className="logo">
                            <Brain size={32} />
                            AI Financial Analyst
                        </Link>
                    </div>
                </nav>
                <div className="container mt-4">
                    <div className="card text-center">
                        <AlertTriangle size={48} className="text-warning mb-2" />
                        <h2>Unable to Load Analysis</h2>
                        <p className="text-muted mt-1">{error}</p>
                        <div className="mt-3">
                            <Link href="/" className="btn btn-secondary">
                                <ArrowLeft size={18} /> Back to Search
                            </Link>
                        </div>
                    </div>
                </div>
            </main>
        );
    }

    const marketData = data.market_data?.data || {};
    const priceData = marketData.price_data || {};
    const fundamentals = data.fundamental_analysis?.data || {};
    const technicals = data.technical_analysis?.data || {};
    const recommendation = data.recommendation?.data || {};
    const insight = data.recommendation?.insight || '';

    const currentPrice = priceData.current_price || 0;
    const previousClose = priceData.previous_close || 0;
    const priceChange = currentPrice - previousClose;
    const priceChangePercent = previousClose ? ((priceChange / previousClose) * 100) : 0;
    const isPositive = priceChange >= 0;

    // Prepare chart data
    const chartData = marketData.historical_prices?.slice(-60) || [];

    return (
        <main>
            {/* Navigation */}
            <nav className="navbar">
                <div className="container navbar-content">
                    <Link href="/" className="logo">
                        <Brain size={32} />
                        AI Financial Analyst
                    </Link>
                    <Link href="/" className="btn btn-secondary">
                        <ArrowLeft size={18} /> New Search
                    </Link>
                </div>
            </nav>

            <div className="container mt-3">
                {/* Stock Header */}
                <div className="flex justify-between items-center" style={{ flexWrap: 'wrap', gap: '1rem' }}>
                    <div>
                        <div className="flex items-center gap-2">
                            <h1>{ticker}</h1>
                            <span className="badge badge-neutral">NSE</span>
                        </div>
                        <p className="text-muted">{data.name}</p>
                    </div>
                    <div className="price-display">
                        <span className="price-current">₹{currentPrice.toLocaleString('en-IN', { maximumFractionDigits: 2 })}</span>
                        <span className={`price-change ${isPositive ? 'positive' : 'negative'}`}>
                            {isPositive ? <TrendingUp size={20} /> : <TrendingDown size={20} />}
                            {isPositive ? '+' : ''}{priceChange.toFixed(2)} ({priceChangePercent.toFixed(2)}%)
                        </span>
                    </div>
                </div>

                {/* Tabs */}
                <div className="tabs mt-3">
                    <button
                        className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
                        onClick={() => setActiveTab('overview')}
                    >
                        Overview
                    </button>
                    <button
                        className={`tab ${activeTab === 'fundamental' ? 'active' : ''}`}
                        onClick={() => setActiveTab('fundamental')}
                    >
                        Fundamental
                    </button>
                    <button
                        className={`tab ${activeTab === 'technical' ? 'active' : ''}`}
                        onClick={() => setActiveTab('technical')}
                    >
                        Technical
                    </button>
                </div>

                {/* Content */}
                {activeTab === 'overview' && (
                    <div className="analysis-grid">
                        {/* Recommendation Card */}
                        <div className="recommendation-card">
                            <p style={{ opacity: 0.8, fontSize: '0.875rem' }}>AI RECOMMENDATION</p>
                            <p className="recommendation-action">{recommendation.recommendation?.action || 'ANALYZING'}</p>
                            <div className="recommendation-score">{recommendation.scores?.overall_score || '--'}</div>
                            <p className="recommendation-label">Overall Score / 100</p>
                            <div className="mt-2" style={{ display: 'flex', justifyContent: 'center', gap: '1rem' }}>
                                <div>
                                    <p style={{ fontSize: '1.5rem', fontWeight: 600 }}>{recommendation.scores?.fundamental_score || '--'}</p>
                                    <p style={{ fontSize: '0.75rem', opacity: 0.8 }}>Fundamental</p>
                                </div>
                                <div>
                                    <p style={{ fontSize: '1.5rem', fontWeight: 600 }}>{recommendation.scores?.technical_score || '--'}</p>
                                    <p style={{ fontSize: '0.75rem', opacity: 0.8 }}>Technical</p>
                                </div>
                            </div>
                        </div>

                        {/* Price Chart */}
                        <div className="card">
                            <h4 className="mb-2">Price History (60 Days)</h4>
                            <div className="chart-container">
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={chartData}>
                                        <defs>
                                            <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                                                <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                                        <XAxis
                                            dataKey="date"
                                            stroke="#666"
                                            tick={{ fontSize: 10 }}
                                            tickFormatter={(val) => val.slice(5)}
                                        />
                                        <YAxis
                                            stroke="#666"
                                            tick={{ fontSize: 10 }}
                                            domain={['auto', 'auto']}
                                        />
                                        <Tooltip
                                            contentStyle={{
                                                backgroundColor: '#1a1a24',
                                                border: '1px solid #333',
                                                borderRadius: '8px'
                                            }}
                                        />
                                        <Area
                                            type="monotone"
                                            dataKey="close"
                                            stroke="#6366f1"
                                            fill="url(#colorPrice)"
                                            strokeWidth={2}
                                        />
                                    </AreaChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        {/* Target Price */}
                        <div className="card">
                            <div className="flex items-center gap-2 mb-2">
                                <Target size={20} style={{ color: '#8b5cf6' }} />
                                <h4>Target Price</h4>
                            </div>
                            <div className="metrics-grid">
                                <div className="metric-item">
                                    <p className="metric-label">Low Target</p>
                                    <p className="metric-value text-danger">₹{recommendation.target_price?.low?.toLocaleString() || '--'}</p>
                                </div>
                                <div className="metric-item">
                                    <p className="metric-label">High Target</p>
                                    <p className="metric-value text-success">₹{recommendation.target_price?.high?.toLocaleString() || '--'}</p>
                                </div>
                                <div className="metric-item">
                                    <p className="metric-label">Upside</p>
                                    <p className="metric-value">{recommendation.target_price?.upside_percent || 0}%</p>
                                </div>
                                <div className="metric-item">
                                    <p className="metric-label">Risk Level</p>
                                    <p className={`metric-value ${recommendation.risk_assessment?.level === 'Low' ? 'text-success' :
                                            recommendation.risk_assessment?.level === 'Moderate' ? 'text-warning' : 'text-danger'
                                        }`}>{recommendation.risk_assessment?.level || '--'}</p>
                                </div>
                            </div>
                        </div>

                        {/* Key Factors */}
                        <div className="card">
                            <h4 className="mb-2">Key Factors</h4>
                            <div className="flex flex-col gap-2">
                                <div>
                                    <p className="text-muted mb-1" style={{ fontSize: '0.75rem' }}>BULLISH FACTORS</p>
                                    <ul className="signal-list">
                                        {(recommendation.key_factors?.bullish || []).slice(0, 3).map((factor: string, i: number) => (
                                            <li key={i} className="signal-item bullish">
                                                <CheckCircle size={14} /> {factor}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                                <div className="mt-2">
                                    <p className="text-muted mb-1" style={{ fontSize: '0.75rem' }}>BEARISH FACTORS</p>
                                    <ul className="signal-list">
                                        {(recommendation.key_factors?.bearish || []).slice(0, 3).map((factor: string, i: number) => (
                                            <li key={i} className="signal-item bearish">
                                                <XCircle size={14} /> {factor}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        </div>

                        {/* AI Insight */}
                        <div className="card" style={{ gridColumn: '1 / -1' }}>
                            <div className="flex items-center gap-2 mb-2">
                                <Brain size={20} style={{ color: '#6366f1' }} />
                                <h4>AI Analysis</h4>
                            </div>
                            <p className="text-muted" style={{ whiteSpace: 'pre-line', lineHeight: 1.8 }}>
                                {insight || 'Analysis not available'}
                            </p>
                        </div>
                    </div>
                )}

                {activeTab === 'fundamental' && (
                    <div className="analysis-grid">
                        {/* Profitability */}
                        <div className="card">
                            <div className="flex items-center gap-2 mb-2">
                                <DollarSign size={20} style={{ color: '#22c55e' }} />
                                <h4>Profitability</h4>
                                <span className={`badge ${fundamentals.profitability?.assessment === 'Strong' ? 'badge-success' :
                                        fundamentals.profitability?.assessment === 'Good' ? 'badge-success' :
                                            fundamentals.profitability?.assessment === 'Moderate' ? 'badge-warning' : 'badge-danger'
                                    }`}>{fundamentals.profitability?.assessment}</span>
                            </div>
                            <div className="metrics-grid">
                                <div className="metric-item">
                                    <p className="metric-label">ROE</p>
                                    <p className="metric-value">{fundamentals.profitability?.roe?.toFixed(1) || '--'}%</p>
                                </div>
                                <div className="metric-item">
                                    <p className="metric-label">ROA</p>
                                    <p className="metric-value">{fundamentals.profitability?.roa?.toFixed(1) || '--'}%</p>
                                </div>
                                <div className="metric-item">
                                    <p className="metric-label">Profit Margin</p>
                                    <p className="metric-value">{fundamentals.profitability?.profit_margin?.toFixed(1) || '--'}%</p>
                                </div>
                                <div className="metric-item">
                                    <p className="metric-label">Operating Margin</p>
                                    <p className="metric-value">{fundamentals.profitability?.operating_margin?.toFixed(1) || '--'}%</p>
                                </div>
                            </div>
                        </div>

                        {/* Valuation */}
                        <div className="card">
                            <div className="flex items-center gap-2 mb-2">
                                <PieChart size={20} style={{ color: '#8b5cf6' }} />
                                <h4>Valuation</h4>
                                <span className={`badge ${fundamentals.valuation?.assessment?.includes('Undervalued') ? 'badge-success' :
                                        fundamentals.valuation?.assessment?.includes('Attractive') ? 'badge-success' :
                                            fundamentals.valuation?.assessment?.includes('Fair') ? 'badge-neutral' : 'badge-warning'
                                    }`}>{fundamentals.valuation?.assessment}</span>
                            </div>
                            <div className="metrics-grid">
                                <div className="metric-item">
                                    <p className="metric-label">P/E Ratio</p>
                                    <p className="metric-value">{fundamentals.valuation?.pe_ratio || '--'}</p>
                                </div>
                                <div className="metric-item">
                                    <p className="metric-label">P/B Ratio</p>
                                    <p className="metric-value">{fundamentals.valuation?.pb_ratio || '--'}</p>
                                </div>
                                <div className="metric-item">
                                    <p className="metric-label">EV/EBITDA</p>
                                    <p className="metric-value">{fundamentals.valuation?.ev_ebitda || '--'}</p>
                                </div>
                                <div className="metric-item">
                                    <p className="metric-label">PEG Ratio</p>
                                    <p className="metric-value">{fundamentals.valuation?.peg_ratio || '--'}</p>
                                </div>
                            </div>
                        </div>

                        {/* Financial Health */}
                        <div className="card">
                            <div className="flex items-center gap-2 mb-2">
                                <Activity size={20} style={{ color: '#f59e0b' }} />
                                <h4>Financial Health</h4>
                                <span className={`badge ${fundamentals.financial_health?.assessment === 'Strong' ? 'badge-success' :
                                        fundamentals.financial_health?.assessment === 'Healthy' ? 'badge-success' :
                                            fundamentals.financial_health?.assessment === 'Moderate' ? 'badge-warning' : 'badge-danger'
                                    }`}>{fundamentals.financial_health?.assessment}</span>
                            </div>
                            <div className="metrics-grid">
                                <div className="metric-item">
                                    <p className="metric-label">Current Ratio</p>
                                    <p className="metric-value">{fundamentals.financial_health?.current_ratio || '--'}</p>
                                </div>
                                <div className="metric-item">
                                    <p className="metric-label">Quick Ratio</p>
                                    <p className="metric-value">{fundamentals.financial_health?.quick_ratio || '--'}</p>
                                </div>
                                <div className="metric-item">
                                    <p className="metric-label">Debt/Equity</p>
                                    <p className="metric-value">{fundamentals.financial_health?.debt_to_equity || '--'}</p>
                                </div>
                                <div className="metric-item">
                                    <p className="metric-label">Net Debt</p>
                                    <p className="metric-value">
                                        {fundamentals.financial_health?.net_debt
                                            ? `₹${(fundamentals.financial_health.net_debt / 10000000).toFixed(0)} Cr`
                                            : '--'}
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Growth */}
                        <div className="card">
                            <div className="flex items-center gap-2 mb-2">
                                <TrendingUp size={20} style={{ color: '#22c55e' }} />
                                <h4>Growth</h4>
                                <span className={`badge ${fundamentals.growth?.assessment?.includes('High') ? 'badge-success' :
                                        fundamentals.growth?.assessment?.includes('Moderate') ? 'badge-warning' : 'badge-danger'
                                    }`}>{fundamentals.growth?.assessment}</span>
                            </div>
                            <div className="metrics-grid">
                                <div className="metric-item">
                                    <p className="metric-label">Revenue Growth</p>
                                    <p className={`metric-value ${(fundamentals.growth?.revenue_growth || 0) > 0 ? 'text-success' : 'text-danger'}`}>
                                        {fundamentals.growth?.revenue_growth?.toFixed(1) || '--'}%
                                    </p>
                                </div>
                                <div className="metric-item">
                                    <p className="metric-label">Earnings Growth</p>
                                    <p className={`metric-value ${(fundamentals.growth?.earnings_growth || 0) > 0 ? 'text-success' : 'text-danger'}`}>
                                        {fundamentals.growth?.earnings_growth?.toFixed(1) || '--'}%
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Fundamental Insight */}
                        <div className="card" style={{ gridColumn: '1 / -1' }}>
                            <div className="flex items-center gap-2 mb-2">
                                <Brain size={20} style={{ color: '#6366f1' }} />
                                <h4>Fundamental Analysis Insight</h4>
                            </div>
                            <p className="text-muted" style={{ whiteSpace: 'pre-line', lineHeight: 1.8 }}>
                                {data.fundamental_analysis?.insight || 'Analysis not available'}
                            </p>
                        </div>
                    </div>
                )}

                {activeTab === 'technical' && (
                    <div className="analysis-grid">
                        {/* Trend */}
                        <div className="card">
                            <div className="flex items-center gap-2 mb-2">
                                <TrendingUp size={20} style={{ color: '#6366f1' }} />
                                <h4>Trend Analysis</h4>
                                <span className={`badge ${technicals.trend?.overall_trend?.includes('Bullish') ? 'badge-success' :
                                        technicals.trend?.overall_trend === 'Neutral' ? 'badge-neutral' : 'badge-danger'
                                    }`}>{technicals.trend?.overall_trend}</span>
                            </div>
                            <div className="metrics-grid">
                                <div className="metric-item">
                                    <p className="metric-label">Short Term</p>
                                    <p className={`metric-value ${technicals.trend?.short_term?.direction === 'Bullish' ? 'text-success' : 'text-danger'}`}>
                                        {technicals.trend?.short_term?.direction} ({technicals.trend?.short_term?.change_pct}%)
                                    </p>
                                </div>
                                <div className="metric-item">
                                    <p className="metric-label">Medium Term</p>
                                    <p className={`metric-value ${technicals.trend?.medium_term?.direction === 'Bullish' ? 'text-success' : 'text-danger'}`}>
                                        {technicals.trend?.medium_term?.direction}
                                    </p>
                                </div>
                                <div className="metric-item">
                                    <p className="metric-label">Long Term</p>
                                    <p className={`metric-value ${technicals.trend?.long_term?.direction === 'Bullish' ? 'text-success' : 'text-danger'}`}>
                                        {technicals.trend?.long_term?.direction}
                                    </p>
                                </div>
                                <div className="metric-item">
                                    <p className="metric-label">Trend Strength</p>
                                    <p className="metric-value">{technicals.trend?.trend_strength || '--'}/3</p>
                                </div>
                            </div>
                        </div>

                        {/* Indicators */}
                        <div className="card">
                            <div className="flex items-center gap-2 mb-2">
                                <BarChart3 size={20} style={{ color: '#8b5cf6' }} />
                                <h4>Key Indicators</h4>
                            </div>
                            <div className="metrics-grid">
                                <div className="metric-item">
                                    <p className="metric-label">RSI (14)</p>
                                    <p className={`metric-value ${technicals.indicators?.rsi?.condition === 'Oversold' ? 'text-success' :
                                            technicals.indicators?.rsi?.condition === 'Overbought' ? 'text-danger' : ''
                                        }`}>
                                        {technicals.indicators?.rsi?.current || '--'} ({technicals.indicators?.rsi?.condition})
                                    </p>
                                </div>
                                <div className="metric-item">
                                    <p className="metric-label">MACD</p>
                                    <p className={`metric-value ${technicals.indicators?.macd?.signal_type?.includes('Bullish') ? 'text-success' : 'text-danger'
                                        }`}>
                                        {technicals.indicators?.macd?.signal_type}
                                    </p>
                                </div>
                                <div className="metric-item">
                                    <p className="metric-label">Stochastic</p>
                                    <p className="metric-value">{technicals.indicators?.stochastic?.condition}</p>
                                </div>
                                <div className="metric-item">
                                    <p className="metric-label">Volatility</p>
                                    <p className="metric-value">{technicals.indicators?.atr?.volatility}</p>
                                </div>
                            </div>
                        </div>

                        {/* Moving Averages */}
                        <div className="card">
                            <h4 className="mb-2">Moving Averages</h4>
                            <div className="metrics-grid">
                                <div className="metric-item">
                                    <p className="metric-label">SMA 20</p>
                                    <p className="metric-value">
                                        ₹{technicals.indicators?.moving_averages?.sma_20?.toLocaleString() || '--'}
                                        <span className={`badge ml-1 ${technicals.indicators?.moving_averages?.price_vs_20sma === 'Above' ? 'badge-success' : 'badge-danger'}`}>
                                            {technicals.indicators?.moving_averages?.price_vs_20sma}
                                        </span>
                                    </p>
                                </div>
                                <div className="metric-item">
                                    <p className="metric-label">SMA 50</p>
                                    <p className="metric-value">
                                        ₹{technicals.indicators?.moving_averages?.sma_50?.toLocaleString() || '--'}
                                        <span className={`badge ml-1 ${technicals.indicators?.moving_averages?.price_vs_50sma === 'Above' ? 'badge-success' : 'badge-danger'}`}>
                                            {technicals.indicators?.moving_averages?.price_vs_50sma}
                                        </span>
                                    </p>
                                </div>
                                <div className="metric-item">
                                    <p className="metric-label">SMA 200</p>
                                    <p className="metric-value">
                                        ₹{technicals.indicators?.moving_averages?.sma_200?.toLocaleString() || '--'}
                                        <span className={`badge ml-1 ${technicals.indicators?.moving_averages?.price_vs_200sma === 'Above' ? 'badge-success' : 'badge-danger'}`}>
                                            {technicals.indicators?.moving_averages?.price_vs_200sma}
                                        </span>
                                    </p>
                                </div>
                                <div className="metric-item">
                                    <p className="metric-label">Bollinger Position</p>
                                    <p className="metric-value">{technicals.indicators?.bollinger_bands?.position}</p>
                                </div>
                            </div>
                        </div>

                        {/* Support/Resistance */}
                        <div className="card">
                            <h4 className="mb-2">Support & Resistance</h4>
                            <div className="metrics-grid">
                                <div className="metric-item">
                                    <p className="metric-label">Nearest Resistance</p>
                                    <p className="metric-value text-danger">₹{technicals.support_resistance?.nearest_resistance?.toLocaleString() || '--'}</p>
                                </div>
                                <div className="metric-item">
                                    <p className="metric-label">Nearest Support</p>
                                    <p className="metric-value text-success">₹{technicals.support_resistance?.nearest_support?.toLocaleString() || '--'}</p>
                                </div>
                                <div className="metric-item">
                                    <p className="metric-label">Pivot Point</p>
                                    <p className="metric-value">₹{technicals.support_resistance?.pivot_point?.toLocaleString() || '--'}</p>
                                </div>
                                <div className="metric-item">
                                    <p className="metric-label">Volume Trend</p>
                                    <p className="metric-value">{technicals.volume?.volume_trend}</p>
                                </div>
                            </div>
                        </div>

                        {/* Signals */}
                        <div className="card">
                            <h4 className="mb-2">Trading Signals</h4>
                            <div className="flex gap-3" style={{ flexWrap: 'wrap' }}>
                                <div style={{ flex: 1, minWidth: '200px' }}>
                                    <p className="text-muted mb-1" style={{ fontSize: '0.75rem' }}>BULLISH SIGNALS</p>
                                    <ul className="signal-list">
                                        {(technicals.signals?.bullish_signals || []).map((signal: string, i: number) => (
                                            <li key={i} className="signal-item bullish">
                                                <CheckCircle size={14} /> {signal}
                                            </li>
                                        ))}
                                        {(!technicals.signals?.bullish_signals?.length) && (
                                            <li className="signal-item">No bullish signals</li>
                                        )}
                                    </ul>
                                </div>
                                <div style={{ flex: 1, minWidth: '200px' }}>
                                    <p className="text-muted mb-1" style={{ fontSize: '0.75rem' }}>BEARISH SIGNALS</p>
                                    <ul className="signal-list">
                                        {(technicals.signals?.bearish_signals || []).map((signal: string, i: number) => (
                                            <li key={i} className="signal-item bearish">
                                                <XCircle size={14} /> {signal}
                                            </li>
                                        ))}
                                        {(!technicals.signals?.bearish_signals?.length) && (
                                            <li className="signal-item">No bearish signals</li>
                                        )}
                                    </ul>
                                </div>
                            </div>
                        </div>

                        {/* Volume */}
                        <div className="card">
                            <h4 className="mb-2">Volume Analysis</h4>
                            <div className="metrics-grid">
                                <div className="metric-item">
                                    <p className="metric-label">Current Volume</p>
                                    <p className="metric-value">{(technicals.volume?.current_volume / 1000000)?.toFixed(2)}M</p>
                                </div>
                                <div className="metric-item">
                                    <p className="metric-label">Avg Volume (20D)</p>
                                    <p className="metric-value">{(technicals.volume?.avg_volume_20 / 1000000)?.toFixed(2)}M</p>
                                </div>
                                <div className="metric-item">
                                    <p className="metric-label">Volume Ratio</p>
                                    <p className={`metric-value ${technicals.volume?.volume_ratio > 1 ? 'text-success' : 'text-danger'}`}>
                                        {technicals.volume?.volume_ratio}x
                                    </p>
                                </div>
                                <div className="metric-item">
                                    <p className="metric-label">Price-Volume Signal</p>
                                    <p className="metric-value">{technicals.volume?.price_volume_signal}</p>
                                </div>
                            </div>
                        </div>

                        {/* Technical Insight */}
                        <div className="card" style={{ gridColumn: '1 / -1' }}>
                            <div className="flex items-center gap-2 mb-2">
                                <Brain size={20} style={{ color: '#6366f1' }} />
                                <h4>Technical Analysis Insight</h4>
                            </div>
                            <p className="text-muted" style={{ whiteSpace: 'pre-line', lineHeight: 1.8 }}>
                                {data.technical_analysis?.insight || 'Analysis not available'}
                            </p>
                        </div>
                    </div>
                )}

                {/* Footer */}
                <footer className="text-center mt-4 mb-3">
                    <p className="text-muted">
                        Analysis generated at {new Date(data.generated_at).toLocaleString()} • Not financial advice
                    </p>
                </footer>
            </div>
        </main>
    );
}
