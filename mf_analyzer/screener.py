"""
Fund screening and ranking module
"""

from typing import List, Dict, Optional
import logging

from .api_client import MFAPIClient
from .calculator import RiskMetricsCalculator
from .config import SCORING_WEIGHTS, MIN_MONTHS_PER_YEAR, PLAN_TYPES

logger = logging.getLogger(__name__)


class FundScreener:
    """Screen and rank mutual funds based on performance metrics"""
    
    def __init__(self, api_client: MFAPIClient, calculator: RiskMetricsCalculator):
        self.api_client = api_client
        self.calculator = calculator
    
    def filter_by_plan_type(self, funds: List[Dict], plan_type: str) -> List[Dict]:
        """
        Filter funds by plan type (Growth/IDCW/Both).
        
        Args:
            funds: List of fund dictionaries
            plan_type: 'growth', 'idcw', or 'both'
            
        Returns:
            Filtered list of funds
        """
        if plan_type == 'both':
            return funds
        
        keywords = PLAN_TYPES.get(plan_type, [])
        filtered = [
            f for f in funds 
            if any(keyword in f['schemeName'].lower() for keyword in keywords)
        ]
        
        logger.info(f"Filtered {len(funds)} funds to {len(filtered)} by {plan_type} plan type")
        return filtered
    
    def calculate_composite_score(self, metrics: Dict) -> float:
        """
        Calculate composite score for ranking funds.
        
        Args:
            metrics: Dictionary of fund metrics
            
        Returns:
            Composite score
        """
        score = (
            metrics['sharpe_ratio'] * SCORING_WEIGHTS['sharpe_ratio'] +
            (metrics['annual_return'] / 20) * SCORING_WEIGHTS['annual_return'] +
            metrics['sortino_ratio'] * SCORING_WEIGHTS['sortino_ratio'] +
            metrics['calmar_ratio'] * SCORING_WEIGHTS['calmar_ratio']
        )
        return round(score, 2)
    
    def screen_and_rank(
        self,
        search_query: str,
        analysis_years: int = 5,
        top_n: int = 5,
        plan_type: str = 'both'
    ) -> List[Dict]:
        """
        Search, analyze, and rank mutual funds.
        
        Args:
            search_query: Search term for funds
            analysis_years: Years of data to analyze
            top_n: Number of top funds to return
            plan_type: Filter by plan type ('growth', 'idcw', 'both')
            
        Returns:
            List of top N ranked funds with metrics
        """
        print(f"\n🔍 Searching for '{search_query}' funds...")
        
        # Search for funds
        try:
            search_results = self.api_client.search_mutual_funds(search_query)
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []
        
        if not search_results:
            print(f"❌ No funds found matching '{search_query}'")
            return []
        
        # Filter by plan type
        original_count = len(search_results)
        search_results = self.filter_by_plan_type(search_results, plan_type)
        
        if not search_results:
            print(f"❌ No {plan_type.upper()} plans found (filtered from {original_count} funds)")
            return []
        
        if plan_type != 'both':
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
            
            try:
                nav_df = self.api_client.fetch_nav_history(scheme_code)
                metrics = self.calculator.calculate_screening_metrics(nav_df, analysis_years)
                
                if metrics and metrics['months_analyzed'] >= analysis_years * MIN_MONTHS_PER_YEAR:
                    metrics['scheme_code'] = scheme_code
                    metrics['scheme_name'] = scheme_name
                    metrics['composite_score'] = self.calculate_composite_score(metrics)
                    analyzed_funds.append(metrics)
                    
            except Exception as e:
                logger.warning(f"Failed to analyze {scheme_code}: {str(e)[:50]}")
                print(f"  ⚠️  Failed to analyze {scheme_code}: {str(e)[:50]}")
        
        if not analyzed_funds:
            print(f"\n❌ No funds had sufficient {analysis_years}-year data for analysis")
            return []
        
        # Sort by composite score
        analyzed_funds.sort(key=lambda x: x['composite_score'], reverse=True)
        
        print(f"\n✅ Successfully analyzed {len(analyzed_funds)} funds with sufficient data\n")
        
        return analyzed_funds[:top_n]
