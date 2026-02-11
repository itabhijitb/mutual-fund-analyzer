"""
Report generation module for HTML and console outputs
"""

import pandas as pd
import quantstats as qs
from typing import List, Dict
import base64
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate various types of reports for mutual fund analysis"""
    
    @staticmethod
    def generate_quantstats_report(
        nav_dataframe: pd.DataFrame,
        scheme_name: str,
        output_file: str
    ) -> None:
        """
        Generate a comprehensive HTML report using QuantStats.
        
        Args:
            nav_dataframe: DataFrame with 'date' and 'nav' columns
            scheme_name: Name of the mutual fund scheme
            output_file: Path to save the HTML report
        """
        df = nav_dataframe.copy()
        df.set_index('date', inplace=True)
        returns = df['nav'].pct_change().dropna()
        
        qs.reports.html(returns, output=output_file, title=scheme_name)
        print(f"\n📊 Detailed HTML report generated: {output_file}")
        print(f"   Open this file in your browser for interactive charts and analysis.")
        logger.info(f"Generated QuantStats report: {output_file}")
    
    @staticmethod
    def generate_tabbed_report(
        funds_data: List[Dict],
        output_file: str,
        category_name: str = None
    ) -> None:
        """
        Generate a single HTML report with tabs for multiple funds.
        
        Args:
            funds_data: List of dicts with 'scheme_code', 'scheme_name', 'nav_df', 'metrics'
            output_file: Path to save the HTML report
            category_name: Optional category name for the report title
        """
        report_title = f"{category_name} Funds Comparison" if category_name else "Mutual Fund Comparison"
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report_title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
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
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ font-size: 1.1em; opacity: 0.9; }}
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
        .tab:hover {{ background: #e9ecef; color: #495057; }}
        .tab.active {{ color: #667eea; border-bottom-color: #667eea; background: white; }}
        .tab-content {{ display: none; padding: 30px; animation: fadeIn 0.3s ease; }}
        .tab-content.active {{ display: block; }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        .fund-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .fund-header h2 {{ font-size: 1.8em; margin-bottom: 5px; }}
        .fund-header .scheme-code {{ opacity: 0.9; font-size: 0.9em; }}
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
        .metric-card:hover {{ transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }}
        .metric-card h3 {{
            color: #495057;
            font-size: 0.9em;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .metric-value.positive {{ color: #28a745; }}
        .metric-value.negative {{ color: #dc3545; }}
        .section {{ margin-bottom: 30px; }}
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
        .metric-row:nth-child(even) {{ background: white; }}
        .metric-label {{ color: #6c757d; font-weight: 500; }}
        .metric-value-inline {{ color: #495057; font-weight: 600; }}
        .chart-container {{ margin: 20px 0; text-align: center; }}
        .chart-container img {{
            max-width: 100%;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .comparison-table {{ margin-top: 30px; background: white; padding: 20px; border-radius: 10px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e9ecef; }}
        th {{ background: #667eea; color: white; font-weight: 600; position: sticky; top: 0; }}
        tr:hover {{ background: #f8f9fa; }}
        .rank-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        .rank-1 {{ background: #ffd700; color: #856404; }}
        .rank-2 {{ background: #c0c0c0; color: #383d41; }}
        .rank-3 {{ background: #cd7f32; color: white; }}
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
            html_content += f'            <button class="tab" onclick="openTab(event, \'{tab_id}\')">{rank_emoji} {fund_name_short}</button>\n'
        
        html_content += "        </div>\n\n"
        
        # Comparison tab
        html_content += """
        <div id="comparison" class="tab-content active">
            <h2 style="color: #495057; margin-bottom: 20px;">Fund Comparison Overview</h2>
            <div class="comparison-table">
                <table>
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Fund Name</th>
                            <th>Efficiency Score</th>
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
            
            # Get efficiency score from fund data if available
            efficiency_score = fund.get('efficiency_score', 'N/A')
            
            html_content += f"""
                        <tr>
                            <td><span class="rank-badge {rank_class}">{rank_emoji}</span></td>
                            <td><strong>{fund['scheme_name'][:50]}</strong></td>
                            <td style="color: #667eea; font-weight: 700; font-size: 1.1em;">{efficiency_score}</td>
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
        
        # JavaScript for tab switching
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
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n📊 Tabbed HTML report generated: {output_file}")
        print(f"   Open this file in your browser to view all {len(funds_data)} funds with tabs.")
        logger.info(f"Generated tabbed report: {output_file}")
    
    @staticmethod
    def display_fund_comparison(funds: List[Dict], analysis_years: int) -> None:
        """
        Display a comparison table of top funds in the console.
        
        Args:
            funds: List of fund dictionaries with metrics
            analysis_years: Number of years analyzed
        """
        if not funds:
            return
        
        print("\n" + "=" * 120)
        print(f"🏆 TOP {len(funds)} FUNDS FOR {analysis_years}-YEAR INVESTMENT")
        print("=" * 120)
        
        # Header
        print(f"\n{'Rank':<6}{'Fund Name':<50}{'Efficiency':<12}{'Return':<12}{'Sharpe':<10}{'Sortino':<10}{'Drawdown':<12}")
        print("-" * 120)
        
        # Rows
        for idx, fund in enumerate(funds, 1):
            rank_emoji = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
            name = fund['scheme_name'][:48] + ".." if len(fund['scheme_name']) > 50 else fund['scheme_name']
            efficiency = fund.get('efficiency_score', fund.get('composite_score', 0))
            
            print(f"{rank_emoji:<6}{name:<50}{efficiency:>10.2f}  "
                  f"{fund['annual_return']:>10.2f}%  "
                  f"{fund['sharpe_ratio']:>8.2f}  {fund['sortino_ratio']:>8.2f}  "
                  f"{fund['max_drawdown']:>10.2f}%")
        
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
        print(f"   Efficiency Score......... {top_fund.get('efficiency_score', top_fund.get('composite_score', 'N/A')):>8.2f}")
        print("\n" + "=" * 120)
