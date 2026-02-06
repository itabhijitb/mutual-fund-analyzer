# Mutual Fund Analyzer - Production-Ready Modular Version

A comprehensive, production-ready tool for analyzing mutual fund performance with industry-standard risk metrics.

## 🏗️ Architecture

The application follows a **modular, production-ready architecture** with clear separation of concerns:

```
mf_analyzer/
├── __init__.py           # Package initialization
├── config.py             # Configuration and constants
├── api_client.py         # API communication layer
├── calculator.py         # Risk metrics calculation engine
├── screener.py           # Fund screening and ranking logic
├── reports.py            # Report generation (HTML & console)
└── ui.py                 # User interface and interactions

mf_analyzer_main.py       # Main application entry point
requirements.txt          # Python dependencies
mf_analyzer.log          # Application logs (auto-generated)
```

## ✨ Key Features

### 🎯 Modular Design
- **Separation of Concerns**: Each module has a single, well-defined responsibility
- **Testable**: Easy to unit test individual components
- **Maintainable**: Changes to one module don't affect others
- **Extensible**: Easy to add new features or data sources

### 📊 Comprehensive Analysis
- **28 Fund Categories**: Equity, Sectoral, Thematic, Hybrid, Index, and more
- **Industry-Standard Metrics**: Sharpe, Sortino, Calmar ratios with monthly returns
- **3-Year Analysis Period**: Aligned with industry standards
- **Plan Type Filtering**: Growth, IDCW, or Both

### 🔍 Advanced Screening
- **Top 5 Fund Ranking**: Based on composite scoring algorithm
- **5-Year Performance**: Long-term investment analysis
- **Smart Filtering**: By category and plan type
- **Batch Analysis**: Analyze multiple funds simultaneously

### 📈 Professional Reporting
- **Tabbed HTML Reports**: Single file with multiple fund tabs
- **Individual Reports**: QuantStats-powered detailed analysis
- **Console Output**: Organized, categorized metrics display
- **NAV Charts**: Embedded performance visualizations

### 🛡️ Production Features
- **Logging**: Comprehensive logging to file and console
- **Error Handling**: Graceful error handling with user-friendly messages
- **Type Hints**: Full type annotations for better IDE support
- **Input Validation**: Robust validation of user inputs
- **Configuration Management**: Centralized configuration

## 🚀 Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Setup

1. **Clone or download the project**:
```bash
cd /Users/abhijit/scripts
```

2. **Create virtual environment**:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## 📖 Usage

### Running the Application

```bash
# Make the script executable
chmod +x mf_analyzer_main.py

# Run the application
python mf_analyzer_main.py
```

### Mode 1: Single Fund Analysis

Analyze a specific mutual fund in detail:

1. Choose **Mode 1**
2. Enter scheme code (e.g., `119551`) or fund name (e.g., `HDFC Flexi Cap`)
3. View comprehensive risk metrics
4. Optionally generate HTML report

**Example Output**:
```
📈 COMPREHENSIVE RISK ANALYSIS
======================================================================

🎯 PERFORMANCE METRICS:
  Total Return (%)..................................            75.6
  Annual Return (%).................................           21.64
  Cumulative Return (%).............................           79.99

⚖️  RISK-ADJUSTED RETURNS:
  Sharpe Ratio......................................             1.6
  Sortino Ratio.....................................            3.22
  Calmar Ratio......................................            3.74
```

### Mode 2: Fund Screener

Find and compare top-performing funds:

1. Choose **Mode 2**
2. Select **category** (1-28)
3. Select **plan type** (Growth/IDCW/Both)
4. View **top 5 ranked funds**
5. Choose **analysis depth** (1, 3, or 5 funds)
6. Select **report type** (Tabbed/Separate/None)

**Example Workflow**:
```
Category: Flexi Cap (5)
Plan Type: Growth only (1)
Analysis: Top 3 funds (2)
Report: Single tabbed report (1)
```

## 🔧 Configuration

Edit `mf_analyzer/config.py` to customize:

```python
# Analysis Configuration
DEFAULT_RISK_FREE_RATE = 0.07  # 7% (Indian 10-year G-Sec)
DEFAULT_ANALYSIS_PERIOD_YEARS = 3
DEFAULT_SCREENING_PERIOD_YEARS = 5
TOP_N_FUNDS = 5

# Scoring Weights for Fund Ranking
SCORING_WEIGHTS = {
    'sharpe_ratio': 0.4,
    'annual_return': 0.3,
    'sortino_ratio': 0.2,
    'calmar_ratio': 0.1
}
```

## 📊 Metrics Explained

### Performance Metrics
- **Total Return**: Overall return over the analysis period
- **Annual Return**: Annualized return (CAGR)
- **Cumulative Return**: Total cumulative return

### Risk-Adjusted Returns
- **Sharpe Ratio**: Return per unit of total risk (industry standard: monthly returns)
- **Sortino Ratio**: Return per unit of downside risk
- **Calmar Ratio**: Return per unit of maximum drawdown

### Risk Metrics
- **Max Drawdown**: Largest peak-to-trough decline
- **Value at Risk (95%)**: Maximum expected loss at 95% confidence
- **Conditional VaR**: Average loss beyond VaR threshold

### Volatility Metrics
- **Annual Volatility**: Annualized standard deviation
- **Monthly Volatility**: Monthly standard deviation
- **Downside Deviation**: Volatility of negative returns only

## 🏆 Fund Categories

### 📂 Equity Funds (7)
Large Cap, Mid Cap, Small Cap, Multi Cap, Flexi Cap, Large & Mid Cap, Focused

### 🏭 Sectoral Funds (6)
Banking, Technology, Pharma, Infrastructure, FMCG, Energy

### 🌱 Thematic Funds (2)
ESG, Dividend Yield

### 💰 Tax Saving & Hybrid (6)
ELSS, Balanced, Aggressive Hybrid, Conservative Hybrid, Equity Savings, Arbitrage

### 📈 Index Funds (3)
Nifty 50, Sensex, Nifty Next 50

### 🎯 Other Strategies (4)
Value, Contra, International, Custom Search

## 🔍 Module Details

### `api_client.py`
- **MFAPIClient**: Handles all API communications
- Methods: `fetch_nav_history()`, `search_mutual_funds()`
- Error handling for network issues and invalid codes

### `calculator.py`
- **RiskMetricsCalculator**: Calculates all risk and performance metrics
- Methods: `calculate_comprehensive_metrics()`, `calculate_screening_metrics()`
- Uses empyrical library for industry-standard calculations

### `screener.py`
- **FundScreener**: Screens and ranks funds
- Methods: `screen_and_rank()`, `filter_by_plan_type()`, `calculate_composite_score()`
- Implements weighted scoring algorithm

### `reports.py`
- **ReportGenerator**: Generates all types of reports
- Methods: `generate_quantstats_report()`, `generate_tabbed_report()`, `display_fund_comparison()`
- Creates beautiful HTML reports with embedded charts

### `ui.py`
- **ConsoleUI**: Handles all user interactions
- Methods: Display menus, get user inputs, show results
- Clean separation of UI from business logic

### `config.py`
- Centralized configuration
- Fund categories, scoring weights, constants
- Easy to modify without touching code

## 📝 Logging

Application logs are written to `mf_analyzer.log`:

```
2026-02-07 00:30:15 - mf_analyzer.api_client - INFO - Fetched 1234 NAV records for scheme 119551
2026-02-07 00:30:20 - mf_analyzer.calculator - INFO - Calculated metrics for period 2023-02-06 to 2026-02-05
2026-02-07 00:30:25 - mf_analyzer.reports - INFO - Generated tabbed report: mf_Flexi_Cap_comparison.html
```

## 🧪 Testing

The modular structure makes testing easy:

```python
# Example: Test calculator independently
from mf_analyzer.calculator import RiskMetricsCalculator
import pandas as pd

calculator = RiskMetricsCalculator(risk_free_rate=0.07)
nav_df = pd.DataFrame({
    'date': [...],
    'nav': [...]
})
metrics = calculator.calculate_comprehensive_metrics(nav_df)
assert metrics['Sharpe Ratio'] > 0
```

## 🔄 Migration from Old Version

The old `mf_anal.py` is preserved. The new modular version:

**Advantages**:
- ✅ Better code organization
- ✅ Easier to test and maintain
- ✅ Production-ready logging
- ✅ Configurable without code changes
- ✅ Type hints for better IDE support
- ✅ Proper error handling

**Usage**:
```bash
# Old version (still works)
python mf_anal.py

# New modular version (recommended)
python mf_analyzer_main.py
```

## 🐛 Troubleshooting

### Import Errors
```bash
# Ensure you're in the correct directory
cd /Users/abhijit/scripts

# Ensure virtual environment is activated
source .venv/bin/activate
```

### API Errors
- Check internet connection
- Verify scheme code is valid
- Check logs in `mf_analyzer.log`

### NumPy Version Issues
```bash
# Reinstall compatible NumPy version
pip install "numpy<2.0" --force-reinstall
```

## 📚 Data Source

All data is fetched from [mfapi.in](https://www.mfapi.in/), a free mutual fund data API for Indian mutual funds.

## 🤝 Contributing

To extend the application:

1. **Add new metrics**: Extend `RiskMetricsCalculator` in `calculator.py`
2. **Add new categories**: Update `FUND_CATEGORIES` in `config.py`
3. **Add new reports**: Extend `ReportGenerator` in `reports.py`
4. **Add new UI features**: Extend `ConsoleUI` in `ui.py`

## 📄 License

This tool is for educational and personal use.

## 🙏 Acknowledgments

- **mfapi.in**: Free mutual fund data API
- **QuantStats**: Comprehensive financial analysis library
- **Empyrical**: Risk and performance metrics library

---

**Version**: 2.0.0 (Modular Production Release)  
**Last Updated**: February 2026
