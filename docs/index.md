# Mutual Fund Analyzer

> 🚀 Production-ready mutual fund analysis tool with industry-standard risk metrics, fund screening, and beautiful HTML reports

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-modular-brightgreen.svg)](https://github.com/adityabhattacharjee/mutual-fund-analyzer)

## 🌟 Features

- **29 Fund Categories**: Equity, Sectoral, Thematic, Hybrid, Multi Asset, Index funds
- **Industry-Standard Metrics**: Sharpe, Sortino, Calmar ratios with monthly returns
- **Smart Fund Screener**: Find top 5 performers with composite scoring
- **Plan Type Filtering**: Growth, IDCW (Dividend), or Both
- **Beautiful Reports**: Tabbed HTML reports with embedded charts
- **Production-Ready**: Modular architecture, logging, error handling

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/adityabhattacharjee/mutual-fund-analyzer.git
cd mutual-fund-analyzer

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Usage

**Run the modular version (recommended)**:
```bash
python mf_analyzer_main.py
```

**Or run the legacy version**:
```bash
python mf_anal.py
```

## 📊 Example: Find Top Flexi Cap Funds

```bash
$ python mf_analyzer_main.py

Choose analysis mode:
  1. Analyze a single fund
  2. Find top 5 funds (screener)

Enter your choice: 2
Select category: 5 (Flexi Cap)
Select plan type: 1 (Growth only)
```

**Output**:
```
🏆 TOP 5 FUNDS FOR 5-YEAR INVESTMENT

Rank  Fund Name                                    Return    Sharpe   Sortino
🥇    Parag Parikh Flexi Cap Fund - Direct         19.27%    1.13     1.94
🥈    Parag Parikh Flexi Cap Fund - Regular        18.30%    1.05     1.76
🥉    Bank of India Flexi Cap Direct               20.83%    0.85     1.42
```

## 📈 Key Metrics Explained

### Risk-Adjusted Returns
- **Sharpe Ratio**: Return per unit of total risk (>1 is good, >2 is excellent)
- **Sortino Ratio**: Return per unit of downside risk (focuses on negative volatility)
- **Calmar Ratio**: Return per unit of maximum drawdown

### Risk Metrics
- **Max Drawdown**: Largest peak-to-trough decline
- **Value at Risk (95%)**: Maximum expected loss at 95% confidence
- **Volatility**: Standard deviation of returns (annualized)

## 🏗️ Architecture

```
mf_analyzer/
├── api_client.py      # API communication
├── calculator.py      # Risk metrics calculation
├── screener.py        # Fund screening & ranking
├── reports.py         # HTML & console reports
├── ui.py              # User interface
└── config.py          # Configuration
```

## 📚 Documentation

- [Getting Started](getting-started.md)
- [User Guide](user-guide.md)
- [API Reference](api-reference.md)
- [Configuration](configuration.md)
- [Contributing](contributing.md)

## 🎯 Fund Categories

### Equity Funds
Large Cap, Mid Cap, Small Cap, Multi Cap, Flexi Cap, Large & Mid Cap, Focused

### Sectoral Funds
Banking, Technology, Pharma, Infrastructure, FMCG, Energy

### Thematic Funds
ESG, Dividend Yield

### Tax Saving & Hybrid
ELSS, Balanced, Aggressive Hybrid, Conservative Hybrid, Equity Savings, Multi Asset Allocation, Arbitrage

### Index Funds
Nifty 50, Sensex, Nifty Next 50

### Other Strategies
Value, Contra, International

## 🔧 Configuration

Edit `mf_analyzer/config.py`:

```python
DEFAULT_RISK_FREE_RATE = 0.07  # 7% (Indian G-Sec)
DEFAULT_ANALYSIS_PERIOD_YEARS = 3
DEFAULT_SCREENING_PERIOD_YEARS = 5

SCORING_WEIGHTS = {
    'sharpe_ratio': 0.4,
    'annual_return': 0.3,
    'sortino_ratio': 0.2,
    'calmar_ratio': 0.1
}
```

## 📊 Sample Reports

### Console Output
![Console Output](images/console-output.png)

### Tabbed HTML Report
![HTML Report](images/html-report.png)

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](contributing.md) for details.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- [mfapi.in](https://www.mfapi.in/) - Free mutual fund data API
- [QuantStats](https://github.com/ranaroussi/quantstats) - Financial analysis library
- [Empyrical](https://github.com/quantopian/empyrical) - Risk metrics library

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/adityabhattacharjee/mutual-fund-analyzer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/adityabhattacharjee/mutual-fund-analyzer/discussions)

---

**Made with ❤️ for Indian mutual fund investors**
