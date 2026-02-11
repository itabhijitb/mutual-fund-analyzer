"""
User interface module for console interactions
"""

from typing import Optional, Tuple, Dict
import logging

from .config import FUND_CATEGORIES

logger = logging.getLogger(__name__)


class ConsoleUI:
    """Handle console-based user interactions"""
    
    @staticmethod
    def display_welcome() -> None:
        """Display welcome message and main menu"""
        print("\n" + "=" * 70)
        print("📊 MUTUAL FUND ANALYSIS TOOL")
        print("=" * 70)
        print("\nChoose analysis mode:")
        print("  1. Analyze a single fund (detailed metrics)")
        print("  2. Find top 5 funds for 5-year investment (screener)")
        print("  3. Compare two funds and get recommendation")
        print("=" * 70)
    
    @staticmethod
    def get_mode_choice() -> str:
        """Get user's choice of analysis mode"""
        return input("\nEnter your choice (1, 2, or 3): ").strip()
    
    @staticmethod
    def display_categories() -> None:
        """Display all fund categories"""
        print("\n" + "=" * 70)
        print("🔍 FUND SCREENER - TOP 5 FOR 5-YEAR INVESTMENT")
        print("=" * 70)
        
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
    
    @staticmethod
    def get_category_choice() -> Tuple[Optional[str], Optional[str]]:
        """
        Get category selection from user.
        
        Returns:
            Tuple of (search_query, category_name) or (None, None) if invalid
        """
        category_choice = input("\nSelect category number (1-29): ").strip()
        
        if category_choice not in FUND_CATEGORIES:
            print("\n❌ Invalid category selection.")
            return None, None
        
        if category_choice == '29':
            search_query = input("\nEnter custom search term: ").strip()
            return search_query, search_query
        else:
            category = FUND_CATEGORIES[category_choice]
            print(f"\n✅ Selected: {category['name']}")
            return category['search'], category['name']
    
    @staticmethod
    def get_plan_type_choice() -> str:
        """Get plan type filter choice from user"""
        print("\n" + "=" * 70)
        print("💰 PLAN TYPE FILTER")
        print("=" * 70)
        print("  1. Growth plans only")
        print("  2. IDCW plans only (Dividend)")
        print("  3. Both Growth and IDCW")
        print("=" * 70)
        
        choice = input("\nSelect plan type (1-3): ").strip()
        
        if choice == '1':
            print("\n✅ Filter: Growth plans only")
            return 'growth'
        elif choice == '2':
            print("\n✅ Filter: IDCW plans only")
            return 'idcw'
        else:
            print("\n✅ Filter: Both Growth and IDCW plans")
            return 'both'
    
    @staticmethod
    def get_analysis_option() -> int:
        """Get detailed analysis option from user"""
        print("\n" + "=" * 70)
        print("📊 DETAILED ANALYSIS OPTIONS")
        print("=" * 70)
        print("  1. Analyze top fund only")
        print("  2. Analyze top 3 funds")
        print("  3. Analyze all top 5 funds")
        print("  4. Skip detailed analysis")
        print("=" * 70)
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '2':
            return 3
        elif choice == '3':
            return 5
        elif choice == '4':
            return 0
        else:
            return 1
    
    @staticmethod
    def get_report_option() -> str:
        """Get HTML report generation option from user"""
        print("\n" + "=" * 70)
        print("📊 HTML REPORT OPTIONS")
        print("=" * 70)
        print("  1. Single tabbed report (all funds in one file with tabs)")
        print("  2. Separate reports (one file per fund)")
        print("  3. No reports")
        print("=" * 70)
        
        return input("\nSelect option (1-3): ").strip()
    
    @staticmethod
    def display_single_fund_header() -> None:
        """Display header for single fund analysis mode"""
        print("\n" + "=" * 70)
        print("📊 SINGLE FUND ANALYSIS")
        print("=" * 70)
        print("\nYou can enter either:")
        print("  1. Numeric scheme code (e.g., 119551)")
        print("  2. Fund name to search (e.g., HDFC Flexi Cap)")
        print("=" * 70)
    
    @staticmethod
    def get_fund_input() -> str:
        """Get fund scheme code or name from user"""
        return input("\nEnter Mutual Fund Scheme Code or Name: ").strip()
    
    @staticmethod
    def display_search_results(results: list, limit: int = 10) -> Optional[int]:
        """
        Display search results and get user selection.
        
        Args:
            results: List of fund search results
            limit: Maximum number of results to display
            
        Returns:
            Selected index or None if user quits
        """
        print(f"\nFound {len(results)} matching fund(s):")
        print("=" * 60)
        
        for idx, fund in enumerate(results[:limit], 1):
            print(f"{idx}. {fund['schemeName']}")
            print(f"   Scheme Code: {fund['schemeCode']}")
            print()
        
        if len(results) > limit:
            print(f"... and {len(results) - limit} more results")
            print()
        
        selection = input("Enter the number of the fund to analyze (or 'q' to quit): ").strip()
        
        if selection.lower() == 'q':
            return None
        
        try:
            selected_idx = int(selection) - 1
            if 0 <= selected_idx < min(len(results), limit):
                return selected_idx
            else:
                print("\n❌ Invalid selection.")
                return None
        except ValueError:
            print("\n❌ Invalid input.")
            return None
    
    @staticmethod
    def select_fund_from_search(results: list, limit: int = 10) -> Optional[Dict]:
        """
        Display search results and return selected fund object.
        
        Args:
            results: List of fund search results
            limit: Maximum number of results to display
            
        Returns:
            Selected fund dictionary or None if user quits
        """
        print(f"\nFound {len(results)} matching fund(s):")
        print("=" * 60)
        
        for idx, fund in enumerate(results[:limit], 1):
            print(f"{idx}. {fund['schemeName']}")
            print(f"   Scheme Code: {fund['schemeCode']}")
            print()
        
        if len(results) > limit:
            print(f"... and {len(results) - limit} more results")
            print()
        
        selection = input("Enter the number of the fund to analyze (or 'q' to quit): ").strip()
        
        if selection.lower() == 'q':
            return None
        
        try:
            selected_idx = int(selection) - 1
            if 0 <= selected_idx < min(len(results), limit):
                return results[selected_idx]
            else:
                print("\n❌ Invalid selection.")
                return None
        except ValueError:
            print("\n❌ Invalid input.")
            return None
    
    @staticmethod
    def display_fund_metadata(metadata: dict) -> None:
        """Display fund metadata including fund house, category, NAV, time in market"""
        print("\n" + "=" * 70)
        print("ℹ️  FUND INFORMATION")
        print("=" * 70)
        
        print(f"\n📋 Fund Name: {metadata.get('scheme_name', 'N/A')}")
        print(f"🏢 Fund House: {metadata.get('fund_house', 'N/A')}")
        print(f"📂 Category: {metadata.get('scheme_category', 'N/A')}")
        print(f"📄 Scheme Type: {metadata.get('scheme_type', 'N/A')}")
        print(f"🔢 Scheme Code: {metadata.get('scheme_code', 'N/A')}")
        
        print(f"\n💰 Current NAV: ₹{metadata.get('current_nav', 0):.4f}")
        print(f"📅 Latest NAV Date: {metadata.get('latest_nav_date', 'N/A')}")
        print(f"🚀 Inception Date: {metadata.get('inception_date', 'N/A')}")
        print(f"⏱️  Time in Market: {metadata.get('years_in_market', 0)} years")
        
        if metadata.get('isin_growth', 'N/A') != 'N/A':
            print(f"\n🔖 ISIN (Growth): {metadata.get('isin_growth', 'N/A')}")
        if metadata.get('isin_div_reinvestment', 'N/A') != 'N/A':
            print(f"🔖 ISIN (Dividend): {metadata.get('isin_div_reinvestment', 'N/A')}")
        
        print("\n" + "=" * 70)
    
    @staticmethod
    def display_metrics(metrics: dict) -> None:
        """Display comprehensive metrics in organized format"""
        print("\n" + "=" * 70)
        print("📈 COMPREHENSIVE RISK ANALYSIS")
        print("=" * 70)
        
        # Performance Metrics
        print("\n🎯 PERFORMANCE METRICS:")
        print("-" * 70)
        perf_metrics = ['Total Return (%)', 'Annual Return (%)', 'Cumulative Return (%)']
        for metric in perf_metrics:
            if metric in metrics:
                print(f"  {metric:.<50} {metrics[metric]:>15}")
        
        # Volatility Metrics
        print("\n📊 VOLATILITY METRICS:")
        print("-" * 70)
        vol_metrics = ['Annual Volatility (%)', 'Monthly Volatility (%)', 'Downside Deviation (%)']
        for metric in vol_metrics:
            if metric in metrics:
                print(f"  {metric:.<50} {metrics[metric]:>15}")
        
        # Risk-Adjusted Returns
        print("\n⚖️  RISK-ADJUSTED RETURNS:")
        print("-" * 70)
        risk_adj_metrics = ['Sharpe Ratio', 'Sortino Ratio', 'Calmar Ratio']
        for metric in risk_adj_metrics:
            if metric in metrics:
                print(f"  {metric:.<50} {metrics[metric]:>15}")
        
        # Risk Metrics
        print("\n⚠️  RISK METRICS:")
        print("-" * 70)
        risk_metrics_list = ['Max Drawdown (%)', 'Value at Risk 95% (%)', 'Conditional VaR 95% (%)']
        for metric in risk_metrics_list:
            if metric in metrics:
                print(f"  {metric:.<50} {metrics[metric]:>15}")
        
        # Distribution Metrics
        print("\n📉 DISTRIBUTION METRICS:")
        print("-" * 70)
        dist_metrics = ['Skewness', 'Kurtosis', 'Stability', 'Tail Ratio']
        for metric in dist_metrics:
            if metric in metrics:
                print(f"  {metric:.<50} {metrics[metric]:>15}")
        
        # Analysis Details
        print("\n📅 ANALYSIS DETAILS:")
        print("-" * 70)
        time_metrics = ['Analysis Period', 'Start Date', 'End Date', 'Total Months', 'Risk-Free Rate (%)']
        for metric in time_metrics:
            if metric in metrics:
                print(f"  {metric:.<50} {metrics[metric]:>15}")
        
        print("\n" + "=" * 70)
    
    @staticmethod
    def ask_generate_report() -> bool:
        """Ask if user wants to generate HTML report"""
        response = input("\n📊 Generate detailed HTML report? (y/n): ").strip().lower()
        return response == 'y'
    
    @staticmethod
    def get_comparison_period() -> Optional[int]:
        """
        Get comparison period from user.
        
        Returns:
            Number of years for comparison or None for entire history
        """
        print("\n" + "=" * 70)
        print("📅 COMPARISON PERIOD")
        print("=" * 70)
        print("\nChoose analysis period for comparison:")
        print("  1. Entire fund history (recommended for complete picture)")
        print("  2. Last 10 years")
        print("  3. Last 5 years (apples-to-apples comparison)")
        print("  4. Last 3 years")
        print("  5. Custom period")
        print("=" * 70)
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            return None
        elif choice == '2':
            return 10
        elif choice == '3':
            return 5
        elif choice == '4':
            return 3
        elif choice == '5':
            try:
                years = int(input("Enter number of years: ").strip())
                if years > 0:
                    return years
                else:
                    print("\n⚠️  Invalid input. Using entire history.")
                    return None
            except ValueError:
                print("\n⚠️  Invalid input. Using entire history.")
                return None
        else:
            print("\n⚠️  Invalid choice. Using entire history.")
            return None
    
    @staticmethod
    def display_comparison(comparison: dict) -> None:
        """Display fund comparison results with recommendation"""
        print("\n" + "=" * 80)
        print("🔍 FUND COMPARISON ANALYSIS")
        print("=" * 80)
        
        fund1_name = comparison['fund1_name']
        fund2_name = comparison['fund2_name']
        
        print(f"\n📊 Comparing:")
        print(f"  Fund 1: {fund1_name}")
        print(f"  Fund 2: {fund2_name}")
        
        # Display analysis period information
        fund1_metrics = comparison['fund1_metrics']
        fund2_metrics = comparison['fund2_metrics']
        
        print(f"\n📅 Analysis Period:")
        print(f"  Fund 1: {fund1_metrics.get('Analysis Period', 'N/A')} ({fund1_metrics.get('Start Date', 'N/A')} to {fund1_metrics.get('End Date', 'N/A')})")
        print(f"  Fund 2: {fund2_metrics.get('Analysis Period', 'N/A')} ({fund2_metrics.get('Start Date', 'N/A')} to {fund2_metrics.get('End Date', 'N/A')})")
        
        # Display recommendation at the top
        print("\n" + "=" * 80)
        print("💡 RECOMMENDATION SUMMARY")
        print("=" * 80)
        rec = comparison['recommendation']
        
        print(f"\n  🎯 Recommended Fund: {rec['recommended_fund']}")
        print(f"  📊 Confidence Level: {rec['confidence']}")
        print(f"  📝 Primary Reason: {rec['reason']}")
        print(f"  ⚠️  Risk Profile: {rec['risk_profile']}")
        print(f"  ⏰ Investment Horizon: {rec['suggested_investment_horizon']}")
        
        scores = comparison['scores']
        print(f"\n  🏆 Overall Scores: Fund 1: {scores['fund1_score']:.1f}/100 | Fund 2: {scores['fund2_score']:.1f}/100")
        print(f"  📊 Score Difference: {abs(scores['fund1_score'] - scores['fund2_score']):.1f} points")
        
        # Display metric-by-metric comparison
        print("\n" + "=" * 80)
        print("📈 METRIC COMPARISON")
        print("=" * 80)
        print(f"\n{'Metric':<30} {'Fund 1':>15} {'Fund 2':>15} {'Winner':>15}")
        print("-" * 80)
        
        for metric, details in comparison['comparison_details'].items():
            val1 = details['fund1_value']
            val2 = details['fund2_value']
            winner_text = "Fund 1" if details['winner'] == 'fund1' else "Fund 2" if details['winner'] == 'fund2' else "Tie"
            
            # Add emoji for winner
            if details['winner'] == 'fund1':
                winner_display = f"✅ {winner_text}"
            elif details['winner'] == 'fund2':
                winner_display = f"✅ {winner_text}"
            else:
                winner_display = "🤝 Tie"
            
            print(f"{metric:<30} {val1:>15.2f} {val2:>15.2f} {winner_display:>15}")
        
        # Display detailed strengths and weaknesses
        print("\n" + "=" * 80)
        print("📊 DETAILED ANALYSIS")
        print("=" * 80)
        
        rec = comparison['recommendation']
        
        if rec['key_strengths']:
            print(f"\n  ✅ Key Strengths of Recommended Fund:")
            for strength in rec['key_strengths']:
                print(f"     • {strength}")
        
        if rec['key_weaknesses']:
            print(f"\n  ⚠️  Areas to Watch:")
            for weakness in rec['key_weaknesses']:
                print(f"     • {weakness}")
        
        print("\n" + "=" * 80)
        print("\n💡 Note: This recommendation is based on historical performance.")
        print("   Past performance does not guarantee future results.")
        print("   Consider your risk tolerance and investment goals.")
        print("=" * 80)
