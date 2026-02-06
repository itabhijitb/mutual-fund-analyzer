import requests
import pandas as pd
import numpy as np
import empyrical as ep
import quantstats as qs
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


def search_mutual_funds(query: str) -> list:
    api_url = "https://api.mfapi.in/mf/search"
    params = {"q": query}
    response = requests.get(api_url, params=params)
    response.raise_for_status()
    return response.json()


def fetch_nav_history(mutual_fund_scheme_code: str) -> pd.DataFrame:
    api_url = f"https://api.mfapi.in/mf/{mutual_fund_scheme_code}"
    response = requests.get(api_url)
    
    if response.status_code == 404:
        raise ValueError(
            f"Scheme code '{mutual_fund_scheme_code}' not found. "
            "Please enter a valid numeric scheme code (e.g., 119551 for Axis Bluechip Fund)."
        )
    
    response.raise_for_status()

    nav_json = response.json()["data"]

    nav_dataframe = pd.DataFrame(nav_json)

    nav_dataframe["date"] = pd.to_datetime(
        nav_dataframe["date"], format="%d-%m-%Y"
    )

    nav_dataframe["nav"] = nav_dataframe["nav"].astype(float)

    nav_dataframe.sort_values("date", inplace=True)

    nav_dataframe.reset_index(drop=True, inplace=True)
    return nav_dataframe


def calculate_comprehensive_metrics(
    nav_dataframe: pd.DataFrame,
    risk_free_rate: float = 0.07,
    analysis_period_years: int = 3
) -> dict:

    df = nav_dataframe.copy()
    df.set_index('date', inplace=True)
    
    # Filter to analysis period (default 3 years for industry standard)
    if analysis_period_years:
        cutoff_date = df.index[-1] - pd.DateOffset(years=analysis_period_years)
        df = df[df.index >= cutoff_date]
    
    if len(df) < 30:
        raise ValueError(f"Insufficient data for {analysis_period_years}-year analysis (need at least 30 days)")
    
    # Resample to monthly returns (industry standard)
    monthly_nav = df['nav'].resample('M').last()
    monthly_returns = monthly_nav.pct_change().dropna()
    
    # Also keep daily returns for some metrics
    daily_returns = df['nav'].pct_change().dropna()
    
    if len(monthly_returns) < 2:
        raise ValueError("Insufficient data to calculate risk metrics")

    metrics = {}
    
    # Convert annual risk-free rate to monthly for empyrical functions
    monthly_risk_free_rate = (1 + risk_free_rate) ** (1/12) - 1
    
    # Basic Metrics (using monthly returns - industry standard)
    metrics['Total Return (%)'] = round((df['nav'].iloc[-1] / df['nav'].iloc[0] - 1) * 100, 2)
    metrics['Annual Return (%)'] = round(ep.annual_return(monthly_returns, period='monthly') * 100, 2)
    metrics['Cumulative Return (%)'] = round(ep.cum_returns_final(monthly_returns) * 100, 2)
    
    # Volatility Metrics (using monthly returns, annualized)
    metrics['Annual Volatility (%)'] = round(ep.annual_volatility(monthly_returns, period='monthly') * 100, 2)
    metrics['Monthly Volatility (%)'] = round(monthly_returns.std() * 100, 2)
    
    # Risk-Adjusted Returns (INDUSTRY STANDARD: monthly returns)
    metrics['Sharpe Ratio'] = round(ep.sharpe_ratio(monthly_returns, risk_free=monthly_risk_free_rate, period='monthly'), 2)
    metrics['Sortino Ratio'] = round(ep.sortino_ratio(monthly_returns, required_return=monthly_risk_free_rate, period='monthly'), 2)
    metrics['Calmar Ratio'] = round(ep.calmar_ratio(monthly_returns, period='monthly'), 2)
    
    # Drawdown Metrics (use daily for more precision)
    metrics['Max Drawdown (%)'] = round(ep.max_drawdown(daily_returns) * 100, 2)
    
    # Risk Metrics (use daily returns for VaR)
    metrics['Value at Risk 95% (%)'] = round(ep.value_at_risk(daily_returns, cutoff=0.05) * 100, 2)
    metrics['Conditional VaR 95% (%)'] = round(ep.conditional_value_at_risk(daily_returns, cutoff=0.05) * 100, 2)
    
    # Downside Risk (monthly)
    downside_returns = monthly_returns[monthly_returns < 0]
    if len(downside_returns) > 0:
        metrics['Downside Deviation (%)'] = round(downside_returns.std() * np.sqrt(12) * 100, 2)
    else:
        metrics['Downside Deviation (%)'] = 0.0
    
    # Additional Metrics (monthly)
    metrics['Skewness'] = round(monthly_returns.skew(), 2)
    metrics['Kurtosis'] = round(monthly_returns.kurtosis(), 2)
    metrics['Stability'] = round(ep.stability_of_timeseries(monthly_returns), 2)
    metrics['Tail Ratio'] = round(ep.tail_ratio(monthly_returns), 2)
    
    # Time Period
    metrics['Analysis Period'] = f"{analysis_period_years} Year(s)" if analysis_period_years else "Full History"
    metrics['Start Date'] = df.index[0].strftime('%Y-%m-%d')
    metrics['End Date'] = df.index[-1].strftime('%Y-%m-%d')
    metrics['Total Days'] = len(df)
    metrics['Total Months'] = len(monthly_returns)
    metrics['Risk-Free Rate (%)'] = round(risk_free_rate * 100, 2)
    
    return metrics


def fetch_benchmark_data(benchmark: str = 'NIFTY50') -> pd.DataFrame:
    """
    Fetch benchmark index data for comparison.
    For Indian markets, we'll use Nifty 50 as default.
    """
    # This is a placeholder - in production, you'd fetch actual benchmark data
    # from sources like NSE, Yahoo Finance, or other APIs
    return None


def generate_html_report(nav_dataframe: pd.DataFrame, scheme_name: str, output_file: str = 'mf_report.html'):
    """
    Generate a comprehensive HTML report using QuantStats.
    """
    df = nav_dataframe.copy()
    df.set_index('date', inplace=True)
    returns = df['nav'].pct_change().dropna()
    
    # Generate HTML report
    qs.reports.html(returns, output=output_file, title=scheme_name)
    print(f"\n📊 Detailed HTML report generated: {output_file}")
    print(f"   Open this file in your browser for interactive charts and analysis.")


def generate_tabbed_html_report(funds_data: list, output_file: str = 'mf_comparison_report.html', category_name: str = None):
    """
    Generate a single HTML report with tabs for multiple funds.
    funds_data: list of dicts with 'scheme_code', 'scheme_name', 'nav_df', 'metrics'
    category_name: optional category name to include in the report title
    """
    import base64
    from io import BytesIO
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    
    report_title = f"{category_name} Funds Comparison" if category_name else "Mutual Fund Comparison"
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report_title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .tabs {{
            display: flex;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
            overflow-x: auto;
            padding: 0 20px;
        }}
        
        .tab {{
            padding: 15px 25px;
            cursor: pointer;
            border: none;
            background: transparent;
            font-size: 1em;
            font-weight: 500;
            color: #6c757d;
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
            white-space: nowrap;
        }}
        
        .tab:hover {{
            background: #e9ecef;
            color: #495057;
        }}
        
        .tab.active {{
            color: #667eea;
            border-bottom-color: #667eea;
            background: white;
        }}
        
        .tab-content {{
            display: none;
            padding: 30px;
            animation: fadeIn 0.3s ease;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .fund-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        
        .fund-header h2 {{
            font-size: 1.8em;
            margin-bottom: 5px;
        }}
        
        .fund-header .scheme-code {{
            opacity: 0.9;
            font-size: 0.9em;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .metric-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }}
        
        .metric-card h3 {{
            color: #495057;
            font-size: 0.9em;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .metric-value.positive {{
            color: #28a745;
        }}
        
        .metric-value.negative {{
            color: #dc3545;
        }}
        
        .section {{
            margin-bottom: 30px;
        }}
        
        .section h3 {{
            color: #495057;
            font-size: 1.3em;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e9ecef;
        }}
        
        .metric-row {{
            display: flex;
            justify-content: space-between;
            padding: 12px 15px;
            background: #f8f9fa;
            margin-bottom: 8px;
            border-radius: 5px;
        }}
        
        .metric-row:nth-child(even) {{
            background: white;
        }}
        
        .metric-label {{
            color: #6c757d;
            font-weight: 500;
        }}
        
        .metric-value-inline {{
            color: #495057;
            font-weight: 600;
        }}
        
        .chart-container {{
            margin: 20px 0;
            text-align: center;
        }}
        
        .chart-container img {{
            max-width: 100%;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .comparison-table {{
            margin-top: 30px;
            background: white;
            padding: 20px;
            border-radius: 10px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }}
        
        th {{
            background: #667eea;
            color: white;
            font-weight: 600;
            position: sticky;
            top: 0;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .rank-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        
        .rank-1 {{
            background: #ffd700;
            color: #856404;
        }}
        
        .rank-2 {{
            background: #c0c0c0;
            color: #383d41;
        }}
        
        .rank-3 {{
            background: #cd7f32;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 {report_title}</h1>
            <p>Comprehensive Analysis of Top Performing Funds</p>
            <p style="font-size: 0.9em; margin-top: 10px;">Generated on {pd.Timestamp.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="openTab(event, 'comparison')">📈 Comparison</button>
"""
    
    # Add tabs for each fund
    for idx, fund in enumerate(funds_data):
        tab_id = f"fund{idx}"
        fund_name_short = fund['scheme_name'][:30] + "..." if len(fund['scheme_name']) > 30 else fund['scheme_name']
        rank_emoji = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else f"{idx+1}."
        html_content += f'            <button class="tab" onclick="openTab(event, \'{tab_id}\')">{ rank_emoji} {fund_name_short}</button>\n'
    
    html_content += "        </div>\n\n"
    
    # Comparison tab content
    html_content += """
        <div id="comparison" class="tab-content active">
            <h2 style="color: #495057; margin-bottom: 20px;">Fund Comparison Overview</h2>
            <div class="comparison-table">
                <table>
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Fund Name</th>
                            <th>Annual Return</th>
                            <th>Sharpe Ratio</th>
                            <th>Sortino Ratio</th>
                            <th>Max Drawdown</th>
                            <th>Volatility</th>
                        </tr>
                    </thead>
                    <tbody>
"""
    
    # Add comparison rows
    for idx, fund in enumerate(funds_data):
        metrics = fund['metrics']
        rank_class = f"rank-{idx+1}" if idx < 3 else ""
        rank_emoji = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else f"{idx+1}"
        
        html_content += f"""
                        <tr>
                            <td><span class="rank-badge {rank_class}">{rank_emoji}</span></td>
                            <td><strong>{fund['scheme_name'][:50]}</strong></td>
                            <td style="color: #28a745; font-weight: 600;">{metrics.get('Annual Return (%)', 'N/A')}%</td>
                            <td>{metrics.get('Sharpe Ratio', 'N/A')}</td>
                            <td>{metrics.get('Sortino Ratio', 'N/A')}</td>
                            <td style="color: #dc3545; font-weight: 600;">{metrics.get('Max Drawdown (%)', 'N/A')}%</td>
                            <td>{metrics.get('Annual Volatility (%)', 'N/A')}%</td>
                        </tr>
"""
    
    html_content += """
                    </tbody>
                </table>
            </div>
        </div>
"""
    
    # Individual fund tabs
    for idx, fund in enumerate(funds_data):
        tab_id = f"fund{idx}"
        metrics = fund['metrics']
        nav_df = fund['nav_df'].copy()
        
        # Generate NAV chart
        plt.figure(figsize=(12, 6))
        nav_df_indexed = nav_df.set_index('date')
        plt.plot(nav_df_indexed.index, nav_df_indexed['nav'], linewidth=2, color='#667eea')
        plt.title(f"NAV Performance - {fund['scheme_name'][:50]}", fontsize=14, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('NAV', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Convert plot to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        chart_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        rank_emoji = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else f"#{idx+1}"
        
        html_content += f"""
        <div id="{tab_id}" class="tab-content">
            <div class="fund-header">
                <h2>{rank_emoji} {fund['scheme_name']}</h2>
                <p class="scheme-code">Scheme Code: {fund['scheme_code']}</p>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <h3>Annual Return</h3>
                    <div class="metric-value positive">{metrics.get('Annual Return (%)', 'N/A')}%</div>
                </div>
                <div class="metric-card">
                    <h3>Sharpe Ratio</h3>
                    <div class="metric-value">{metrics.get('Sharpe Ratio', 'N/A')}</div>
                </div>
                <div class="metric-card">
                    <h3>Sortino Ratio</h3>
                    <div class="metric-value">{metrics.get('Sortino Ratio', 'N/A')}</div>
                </div>
                <div class="metric-card">
                    <h3>Max Drawdown</h3>
                    <div class="metric-value negative">{metrics.get('Max Drawdown (%)', 'N/A')}%</div>
                </div>
            </div>
            
            <div class="chart-container">
                <img src="data:image/png;base64,{chart_base64}" alt="NAV Chart">
            </div>
            
            <div class="section">
                <h3>📊 Performance Metrics</h3>
                <div class="metric-row">
                    <span class="metric-label">Total Return</span>
                    <span class="metric-value-inline">{metrics.get('Total Return (%)', 'N/A')}%</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Cumulative Return</span>
                    <span class="metric-value-inline">{metrics.get('Cumulative Return (%)', 'N/A')}%</span>
                </div>
            </div>
            
            <div class="section">
                <h3>⚖️ Risk-Adjusted Returns</h3>
                <div class="metric-row">
                    <span class="metric-label">Calmar Ratio</span>
                    <span class="metric-value-inline">{metrics.get('Calmar Ratio', 'N/A')}</span>
                </div>
            </div>
            
            <div class="section">
                <h3>📉 Volatility Metrics</h3>
                <div class="metric-row">
                    <span class="metric-label">Annual Volatility</span>
                    <span class="metric-value-inline">{metrics.get('Annual Volatility (%)', 'N/A')}%</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Monthly Volatility</span>
                    <span class="metric-value-inline">{metrics.get('Monthly Volatility (%)', 'N/A')}%</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Downside Deviation</span>
                    <span class="metric-value-inline">{metrics.get('Downside Deviation (%)', 'N/A')}%</span>
                </div>
            </div>
            
            <div class="section">
                <h3>⚠️ Risk Metrics</h3>
                <div class="metric-row">
                    <span class="metric-label">Value at Risk (95%)</span>
                    <span class="metric-value-inline">{metrics.get('Value at Risk 95% (%)', 'N/A')}%</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Conditional VaR (95%)</span>
                    <span class="metric-value-inline">{metrics.get('Conditional VaR 95% (%)', 'N/A')}%</span>
                </div>
            </div>
            
            <div class="section">
                <h3>📅 Analysis Details</h3>
                <div class="metric-row">
                    <span class="metric-label">Analysis Period</span>
                    <span class="metric-value-inline">{metrics.get('Analysis Period', 'N/A')}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Start Date</span>
                    <span class="metric-value-inline">{metrics.get('Start Date', 'N/A')}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">End Date</span>
                    <span class="metric-value-inline">{metrics.get('End Date', 'N/A')}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Total Months Analyzed</span>
                    <span class="metric-value-inline">{metrics.get('Total Months', 'N/A')}</span>
                </div>
            </div>
        </div>
"""
    
    # Add JavaScript for tab switching
    html_content += """
    </div>
    
    <script>
        function openTab(evt, tabName) {
            var i, tabcontent, tablinks;
            
            tabcontent = document.getElementsByClassName("tab-content");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].classList.remove("active");
            }
            
            tablinks = document.getElementsByClassName("tab");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].classList.remove("active");
            }
            
            document.getElementById(tabName).classList.add("active");
            evt.currentTarget.classList.add("active");
        }
    </script>
</body>
</html>
"""
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n📊 Tabbed HTML report generated: {output_file}")
    print(f"   Open this file in your browser to view all {len(funds_data)} funds with tabs.")


def analyze_fund_for_screening(scheme_code: str, analysis_years: int = 5) -> dict:
    """
    Analyze a single fund and return key metrics for screening.
    Returns None if analysis fails.
    """
    try:
        nav_df = fetch_nav_history(scheme_code)
        metrics = calculate_comprehensive_metrics(nav_df, analysis_period_years=analysis_years)
        
        # Return simplified metrics for comparison
        return {
            'scheme_code': scheme_code,
            'annual_return': metrics.get('Annual Return (%)', 0),
            'sharpe_ratio': metrics.get('Sharpe Ratio', 0),
            'sortino_ratio': metrics.get('Sortino Ratio', 0),
            'max_drawdown': metrics.get('Max Drawdown (%)', 0),
            'volatility': metrics.get('Annual Volatility (%)', 0),
            'calmar_ratio': metrics.get('Calmar Ratio', 0),
            'total_return': metrics.get('Total Return (%)', 0),
            'months_analyzed': metrics.get('Total Months', 0)
        }
    except Exception as e:
        print(f"  ⚠️  Failed to analyze {scheme_code}: {str(e)[:50]}")
        return None


def screen_and_rank_funds(search_query: str, analysis_years: int = 5, top_n: int = 5, plan_type: str = 'both') -> list:
    """
    Search for funds, analyze them, and return top N ranked by composite score.
    plan_type: 'growth', 'idcw', or 'both'
    """
    print(f"\n🔍 Searching for '{search_query}' funds...")
    
    # Search for funds
    try:
        search_results = search_mutual_funds(search_query)
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return []
    
    if not search_results:
        print(f"❌ No funds found matching '{search_query}'")
        return []
    
    # Filter by plan type
    if plan_type != 'both':
        original_count = len(search_results)
        if plan_type == 'growth':
            search_results = [f for f in search_results if 'growth' in f['schemeName'].lower()]
        elif plan_type == 'idcw':
            search_results = [f for f in search_results if 'idcw' in f['schemeName'].lower() or 'dividend' in f['schemeName'].lower()]
        
        if not search_results:
            print(f"❌ No {plan_type.upper()} plans found (filtered from {original_count} funds)")
            return []
        
        print(f"✅ Found {len(search_results)} funds (filtered from {original_count} by {plan_type.upper()} plan type)")
    else:
        print(f"✅ Found {len(search_results)} funds")
    print(f"\n⏳ Analyzing funds for {analysis_years}-year performance...")
    print("   This may take a few moments...\n")
    
    analyzed_funds = []
    
    for idx, fund in enumerate(search_results, 1):
        scheme_code = str(fund['schemeCode'])
        scheme_name = fund['schemeName']
        
        print(f"  [{idx}/{len(search_results)}] Analyzing: {scheme_name[:60]}...")
        
        metrics = analyze_fund_for_screening(scheme_code, analysis_years)
        
        if metrics and metrics['months_analyzed'] >= analysis_years * 10:  # At least 10 months per year
            metrics['scheme_name'] = scheme_name
            
            # Calculate composite score (weighted average)
            # Sharpe ratio: 40%, Annual return: 30%, Sortino: 20%, Calmar: 10%
            composite_score = (
                metrics['sharpe_ratio'] * 0.4 +
                (metrics['annual_return'] / 20) * 0.3 +  # Normalize return
                metrics['sortino_ratio'] * 0.2 +
                metrics['calmar_ratio'] * 0.1
            )
            metrics['composite_score'] = round(composite_score, 2)
            
            analyzed_funds.append(metrics)
    
    if not analyzed_funds:
        print(f"\n❌ No funds had sufficient {analysis_years}-year data for analysis")
        return []
    
    # Sort by composite score
    analyzed_funds.sort(key=lambda x: x['composite_score'], reverse=True)
    
    print(f"\n✅ Successfully analyzed {len(analyzed_funds)} funds with sufficient data\n")
    
    return analyzed_funds[:top_n]


def display_fund_comparison(funds: list, analysis_years: int):
    """
    Display a comparison table of top funds.
    """
    if not funds:
        return
    
    print("\n" + "=" * 120)
    print(f"🏆 TOP {len(funds)} FUNDS FOR {analysis_years}-YEAR INVESTMENT")
    print("=" * 120)
    
    # Header
    print(f"\n{'Rank':<6}{'Fund Name':<50}{'Return':<12}{'Sharpe':<10}{'Sortino':<10}{'Drawdown':<12}{'Score':<10}")
    print("-" * 120)
    
    # Rows
    for idx, fund in enumerate(funds, 1):
        rank_emoji = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
        name = fund['scheme_name'][:48] + ".." if len(fund['scheme_name']) > 50 else fund['scheme_name']
        
        print(f"{rank_emoji:<6}{name:<50}{fund['annual_return']:>10.2f}%  "
              f"{fund['sharpe_ratio']:>8.2f}  {fund['sortino_ratio']:>8.2f}  "
              f"{fund['max_drawdown']:>10.2f}%  {fund['composite_score']:>8.2f}")
    
    print("\n" + "=" * 120)
    
    # Show detailed breakdown of top fund
    print(f"\n📊 DETAILED ANALYSIS - TOP RANKED FUND")
    print("=" * 120)
    top_fund = funds[0]
    print(f"\n🏆 {top_fund['scheme_name']}")
    print(f"   Scheme Code: {top_fund['scheme_code']}\n")
    print(f"   Annual Return............ {top_fund['annual_return']:>8.2f}%")
    print(f"   Total Return ({analysis_years}Y)...... {top_fund['total_return']:>8.2f}%")
    print(f"   Sharpe Ratio............. {top_fund['sharpe_ratio']:>8.2f}")
    print(f"   Sortino Ratio............ {top_fund['sortino_ratio']:>8.2f}")
    print(f"   Calmar Ratio............. {top_fund['calmar_ratio']:>8.2f}")
    print(f"   Annual Volatility........ {top_fund['volatility']:>8.2f}%")
    print(f"   Max Drawdown............. {top_fund['max_drawdown']:>8.2f}%")
    print(f"   Composite Score.......... {top_fund['composite_score']:>8.2f}")
    print("\n" + "=" * 120)


if __name__ == "__main__":

    print("\n" + "=" * 70)
    print("📊 MUTUAL FUND ANALYSIS TOOL")
    print("=" * 70)
    print("\nChoose analysis mode:")
    print("  1. Analyze a single fund (detailed metrics)")
    print("  2. Find top 5 funds for 5-year investment (screener)")
    print("=" * 70)
    
    mode = input("\nEnter your choice (1 or 2): ").strip()
    
    if mode == '2':
        # Fund Screener Mode
        print("\n" + "=" * 70)
        print("🔍 FUND SCREENER - TOP 5 FOR 5-YEAR INVESTMENT")
        print("=" * 70)
        
        # Define comprehensive fund categories
        categories = {
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
        
        print("\n📂 EQUITY FUNDS:")
        print("  1. Large Cap / Bluechip          2. Mid Cap")
        print("  3. Small Cap                     4. Multi Cap")
        print("  5. Flexi Cap                     6. Large & Mid Cap")
        print("  7. Focused Fund")
        
        print("\n🏭 SECTORAL FUNDS:")
        print("  8. Banking                       9. Technology")
        print(" 10. Pharma                       11. Infrastructure")
        print(" 12. FMCG                         13. Energy")
        
        print("\n🌱 THEMATIC FUNDS:")
        print(" 14. ESG                          15. Dividend Yield")
        
        print("\n💰 TAX SAVING & HYBRID:")
        print(" 16. ELSS / Tax Saver             17. Balanced / Hybrid")
        print(" 18. Aggressive Hybrid            19. Conservative Hybrid")
        print(" 20. Equity Savings               21. Multi Asset Allocation")
        print(" 22. Arbitrage Fund")
        
        print("\n📈 INDEX FUNDS:")
        print(" 23. Nifty 50                     24. Sensex")
        print(" 25. Nifty Next 50")
        
        print("\n🎯 OTHER STRATEGIES:")
        print(" 26. Value Fund                   27. Contra Fund")
        print(" 28. International / Global       29. Custom Search")
        
        print("\n" + "=" * 70)
        
        category_choice = input("\nSelect category number (1-29): ").strip()
        
        if category_choice in categories:
            if category_choice == '29':
                search_query = input("\nEnter custom search term: ").strip()
                selected_category_name = search_query
            else:
                search_query = categories[category_choice]['search']
                selected_category_name = categories[category_choice]['name']
                print(f"\n✅ Selected: {selected_category_name}")
        else:
            print("\n❌ Invalid category selection. Exiting.")
            exit(0)
        
        if not search_query:
            print("\n❌ No search query provided. Exiting.")
            exit(0)
        
        # Ask for plan type preference
        print("\n" + "=" * 70)
        print("💰 PLAN TYPE FILTER")
        print("=" * 70)
        print("  1. Growth plans only")
        print("  2. IDCW plans only (Dividend)")
        print("  3. Both Growth and IDCW")
        print("=" * 70)
        
        plan_type_choice = input("\nSelect plan type (1-3): ").strip()
        
        plan_type_filter = None
        if plan_type_choice == '1':
            plan_type_filter = 'growth'
            print("\n✅ Filter: Growth plans only")
        elif plan_type_choice == '2':
            plan_type_filter = 'idcw'
            print("\n✅ Filter: IDCW plans only")
        else:
            plan_type_filter = 'both'
            print("\n✅ Filter: Both Growth and IDCW plans")
        
        # Screen and rank funds
        top_funds = screen_and_rank_funds(search_query, analysis_years=5, top_n=5, plan_type=plan_type_filter)
        
        if top_funds:
            display_fund_comparison(top_funds, analysis_years=5)
            
            # Ask if user wants detailed analysis
            print("\n" + "=" * 70)
            print("📊 DETAILED ANALYSIS OPTIONS")
            print("=" * 70)
            print("  1. Analyze top fund only")
            print("  2. Analyze top 3 funds")
            print("  3. Analyze all top 5 funds")
            print("  4. Skip detailed analysis")
            print("=" * 70)
            
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == '4':
                print("\n✅ Screening complete!\n")
                exit(0)
            
            # Determine how many funds to analyze
            num_to_analyze = 1
            if choice == '2':
                num_to_analyze = min(3, len(top_funds))
            elif choice == '3':
                num_to_analyze = len(top_funds)
            else:
                num_to_analyze = 1
            
            # Ask about HTML reports
            print("\n" + "=" * 70)
            print("📊 HTML REPORT OPTIONS")
            print("=" * 70)
            print("  1. Single tabbed report (all funds in one file with tabs)")
            print("  2. Separate reports (one file per fund)")
            print("  3. No reports")
            print("=" * 70)
            
            report_choice = input("\nSelect option (1-3): ").strip()
            
            # Analyze selected funds
            print(f"\n⏳ Analyzing top {num_to_analyze} fund(s) in detail...\n")
            
            funds_data_for_tabbed = []
            
            for idx, fund in enumerate(top_funds[:num_to_analyze], 1):
                print("\n" + "=" * 70)
                print(f"📈 DETAILED ANALYSIS #{idx} - {fund['scheme_name'][:50]}")
                print("=" * 70)
                
                try:
                    nav_df = fetch_nav_history(fund['scheme_code'])
                    metrics = calculate_comprehensive_metrics(nav_df, analysis_period_years=3)
                    
                    # Store data for tabbed report if needed
                    if report_choice == '1':
                        funds_data_for_tabbed.append({
                            'scheme_code': fund['scheme_code'],
                            'scheme_name': fund['scheme_name'],
                            'nav_df': nav_df,
                            'metrics': metrics
                        })
                    
                    # Display comprehensive metrics
                    print(f"\n🎯 PERFORMANCE METRICS:")
                    print("-" * 70)
                    perf_metrics = ['Total Return (%)', 'Annual Return (%)', 'Cumulative Return (%)']
                    for metric in perf_metrics:
                        if metric in metrics:
                            print(f"  {metric:.<50} {metrics[metric]:>15}")
                    
                    print(f"\n📊 VOLATILITY METRICS:")
                    print("-" * 70)
                    vol_metrics = ['Annual Volatility (%)', 'Monthly Volatility (%)', 'Downside Deviation (%)']
                    for metric in vol_metrics:
                        if metric in metrics:
                            print(f"  {metric:.<50} {metrics[metric]:>15}")
                    
                    print(f"\n⚖️  RISK-ADJUSTED RETURNS:")
                    print("-" * 70)
                    risk_adj_metrics = ['Sharpe Ratio', 'Sortino Ratio', 'Calmar Ratio']
                    for metric in risk_adj_metrics:
                        if metric in metrics:
                            print(f"  {metric:.<50} {metrics[metric]:>15}")
                    
                    print(f"\n⚠️  RISK METRICS:")
                    print("-" * 70)
                    risk_metrics_list = ['Max Drawdown (%)', 'Value at Risk 95% (%)', 'Conditional VaR 95% (%)']
                    for metric in risk_metrics_list:
                        if metric in metrics:
                            print(f"  {metric:.<50} {metrics[metric]:>15}")
                    
                    # Generate separate HTML report if requested
                    if report_choice == '2':
                        output_file = f"mf_report_{fund['scheme_code']}.html"
                        print(f"\n⏳ Generating HTML report...")
                        generate_html_report(nav_df, fund['scheme_name'], output_file)
                    
                except Exception as e:
                    print(f"\n❌ Error analyzing fund: {e}")
            
            # Generate tabbed report if requested
            if report_choice == '1' and funds_data_for_tabbed:
                print("\n⏳ Generating tabbed HTML report...")
                # Create filename with category name
                category_slug = selected_category_name.replace(' ', '_').replace('/', '_').replace('&', 'and')
                tabbed_report_file = f"mf_{category_slug}_comparison.html"
                generate_tabbed_html_report(funds_data_for_tabbed, tabbed_report_file, selected_category_name)
            
            print("\n" + "=" * 70)
            print(f"✅ Detailed analysis complete for {num_to_analyze} fund(s)!")
            if report_choice == '1':
                print(f"\n📊 Tabbed HTML report generated: {tabbed_report_file}")
                print("   Open this file in your browser to view all funds with tabs.")
            elif report_choice == '2':
                print(f"\n📊 {num_to_analyze} separate HTML report(s) generated.")
                print("   Open the files in your browser for interactive charts.")
            print("\n" + "=" * 70 + "\n")
            exit(0)
        else:
            exit(0)
    else:
        # Single Fund Analysis Mode
        print("\n" + "=" * 70)
        print("📊 SINGLE FUND ANALYSIS")
        print("=" * 70)
        print("\nYou can enter either:")
        print("  1. Numeric scheme code (e.g., 119551)")
        print("  2. Fund name to search (e.g., HDFC Flexi Cap)")
        print("=" * 70)
    
        user_input = input("\nEnter Mutual Fund Scheme Code or Name: ").strip()
    
    scheme_code = user_input
    
    if not user_input.isdigit():
        print("\nSearching for mutual funds...")
        try:
            search_results = search_mutual_funds(user_input)
            
            if not search_results:
                print(f"\nNo mutual funds found matching '{user_input}'")
                print("\nTip: Try a shorter search term like:")
                print("  - 'HDFC Flexi' instead of 'HDFC Flexi Cap Fund - Regular Plan'")
                print("  - 'Axis Blue' instead of 'Axis Bluechip Fund'")
                print("  - 'SBI Small' instead of 'SBI Small Cap Fund'")
                exit(1)
            
            print(f"\nFound {len(search_results)} matching fund(s):")
            print("=" * 60)
            
            for idx, fund in enumerate(search_results[:10], 1):
                print(f"{idx}. {fund['schemeName']}")
                print(f"   Scheme Code: {fund['schemeCode']}")
                print()
            
            if len(search_results) > 10:
                print(f"... and {len(search_results) - 10} more results")
                print()
            
            selection = input("Enter the number of the fund to analyze (or 'q' to quit): ").strip()
            
            if selection.lower() == 'q':
                exit(0)
            
            try:
                selected_idx = int(selection) - 1
                if 0 <= selected_idx < min(len(search_results), 10):
                    scheme_code = str(search_results[selected_idx]['schemeCode'])
                    print(f"\nAnalyzing: {search_results[selected_idx]['schemeName']}")
                else:
                    print("\nInvalid selection.")
                    exit(1)
            except ValueError:
                print("\nInvalid input.")
                exit(1)
        except Exception as e:
            print(f"\nError during search: {e}")
            exit(1)

    try:
        nav_history_dataframe = fetch_nav_history(scheme_code)
        
        # Get fund name for report
        fund_name = f"Mutual Fund {scheme_code}"
        if not user_input.isdigit() and 'search_results' in locals():
            fund_name = search_results[selected_idx]['schemeName']
        
        print("\n⏳ Calculating comprehensive risk metrics...\n")
        
        risk_statistics = calculate_comprehensive_metrics(nav_history_dataframe)
        
        # Display metrics in organized sections
        print("\n" + "=" * 70)
        print(f"📈 COMPREHENSIVE RISK ANALYSIS")
        print("=" * 70)
        
        # Performance Metrics
        print("\n🎯 PERFORMANCE METRICS:")
        print("-" * 70)
        perf_metrics = ['Total Return (%)', 'Annual Return (%)', 'Cumulative Return (%)']
        for metric in perf_metrics:
            if metric in risk_statistics:
                print(f"  {metric:.<50} {risk_statistics[metric]:>15}")
        
        # Volatility Metrics
        print("\n📊 VOLATILITY METRICS:")
        print("-" * 70)
        vol_metrics = ['Annual Volatility (%)', 'Monthly Volatility (%)', 'Downside Deviation (%)']
        for metric in vol_metrics:
            if metric in risk_statistics:
                print(f"  {metric:.<50} {risk_statistics[metric]:>15}")
        
        # Risk-Adjusted Returns
        print("\n⚖️  RISK-ADJUSTED RETURNS:")
        print("-" * 70)
        risk_adj_metrics = ['Sharpe Ratio', 'Sortino Ratio', 'Calmar Ratio']
        for metric in risk_adj_metrics:
            if metric in risk_statistics:
                print(f"  {metric:.<50} {risk_statistics[metric]:>15}")
        
        # Risk Metrics
        print("\n⚠️  RISK METRICS:")
        print("-" * 70)
        risk_metrics = ['Max Drawdown (%)', 'Value at Risk 95% (%)', 'Conditional VaR 95% (%)']
        for metric in risk_metrics:
            if metric in risk_statistics:
                print(f"  {metric:.<50} {risk_statistics[metric]:>15}")
        
        # Distribution Metrics
        print("\n📉 DISTRIBUTION METRICS:")
        print("-" * 70)
        dist_metrics = ['Skewness', 'Kurtosis', 'Stability', 'Tail Ratio']
        for metric in dist_metrics:
            if metric in risk_statistics:
                print(f"  {metric:.<50} {risk_statistics[metric]:>15}")
        
        # Time Period
        print("\n📅 ANALYSIS DETAILS:")
        print("-" * 70)
        time_metrics = ['Analysis Period', 'Start Date', 'End Date', 'Total Months', 'Risk-Free Rate (%)']
        for metric in time_metrics:
            if metric in risk_statistics:
                print(f"  {metric:.<50} {risk_statistics[metric]:>15}")
        
        print("\n" + "=" * 70)
        
        # Ask if user wants HTML report
        generate_report = input("\n📊 Generate detailed HTML report? (y/n): ").strip().lower()
        if generate_report == 'y':
            output_file = f"mf_report_{scheme_code}.html"
            print(f"\n⏳ Generating comprehensive HTML report...")
            generate_html_report(nav_history_dataframe, fund_name, output_file)
            print(f"\n✅ Analysis complete!\n")
        else:
            print(f"\n✅ Analysis complete!\n")
            
    except ValueError as e:
        print(f"\n❌ Error: {e}")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()
