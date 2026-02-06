# Mutual Fund Risk Analysis Tool

A comprehensive Python tool for analyzing mutual fund risk metrics using professional-grade financial libraries.

## Features

### 🔍 Search & Analysis
- Search mutual funds by name or use scheme codes directly
- Fetch historical NAV data from mfapi.in
- Calculate 20+ professional risk metrics

### 📊 Risk Metrics Calculated

#### Performance Metrics
- **Total Return (%)** - Overall return from start to end
- **Annual Return (%)** - Annualized return rate
- **Cumulative Return (%)** - Total cumulative return

#### Volatility Metrics
- **Annual Volatility (%)** - Annualized standard deviation
- **Daily Volatility (%)** - Daily standard deviation
- **Downside Deviation (%)** - Volatility of negative returns only

#### Risk-Adjusted Returns
- **Sharpe Ratio** - Return per unit of total risk
- **Sortino Ratio** - Return per unit of downside risk
- **Calmar Ratio** - Return relative to maximum drawdown

#### Risk Metrics
- **Max Drawdown (%)** - Largest peak-to-trough decline
- **Value at Risk 95% (%)** - Maximum expected loss at 95% confidence
- **Conditional VaR 95% (%)** - Expected loss beyond VaR threshold

#### Distribution Metrics
- **Skewness** - Asymmetry of return distribution
- **Kurtosis** - Tail heaviness of distribution
- **Stability** - R-squared of linear fit to cumulative returns
- **Tail Ratio** - Ratio of right tail to left tail

### 📈 HTML Report Generation
- Interactive charts and visualizations
- Comprehensive performance analysis
- Powered by QuantStats library

## Installation

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Dependencies

- **requests** - API calls to fetch mutual fund data
- **pandas** - Data manipulation and analysis
- **numpy** - Numerical computations
- **empyrical** - Financial risk metrics calculations
- **quantstats** - Portfolio analytics and reporting
- **matplotlib** - Visualization (for reports)
- **pyportfolioopt** - Portfolio optimization tools

## Usage

### Basic Usage

```bash
python mf_anal.py
```

### Search by Fund Name

```
Enter Mutual Fund Scheme Code or Name: HDFC Flexi Cap
```

The tool will:
1. Search for matching funds
2. Display up to 10 results
3. Let you select which fund to analyze

### Direct Scheme Code

```
Enter Mutual Fund Scheme Code or Name: 119551
```

Directly analyzes the fund with scheme code 119551.

## Example Output

```
======================================================================
📈 COMPREHENSIVE RISK ANALYSIS
======================================================================

🎯 PERFORMANCE METRICS:
----------------------------------------------------------------------
  Total Return (%).................................... 234.56
  Annual Return (%)................................... 17.39
  Cumulative Return (%)............................... 234.56

📊 VOLATILITY METRICS:
----------------------------------------------------------------------
  Annual Volatility (%)............................... 17.18
  Daily Volatility (%)................................ 1.08
  Downside Deviation (%).............................. 12.45

⚖️  RISK-ADJUSTED RETURNS:
----------------------------------------------------------------------
  Sharpe Ratio........................................ 0.63
  Sortino Ratio....................................... 0.89
  Calmar Ratio........................................ 0.45

⚠️  RISK METRICS:
----------------------------------------------------------------------
  Max Drawdown (%).................................... -38.56
  Value at Risk 95% (%)............................... -2.15
  Conditional VaR 95% (%).............................. -3.42

📉 DISTRIBUTION METRICS:
----------------------------------------------------------------------
  Skewness............................................ -0.23
  Kurtosis............................................ 2.45
  Stability........................................... 0.87
  Tail Ratio.......................................... 1.12

📅 TIME PERIOD:
----------------------------------------------------------------------
  Start Date.......................................... 2012-01-01
  End Date............................................ 2026-02-06
  Total Days.......................................... 3223
======================================================================
```

## HTML Report

When prompted, generate a detailed HTML report with:
- Interactive performance charts
- Rolling metrics visualization
- Drawdown analysis
- Monthly/yearly returns heatmap
- Distribution plots

Open the generated `mf_report_[scheme_code].html` file in your browser.

## Popular Scheme Codes

- **119551** - Axis Bluechip Fund - Direct Growth
- **120503** - HDFC Balanced Advantage Fund - Direct Growth
- **118989** - SBI Small Cap Fund - Direct Growth
- **118955** - HDFC Flexi Cap Fund - Direct Growth
- **119597** - Parag Parikh Flexi Cap Fund - Direct Growth

## API Source

Data is fetched from [mfapi.in](https://www.mfapi.in/) - a free API for Indian mutual fund NAV data.

## Libraries Used

### Empyrical
Professional-grade risk metrics library by Quantopian. Provides industry-standard calculations for:
- Sharpe, Sortino, and Calmar ratios
- Maximum drawdown
- Value at Risk (VaR)
- Alpha and Beta

### QuantStats
Comprehensive portfolio analytics library. Features:
- Beautiful HTML reports
- Interactive visualizations
- Rolling metrics
- Benchmark comparisons

### PyPortfolioOpt
Portfolio optimization and risk modeling:
- Expected returns calculation
- Covariance matrices
- Efficient frontier analysis

## Notes

- **Risk-Free Rate**: Default is 6.5% (Indian context). Adjust in code if needed.
- **Trading Days**: Calculations assume 252 trading days per year.
- **Data Quality**: Depends on mfapi.in data availability and accuracy.

## Interpreting Metrics

### Sharpe Ratio
- **> 1.0**: Good risk-adjusted returns
- **> 2.0**: Very good
- **> 3.0**: Excellent

### Sortino Ratio
- Similar to Sharpe but only considers downside volatility
- Higher is better (penalizes only negative volatility)

### Max Drawdown
- Shows worst peak-to-trough decline
- Lower absolute value is better
- Important for understanding downside risk

### Tail Ratio
- **> 1.0**: More upside potential than downside risk
- **< 1.0**: More downside risk than upside potential

## Future Enhancements

- [ ] Benchmark comparison (Nifty 50, Sensex)
- [ ] Multi-fund comparison
- [ ] Portfolio optimization
- [ ] Rolling metrics visualization
- [ ] Export to Excel/CSV
- [ ] Email reports

## License

MIT License - Free to use and modify

## Contributing

Feel free to submit issues and enhancement requests!
