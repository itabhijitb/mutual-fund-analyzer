"""
Configuration settings for Mutual Fund Analyzer
"""

# API Configuration
API_BASE_URL = "https://api.mfapi.in/mf"
API_TIMEOUT = 30  # seconds

# Analysis Configuration
DEFAULT_RISK_FREE_RATE = 0.07  # 7% (Indian 10-year G-Sec rate)
DEFAULT_ANALYSIS_PERIOD_YEARS = None  # None = use entire NAV history for better accuracy
DEFAULT_SCREENING_PERIOD_YEARS = 5
TOP_N_FUNDS = 5

# Scoring Weights for Fund Ranking
SCORING_WEIGHTS = {
    'sharpe_ratio': 0.4,
    'annual_return': 0.3,
    'sortino_ratio': 0.2,
    'calmar_ratio': 0.1
}

# Minimum data requirements
MIN_MONTHS_PER_YEAR = 10  # Minimum months of data required per year of analysis

# Fund Categories
FUND_CATEGORIES = {
    '1': {'name': 'Large Cap / Bluechip', 'search': 'Large Cap'},
    '2': {'name': 'Mid Cap', 'search': 'Mid Cap'},
    '3': {'name': 'Small Cap', 'search': 'Small Cap'},
    '4': {'name': 'Multi Cap', 'search': 'Multi Cap'},
    '5': {'name': 'Flexi Cap', 'search': 'Flexi Cap'},
    '6': {'name': 'Large & Mid Cap', 'search': 'Large and Mid Cap'},
    '7': {'name': 'Focused Fund', 'search': 'Focused'},
    '8': {'name': 'Sectoral - Banking', 'search': 'Banking'},
    '9': {'name': 'Sectoral - Technology', 'search': 'Technology'},
    '10': {'name': 'Sectoral - Pharma', 'search': 'Pharma'},
    '11': {'name': 'Sectoral - Infrastructure', 'search': 'Infrastructure'},
    '12': {'name': 'Sectoral - FMCG', 'search': 'FMCG'},
    '13': {'name': 'Sectoral - Energy', 'search': 'Energy'},
    '14': {'name': 'Thematic - ESG', 'search': 'ESG'},
    '15': {'name': 'Thematic - Dividend Yield', 'search': 'Dividend'},
    '16': {'name': 'ELSS / Tax Saver', 'search': 'ELSS'},
    '17': {'name': 'Balanced / Hybrid Equity', 'search': 'Balanced'},
    '18': {'name': 'Aggressive Hybrid', 'search': 'Aggressive Hybrid'},
    '19': {'name': 'Conservative Hybrid', 'search': 'Conservative Hybrid'},
    '20': {'name': 'Equity Savings', 'search': 'Equity Savings'},
    '21': {'name': 'Multi Asset Allocation', 'search': 'Multi Asset'},
    '22': {'name': 'Arbitrage Fund', 'search': 'Arbitrage'},
    '23': {'name': 'Index Fund - Nifty 50', 'search': 'Nifty 50'},
    '24': {'name': 'Index Fund - Sensex', 'search': 'Sensex'},
    '25': {'name': 'Index Fund - Nifty Next 50', 'search': 'Nifty Next 50'},
    '26': {'name': 'Value Fund', 'search': 'Value'},
    '27': {'name': 'Contra Fund', 'search': 'Contra'},
    '28': {'name': 'International / Global', 'search': 'International'},
    '29': {'name': 'Custom Search', 'search': None}
}

# Plan Types
PLAN_TYPES = {
    'growth': ['growth'],
    'idcw': ['idcw', 'dividend'],
    'both': []
}
