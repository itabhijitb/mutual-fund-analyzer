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
        """Calculate scores using cost-benefit analysis with trade-off considerations"""
        
        # Extract metrics for both funds
        fund1_return = comparison_details.get('Annual Return (%)', {}).get('fund1_value', 0)
        fund2_return = comparison_details.get('Annual Return (%)', {}).get('fund2_value', 0)
        
        fund1_sharpe = comparison_details.get('Sharpe Ratio', {}).get('fund1_value', 0)
        fund2_sharpe = comparison_details.get('Sharpe Ratio', {}).get('fund2_value', 0)
        
        fund1_sortino = comparison_details.get('Sortino Ratio', {}).get('fund1_value', 0)
        fund2_sortino = comparison_details.get('Sortino Ratio', {}).get('fund2_value', 0)
        
        fund1_volatility = comparison_details.get('Annual Volatility (%)', {}).get('fund1_value', 0)
        fund2_volatility = comparison_details.get('Annual Volatility (%)', {}).get('fund2_value', 0)
        
        fund1_drawdown = abs(comparison_details.get('Max Drawdown (%)', {}).get('fund1_value', 0))
        fund2_drawdown = abs(comparison_details.get('Max Drawdown (%)', {}).get('fund2_value', 0))
        
        fund1_calmar = comparison_details.get('Calmar Ratio', {}).get('fund1_value', 0)
        fund2_calmar = comparison_details.get('Calmar Ratio', {}).get('fund2_value', 0)
        
        # Calculate efficiency scores using mathematical models
        fund1_efficiency = self._calculate_efficiency_score(
            fund1_return, fund1_sharpe, fund1_sortino, fund1_volatility, fund1_drawdown, fund1_calmar
        )
        fund2_efficiency = self._calculate_efficiency_score(
            fund2_return, fund2_sharpe, fund2_sortino, fund2_volatility, fund2_drawdown, fund2_calmar
        )
        
        # Normalize to 100-point scale
        total_efficiency = fund1_efficiency + fund2_efficiency
        if total_efficiency > 0:
            fund1_score = round((fund1_efficiency / total_efficiency) * 100, 2)
            fund2_score = round((fund2_efficiency / total_efficiency) * 100, 2)
        else:
            fund1_score = 50.0
            fund2_score = 50.0
        
        # Determine winner with minimum threshold
        score_diff = abs(fund1_score - fund2_score)
        if score_diff < 5:  # Less than 5% difference = tie
            winner = 'tie'
        else:
            winner = 'fund1' if fund1_score > fund2_score else 'fund2'
        
        return {
            'fund1_score': fund1_score,
            'fund2_score': fund2_score,
            'fund1_efficiency': round(fund1_efficiency, 2),
            'fund2_efficiency': round(fund2_efficiency, 2),
            'winner': winner,
            'methodology': 'Risk-Adjusted Efficiency Model'
        }
    
    def _calculate_efficiency_score(
        self,
        annual_return: float,
        sharpe: float,
        sortino: float,
        volatility: float,
        max_drawdown: float,
        calmar: float
    ) -> float:
        """
        Calculate efficiency score using multi-factor optimization model.
        
        Model considers:
        1. Risk-adjusted returns (Sharpe, Sortino, Calmar) - 60% weight
        2. Absolute return with diminishing returns - 25% weight
        3. Risk penalty (volatility, drawdown) - 15% weight
        
        This ensures marginal return improvements don't outweigh significant risk differences.
        """
        # Component 1: Risk-Adjusted Returns (most important)
        # Average of normalized risk-adjusted ratios
        risk_adj_score = 0
        risk_adj_count = 0
        
        if sharpe > 0:
            # Sharpe ratio normalized (excellent > 2, good > 1, poor < 0.5)
            sharpe_normalized = min(sharpe / 2.0, 1.0) * 100
            risk_adj_score += sharpe_normalized * 0.4  # 40% of risk-adj component
            risk_adj_count += 1
        
        if sortino > 0:
            # Sortino ratio normalized (excellent > 2.5, good > 1.5, poor < 0.75)
            sortino_normalized = min(sortino / 2.5, 1.0) * 100
            risk_adj_score += sortino_normalized * 0.35  # 35% of risk-adj component
            risk_adj_count += 1
        
        if calmar > 0:
            # Calmar ratio normalized (excellent > 2, good > 1, poor < 0.5)
            calmar_normalized = min(calmar / 2.0, 1.0) * 100
            risk_adj_score += calmar_normalized * 0.25  # 25% of risk-adj component
            risk_adj_count += 1
        
        # Component 2: Absolute Return with Diminishing Returns
        # Use logarithmic scaling to prevent marginal return differences from dominating
        if annual_return > 0:
            # Log scale: 10% = 0.5, 20% = 0.65, 30% = 0.74, 40% = 0.80
            return_score = np.log1p(annual_return / 10) / np.log1p(4) * 100
        else:
            return_score = 0
        
        # Component 3: Risk Penalty
        # Penalize high volatility and drawdown
        volatility_penalty = 0
        if volatility > 0:
            # Penalty increases non-linearly with volatility
            # Low vol (5%) = small penalty, High vol (20%) = large penalty
            volatility_penalty = min((volatility / 20) ** 1.5 * 50, 50)
        
        drawdown_penalty = 0
        if max_drawdown > 0:
            # Penalty increases non-linearly with drawdown
            # Small DD (10%) = small penalty, Large DD (30%) = large penalty
            drawdown_penalty = min((max_drawdown / 30) ** 1.5 * 50, 50)
        
        risk_penalty = (volatility_penalty * 0.4 + drawdown_penalty * 0.6)
        
        # Combine components with weights
        # Risk-adjusted returns: 60%, Absolute return: 25%, Risk penalty: -15%
        efficiency_score = (
            risk_adj_score * 0.60 +
            return_score * 0.25 -
            risk_penalty * 0.15
        )
        
        return max(efficiency_score, 0)  # Ensure non-negative
    
    def _generate_recommendation(
        self,
        comparison_details: Dict,
        scores: Dict,
        fund1_name: str,
        fund2_name: str,
        fund1_metrics: Dict,
        fund2_metrics: Dict
    ) -> Dict:
        """Generate detailed recommendation based on cost-benefit analysis"""
        
        winner = scores['winner']
        score_diff = abs(scores['fund1_score'] - scores['fund2_score'])
        
        if winner == 'tie':
            recommended_fund = "Both funds are equally matched"
            confidence = "Low"
            reason = "Efficiency scores are within 5% - no clear winner based on risk-adjusted analysis"
            trade_off_analysis = "Both funds offer similar risk-return trade-offs"
        else:
            recommended_fund = fund1_name if winner == 'fund1' else fund2_name
            loser_name = fund2_name if winner == 'fund1' else fund1_name
            
            # Confidence based on efficiency score difference
            if score_diff > 25:
                confidence = "Very High"
            elif score_diff > 15:
                confidence = "High"
            elif score_diff > 8:
                confidence = "Medium"
            else:
                confidence = "Low"
            
            # Analyze trade-offs
            trade_off_analysis = self._analyze_tradeoffs(
                comparison_details, winner, recommended_fund, loser_name
            )
            
            # Build reason based on efficiency model
            winner_metrics = fund1_metrics if winner == 'fund1' else fund2_metrics
            loser_metrics = fund2_metrics if winner == 'fund1' else fund1_metrics
            
            sharpe_diff = winner_metrics.get('Sharpe Ratio', 0) - loser_metrics.get('Sharpe Ratio', 0)
            return_diff = winner_metrics.get('Annual Return (%)', 0) - loser_metrics.get('Annual Return (%)', 0)
            
            if sharpe_diff > 0.3:
                reason = f"Superior risk-adjusted returns (Sharpe: +{sharpe_diff:.2f}) justify recommendation"
            elif return_diff > 3 and sharpe_diff > 0:
                reason = f"Better returns (+{return_diff:.1f}%) with comparable or lower risk"
            else:
                reason = "Better overall efficiency based on multi-factor risk-return optimization"
        
        # Risk profile assessment
        winner_metrics = fund1_metrics if winner == 'fund1' else fund2_metrics if winner != 'tie' else fund1_metrics
        volatility = winner_metrics.get('Annual Volatility (%)', 0)
        max_dd = abs(winner_metrics.get('Max Drawdown (%)', 0))
        sharpe = winner_metrics.get('Sharpe Ratio', 0)
        
        if volatility < 12 and max_dd < 15:
            risk_profile = "Low Risk (Conservative)"
        elif volatility < 18 and max_dd < 25:
            risk_profile = "Moderate Risk (Balanced)"
        elif volatility < 25 and max_dd < 35:
            risk_profile = "Moderate-High Risk (Growth)"
        else:
            risk_profile = "High Risk (Aggressive)"
        
        # Investment horizon based on risk-adjusted metrics
        if sharpe > 1.8 and max_dd < 20:
            horizon = "3+ years (Excellent risk-adjusted profile)"
        elif sharpe > 1.2 and max_dd < 30:
            horizon = "5+ years (Good risk-adjusted profile)"
        elif sharpe > 0.8:
            horizon = "7+ years (Moderate risk-adjusted profile)"
        else:
            horizon = "10+ years (Requires long horizon for risk compensation)"
        
        return {
            'recommended_fund': recommended_fund,
            'confidence': confidence,
            'reason': reason,
            'trade_off_analysis': trade_off_analysis,
            'risk_profile': risk_profile,
            'suggested_investment_horizon': horizon,
            'key_strengths': self._get_key_strengths(comparison_details, winner),
            'key_weaknesses': self._get_key_weaknesses(comparison_details, winner),
            'overall_score_difference': score_diff,
            'methodology': scores.get('methodology', 'N/A')
        }
    
    def _analyze_tradeoffs(
        self,
        comparison_details: Dict,
        winner: str,
        winner_name: str,
        loser_name: str
    ) -> str:
        """Analyze trade-offs between return and risk metrics"""
        
        if winner == 'tie':
            return "No significant trade-offs - funds are equally balanced"
        
        # Check if winner has lower return but better risk metrics
        return_winner = comparison_details.get('Annual Return (%)', {}).get('winner', 'tie')
        sharpe_winner = comparison_details.get('Sharpe Ratio', {}).get('winner', 'tie')
        volatility_winner = comparison_details.get('Annual Volatility (%)', {}).get('winner', 'tie')
        drawdown_winner = comparison_details.get('Max Drawdown (%)', {}).get('winner', 'tie')
        
        return_diff = abs(comparison_details.get('Annual Return (%)', {}).get('difference', 0))
        sharpe_diff = abs(comparison_details.get('Sharpe Ratio', {}).get('difference', 0))
        vol_diff = abs(comparison_details.get('Annual Volatility (%)', {}).get('difference', 0))
        dd_diff = abs(comparison_details.get('Max Drawdown (%)', {}).get('difference', 0))
        
        # Case 1: Winner has lower return but much better risk profile
        if return_winner != winner and sharpe_winner == winner:
            if return_diff < 3 and sharpe_diff > 0.3:
                return f"{winner_name} sacrifices {return_diff:.1f}% return for significantly better risk-adjusted performance (Sharpe +{sharpe_diff:.2f})"
            elif vol_diff > 3 or dd_diff > 5:
                return f"{winner_name} offers {vol_diff:.1f}% lower volatility and {dd_diff:.1f}% better drawdown control, worth the {return_diff:.1f}% return trade-off"
        
        # Case 2: Winner has higher return AND better risk metrics
        if return_winner == winner and (sharpe_winner == winner or volatility_winner == winner):
            return f"{winner_name} dominates with both higher returns (+{return_diff:.1f}%) and better risk metrics - no trade-off needed"
        
        # Case 3: Winner has higher return but slightly worse risk
        if return_winner == winner and sharpe_winner != winner:
            if return_diff > 5 and sharpe_diff < 0.2:
                return f"{winner_name}'s {return_diff:.1f}% higher return justifies marginally higher risk (Sharpe diff: {sharpe_diff:.2f})"
        
        return f"{winner_name} offers better overall risk-return efficiency based on multi-factor analysis"
    
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
