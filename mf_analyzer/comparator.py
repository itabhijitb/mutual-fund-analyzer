"""
Fund comparison and recommendation module
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class FundComparator:
    """Compare two mutual funds and provide recommendations"""
    
    def __init__(self):
        pass
    
    def compare_funds(
        self,
        fund1_metrics: Dict,
        fund2_metrics: Dict,
        fund1_name: str,
        fund2_name: str
    ) -> Dict:
        """
        Compare two funds and generate detailed comparison.
        
        Args:
            fund1_metrics: Metrics dictionary for fund 1
            fund2_metrics: Metrics dictionary for fund 2
            fund1_name: Name of fund 1
            fund2_name: Name of fund 2
            
        Returns:
            Dictionary containing comparison results and recommendation
        """
        comparison = {
            'fund1_name': fund1_name,
            'fund2_name': fund2_name,
            'fund1_metrics': fund1_metrics,
            'fund2_metrics': fund2_metrics,
            'comparison_details': {},
            'scores': {},
            'recommendation': {}
        }
        
        # Compare key metrics
        metrics_to_compare = [
            ('Annual Return (%)', 'higher_better'),
            ('Sharpe Ratio', 'higher_better'),
            ('Sortino Ratio', 'higher_better'),
            ('Calmar Ratio', 'higher_better'),
            ('Max Drawdown (%)', 'lower_better'),
            ('Annual Volatility (%)', 'lower_better'),
            ('Value at Risk 95% (%)', 'lower_better'),
            ('Downside Deviation (%)', 'lower_better'),
        ]
        
        for metric, direction in metrics_to_compare:
            if metric in fund1_metrics and metric in fund2_metrics:
                val1 = fund1_metrics[metric]
                val2 = fund2_metrics[metric]
                
                if direction == 'higher_better':
                    winner = 'fund1' if val1 > val2 else 'fund2' if val2 > val1 else 'tie'
                    diff = val1 - val2
                else:  # lower_better
                    winner = 'fund1' if val1 < val2 else 'fund2' if val2 < val1 else 'tie'
                    diff = val2 - val1  # Reverse for lower is better
                
                comparison['comparison_details'][metric] = {
                    'fund1_value': val1,
                    'fund2_value': val2,
                    'difference': round(diff, 2),
                    'winner': winner,
                    'direction': direction
                }
        
        # Calculate overall scores
        scores = self._calculate_scores(comparison['comparison_details'])
        comparison['scores'] = scores
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            comparison['comparison_details'],
            scores,
            fund1_name,
            fund2_name,
            fund1_metrics,
            fund2_metrics
        )
        comparison['recommendation'] = recommendation
        
        logger.info(f"Completed comparison between {fund1_name} and {fund2_name}")
        return comparison
    
    def _calculate_scores(self, comparison_details: Dict) -> Dict:
        """Calculate weighted scores for each fund"""
        
        # Weights for different aspects
        weights = {
            'Annual Return (%)': 0.25,
            'Sharpe Ratio': 0.20,
            'Sortino Ratio': 0.15,
            'Calmar Ratio': 0.10,
            'Max Drawdown (%)': 0.15,
            'Annual Volatility (%)': 0.10,
            'Value at Risk 95% (%)': 0.03,
            'Downside Deviation (%)': 0.02,
        }
        
        fund1_score = 0
        fund2_score = 0
        total_weight = 0
        
        for metric, details in comparison_details.items():
            if metric in weights:
                weight = weights[metric]
                total_weight += weight
                
                if details['winner'] == 'fund1':
                    fund1_score += weight
                elif details['winner'] == 'fund2':
                    fund2_score += weight
                else:  # tie
                    fund1_score += weight / 2
                    fund2_score += weight / 2
        
        # Normalize scores to 100
        if total_weight > 0:
            fund1_score = round((fund1_score / total_weight) * 100, 2)
            fund2_score = round((fund2_score / total_weight) * 100, 2)
        
        return {
            'fund1_score': fund1_score,
            'fund2_score': fund2_score,
            'winner': 'fund1' if fund1_score > fund2_score else 'fund2' if fund2_score > fund1_score else 'tie'
        }
    
    def _generate_recommendation(
        self,
        comparison_details: Dict,
        scores: Dict,
        fund1_name: str,
        fund2_name: str,
        fund1_metrics: Dict,
        fund2_metrics: Dict
    ) -> Dict:
        """Generate detailed recommendation based on comparison"""
        
        winner = scores['winner']
        
        if winner == 'tie':
            recommended_fund = "Both funds are equally matched"
            confidence = "Low"
            reason = "The funds show similar performance across key metrics"
        else:
            recommended_fund = fund1_name if winner == 'fund1' else fund2_name
            score_diff = abs(scores['fund1_score'] - scores['fund2_score'])
            
            if score_diff > 20:
                confidence = "High"
            elif score_diff > 10:
                confidence = "Medium"
            else:
                confidence = "Low"
            
            # Build reason based on strengths
            strengths = []
            for metric, details in comparison_details.items():
                if details['winner'] == winner:
                    strengths.append(metric)
            
            reason = f"Better performance in: {', '.join(strengths[:3])}"
        
        # Risk profile assessment
        winner_metrics = fund1_metrics if winner == 'fund1' else fund2_metrics
        volatility = winner_metrics.get('Annual Volatility (%)', 0)
        max_dd = abs(winner_metrics.get('Max Drawdown (%)', 0))
        
        if volatility < 15 and max_dd < 20:
            risk_profile = "Low Risk"
        elif volatility < 25 and max_dd < 35:
            risk_profile = "Moderate Risk"
        else:
            risk_profile = "High Risk"
        
        # Investment horizon suggestion
        sharpe = winner_metrics.get('Sharpe Ratio', 0)
        if sharpe > 1.5:
            horizon = "3+ years (Strong risk-adjusted returns)"
        elif sharpe > 1.0:
            horizon = "5+ years (Good risk-adjusted returns)"
        else:
            horizon = "7+ years (Requires longer horizon)"
        
        return {
            'recommended_fund': recommended_fund,
            'confidence': confidence,
            'reason': reason,
            'risk_profile': risk_profile,
            'suggested_investment_horizon': horizon,
            'key_strengths': self._get_key_strengths(comparison_details, winner),
            'key_weaknesses': self._get_key_weaknesses(comparison_details, winner),
            'overall_score_difference': abs(scores['fund1_score'] - scores['fund2_score'])
        }
    
    def _get_key_strengths(self, comparison_details: Dict, winner: str) -> List[str]:
        """Get top 3 strengths of the winning fund"""
        strengths = []
        
        for metric, details in comparison_details.items():
            if details['winner'] == winner and details['difference'] != 0:
                strengths.append({
                    'metric': metric,
                    'difference': abs(details['difference'])
                })
        
        # Sort by difference magnitude
        strengths.sort(key=lambda x: x['difference'], reverse=True)
        
        return [s['metric'] for s in strengths[:3]]
    
    def _get_key_weaknesses(self, comparison_details: Dict, winner: str) -> List[str]:
        """Get top 3 weaknesses of the winning fund"""
        loser = 'fund2' if winner == 'fund1' else 'fund1'
        weaknesses = []
        
        for metric, details in comparison_details.items():
            if details['winner'] == loser and details['difference'] != 0:
                weaknesses.append({
                    'metric': metric,
                    'difference': abs(details['difference'])
                })
        
        # Sort by difference magnitude
        weaknesses.sort(key=lambda x: x['difference'], reverse=True)
        
        return [w['metric'] for w in weaknesses[:3]]
