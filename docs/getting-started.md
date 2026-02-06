# Getting Started

This guide will help you get up and running with the Mutual Fund Analyzer.

## Prerequisites

- Python 3.9 or higher
- pip package manager
- Internet connection (for fetching fund data)

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/adityabhattacharjee/mutual-fund-analyzer.git
cd mutual-fund-analyzer
```

### Step 2: Create Virtual Environment

**On macOS/Linux**:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**On Windows**:
```bash
python -m venv .venv
.venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## First Run

### Mode 1: Analyze a Single Fund

```bash
python mf_analyzer_main.py
```

1. Choose **Mode 1**
2. Enter a scheme code (e.g., `119551`) or fund name (e.g., `HDFC Flexi Cap`)
3. View comprehensive metrics
4. Optionally generate HTML report

**Example**:
```
Enter Mutual Fund Scheme Code or Name: 119551

⏳ Calculating comprehensive risk metrics...

📈 COMPREHENSIVE RISK ANALYSIS
======================================================================

🎯 PERFORMANCE METRICS:
  Total Return (%)..................................            75.6
  Annual Return (%).................................           21.64
  Sharpe Ratio......................................             1.6
```

### Mode 2: Fund Screener

```bash
python mf_analyzer_main.py
```

1. Choose **Mode 2**
2. Select category (e.g., **5** for Flexi Cap)
3. Select plan type (e.g., **1** for Growth only)
4. View top 5 ranked funds
5. Choose how many to analyze in detail (1, 3, or 5)
6. Select report type (Tabbed/Separate/None)

**Example**:
```
Select category number (1-28): 5
✅ Selected: Flexi Cap

Select plan type (1-3): 1
✅ Filter: Growth plans only

🔍 Searching for 'Flexi Cap' funds...
✅ Found 8 funds (filtered from 15 by GROWTH plan type)

🏆 TOP 5 FUNDS FOR 5-YEAR INVESTMENT
```

## Understanding the Output

### Performance Metrics
- **Total Return**: Overall return over the analysis period
- **Annual Return**: Annualized return (CAGR)
- **Cumulative Return**: Total cumulative return

### Risk-Adjusted Returns
- **Sharpe Ratio**: Higher is better (>1 good, >2 excellent)
- **Sortino Ratio**: Similar to Sharpe but focuses on downside risk
- **Calmar Ratio**: Return relative to maximum drawdown

### Risk Metrics
- **Max Drawdown**: Largest peak-to-trough decline (lower is better)
- **Value at Risk**: Expected maximum loss at 95% confidence
- **Volatility**: Measure of price fluctuation

## HTML Reports

### Single Tabbed Report
All analyzed funds in one file with clickable tabs:

```
mf_Flexi_Cap_comparison.html
```

**Features**:
- Comparison table of all funds
- Individual tabs for each fund
- Embedded NAV charts
- Comprehensive metrics
- Beautiful, responsive design

### Separate Reports
One QuantStats report per fund:

```
mf_report_119551.html
mf_report_122639.html
```

**Features**:
- Interactive charts
- Detailed statistics
- Drawdown analysis
- Rolling metrics

## Next Steps

- [User Guide](user-guide.md) - Detailed usage instructions
- [Configuration](configuration.md) - Customize settings
- [API Reference](api-reference.md) - Module documentation

## Troubleshooting

### Import Errors
```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### NumPy Version Issues
```bash
pip install "numpy<2.0" --force-reinstall
```

### API Connection Issues
- Check internet connection
- Verify scheme code is valid
- Check logs in `mf_analyzer.log`

## Getting Help

- [GitHub Issues](https://github.com/adityabhattacharjee/mutual-fund-analyzer/issues)
- [Documentation](index.md)
- Check `mf_analyzer.log` for detailed error messages
