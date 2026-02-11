#!/usr/bin/env python3
"""
Mutual Fund Analyzer - Main Application
Production-ready modular mutual fund analysis tool
"""

import sys
import logging
from typing import List, Dict

from mf_analyzer.api_client import MFAPIClient
from mf_analyzer.calculator import RiskMetricsCalculator
from mf_analyzer.screener import FundScreener
from mf_analyzer.reports import ReportGenerator
from mf_analyzer.ui import ConsoleUI
from mf_analyzer.comparator import FundComparator
from mf_analyzer.config import (
    DEFAULT_RISK_FREE_RATE,
    DEFAULT_ANALYSIS_PERIOD_YEARS,
    DEFAULT_SCREENING_PERIOD_YEARS,
    TOP_N_FUNDS
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mf_analyzer.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class MutualFundAnalyzer:
    """Main application class for mutual fund analysis"""
    
    def __init__(self):
        self.api_client = MFAPIClient()
        self.calculator = RiskMetricsCalculator(risk_free_rate=DEFAULT_RISK_FREE_RATE)
        self.screener = FundScreener(self.api_client, self.calculator)
        self.report_generator = ReportGenerator()
        self.comparator = FundComparator()
        self.ui = ConsoleUI()
    
    def run_single_fund_analysis(self) -> None:
        """Run single fund analysis mode"""
        self.ui.display_single_fund_header()
        user_input = self.ui.get_fund_input()
        
        if not user_input:
            print("\n❌ No input provided. Exiting.")
            return
        
        scheme_code = user_input
        fund_name = f"Mutual Fund {scheme_code}"
        
        # Search if not a numeric code
        if not user_input.isdigit():
            print("\nSearching for mutual funds...")
            try:
                search_results = self.api_client.search_mutual_funds(user_input)
                
                if not search_results:
                    print(f"\nNo mutual funds found matching '{user_input}'")
                    print("\nTip: Try a shorter search term")
                    return
                
                selected_idx = self.ui.display_search_results(search_results)
                if selected_idx is None:
                    return
                
                scheme_code = str(search_results[selected_idx]['schemeCode'])
                fund_name = search_results[selected_idx]['schemeName']
                print(f"\nAnalyzing: {fund_name}")
                
            except Exception as e:
                print(f"\n❌ Error during search: {e}")
                logger.error(f"Search error: {e}", exc_info=True)
                return
        
        # Fetch and analyze
        try:
            print("\n⏳ Calculating comprehensive risk metrics...\n")
            nav_df = self.api_client.fetch_nav_history(scheme_code)
            metrics = self.calculator.calculate_comprehensive_metrics(
                nav_df,
                analysis_period_years=DEFAULT_ANALYSIS_PERIOD_YEARS
            )
            
            self.ui.display_metrics(metrics)
            
            # Generate report if requested
            if self.ui.ask_generate_report():
                output_file = f"mf_report_{scheme_code}.html"
                print(f"\n⏳ Generating comprehensive HTML report...")
                self.report_generator.generate_quantstats_report(nav_df, fund_name, output_file)
            
            print(f"\n✅ Analysis complete!\n")
            
        except ValueError as e:
            print(f"\n❌ Error: {e}")
            logger.error(f"Analysis error: {e}")
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            logger.error(f"Unexpected error: {e}", exc_info=True)
    
    def run_fund_screener(self) -> None:
        """Run fund screener mode"""
        self.ui.display_categories()
        
        # Get category selection
        search_query, category_name = self.ui.get_category_choice()
        if not search_query:
            return
        
        # Get plan type filter
        plan_type = self.ui.get_plan_type_choice()
        
        # Screen and rank funds
        top_funds = self.screener.screen_and_rank(
            search_query,
            analysis_years=DEFAULT_SCREENING_PERIOD_YEARS,
            top_n=TOP_N_FUNDS,
            plan_type=plan_type
        )
        
        if not top_funds:
            return
        
        # Display comparison
        self.report_generator.display_fund_comparison(top_funds, DEFAULT_SCREENING_PERIOD_YEARS)
        
        # Get analysis option
        num_to_analyze = self.ui.get_analysis_option()
        
        if num_to_analyze == 0:
            print("\n✅ Screening complete!\n")
            return
        
        # Get report option
        report_choice = self.ui.get_report_option()
        
        # Analyze selected funds
        print(f"\n⏳ Analyzing top {num_to_analyze} fund(s) in detail...\n")
        
        funds_data_for_tabbed = []
        
        for idx, fund in enumerate(top_funds[:num_to_analyze], 1):
            print("\n" + "=" * 70)
            print(f"📈 DETAILED ANALYSIS #{idx} - {fund['scheme_name'][:50]}")
            print("=" * 70)
            
            try:
                nav_df = self.api_client.fetch_nav_history(fund['scheme_code'])
                metrics = self.calculator.calculate_comprehensive_metrics(
                    nav_df,
                    analysis_period_years=DEFAULT_ANALYSIS_PERIOD_YEARS
                )
                
                # Store for tabbed report
                if report_choice == '1':
                    funds_data_for_tabbed.append({
                        'scheme_code': fund['scheme_code'],
                        'scheme_name': fund['scheme_name'],
                        'nav_df': nav_df,
                        'metrics': metrics
                    })
                
                # Display key metrics
                print(f"\n🎯 PERFORMANCE METRICS:")
                print("-" * 70)
                for metric in ['Total Return (%)', 'Annual Return (%)', 'Cumulative Return (%)']:
                    if metric in metrics:
                        print(f"  {metric:.<50} {metrics[metric]:>15}")
                
                print(f"\n📊 VOLATILITY METRICS:")
                print("-" * 70)
                for metric in ['Annual Volatility (%)', 'Monthly Volatility (%)', 'Downside Deviation (%)']:
                    if metric in metrics:
                        print(f"  {metric:.<50} {metrics[metric]:>15}")
                
                print(f"\n⚖️  RISK-ADJUSTED RETURNS:")
                print("-" * 70)
                for metric in ['Sharpe Ratio', 'Sortino Ratio', 'Calmar Ratio']:
                    if metric in metrics:
                        print(f"  {metric:.<50} {metrics[metric]:>15}")
                
                print(f"\n⚠️  RISK METRICS:")
                print("-" * 70)
                for metric in ['Max Drawdown (%)', 'Value at Risk 95% (%)', 'Conditional VaR 95% (%)']:
                    if metric in metrics:
                        print(f"  {metric:.<50} {metrics[metric]:>15}")
                
                # Generate separate report if requested
                if report_choice == '2':
                    output_file = f"mf_report_{fund['scheme_code']}.html"
                    print(f"\n⏳ Generating HTML report...")
                    self.report_generator.generate_quantstats_report(
                        nav_df,
                        fund['scheme_name'],
                        output_file
                    )
                
            except Exception as e:
                print(f"\n❌ Error analyzing fund: {e}")
                logger.error(f"Fund analysis error: {e}", exc_info=True)
        
        # Generate tabbed report if requested
        if report_choice == '1' and funds_data_for_tabbed:
            print("\n⏳ Generating tabbed HTML report...")
            category_slug = category_name.replace(' ', '_').replace('/', '_').replace('&', 'and')
            tabbed_report_file = f"mf_{category_slug}_comparison.html"
            self.report_generator.generate_tabbed_report(
                funds_data_for_tabbed,
                tabbed_report_file,
                category_name
            )
        
        # Final summary
        print("\n" + "=" * 70)
        print(f"✅ Detailed analysis complete for {num_to_analyze} fund(s)!")
        
        if report_choice == '1':
            print(f"\n📊 Tabbed HTML report generated: {tabbed_report_file}")
            print("   Open this file in your browser to view all funds with tabs.")
        elif report_choice == '2':
            print(f"\n📊 {num_to_analyze} separate HTML report(s) generated.")
            print("   Open the files in your browser for interactive charts.")
        
        print("\n" + "=" * 70 + "\n")
    
    def run_fund_comparison(self) -> None:
        """Run fund comparison mode"""
        print("\n" + "=" * 70)
        print("🔍 FUND COMPARISON MODE")
        print("=" * 70)
        
        # Get first fund
        print("\n📊 FUND 1")
        print("-" * 70)
        user_input1 = self.ui.get_fund_input()
        
        if not user_input1:
            return
        
        scheme_code1, fund_name1 = self._get_fund_details(user_input1)
        if not scheme_code1:
            return
        
        # Get second fund
        print("\n📊 FUND 2")
        print("-" * 70)
        user_input2 = self.ui.get_fund_input()
        
        if not user_input2:
            return
        
        scheme_code2, fund_name2 = self._get_fund_details(user_input2)
        if not scheme_code2:
            return
        
        # Get comparison period
        comparison_period = self.ui.get_comparison_period()
        
        try:
            # Fetch NAV data for both funds
            print("\n⏳ Fetching NAV data for both funds...")
            nav_data1 = self.api_client.fetch_nav_history(scheme_code1)
            nav_data2 = self.api_client.fetch_nav_history(scheme_code2)
            
            # Calculate metrics for both funds
            period_desc = f"{comparison_period} years" if comparison_period else "entire history"
            print(f"⏳ Calculating comprehensive metrics ({period_desc})...")
            metrics1 = self.calculator.calculate_comprehensive_metrics(
                nav_data1,
                analysis_period_years=comparison_period
            )
            metrics2 = self.calculator.calculate_comprehensive_metrics(
                nav_data2,
                analysis_period_years=comparison_period
            )
            
            # Compare funds
            print("⏳ Comparing funds and generating recommendation...")
            comparison = self.comparator.compare_funds(
                metrics1, metrics2,
                fund_name1, fund_name2
            )
            
            # Display comparison
            self.ui.display_comparison(comparison)
            
        except Exception as e:
            print(f"\n❌ Error during comparison: {e}")
            logger.error(f"Comparison error: {e}", exc_info=True)
    
    def _get_fund_details(self, user_input: str) -> tuple:
        """Helper to get scheme code and fund name from user input"""
        if user_input.isdigit():
            scheme_code = user_input
            fund_name = f"Fund {scheme_code}"
        else:
            try:
                search_results = self.api_client.search_mutual_funds(user_input)
                
                if not search_results:
                    print(f"\n❌ No funds found matching '{user_input}'")
                    return None, None
                
                selected_fund = self.ui.select_fund_from_search(search_results)
                if not selected_fund:
                    return None, None
                
                scheme_code = str(selected_fund['schemeCode'])
                fund_name = selected_fund['schemeName']
            except Exception as e:
                print(f"\n❌ Error during search: {e}")
                logger.error(f"Search error: {e}", exc_info=True)
                return None, None
        
        return scheme_code, fund_name
    
    def run(self) -> None:
        """Main application entry point"""
        try:
            self.ui.display_welcome()
            mode = self.ui.get_mode_choice()
            
            if mode == '2':
                self.run_fund_screener()
            elif mode == '3':
                self.run_fund_comparison()
            else:
                self.run_single_fund_analysis()
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Operation cancelled by user.\n")
            logger.info("Application interrupted by user")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            logger.error(f"Application error: {e}", exc_info=True)


def main():
    """Application entry point"""
    app = MutualFundAnalyzer()
    app.run()


if __name__ == "__main__":
    main()
