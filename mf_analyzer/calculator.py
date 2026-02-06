"""
Risk metrics calculation module
"""

import pandas as pd
import numpy as np
import empyrical as ep
import warnings
from typing import Dict, Optional
import logging

from .config import DEFAULT_RISK_FREE_RATE, DEFAULT_ANALYSIS_PERIOD_YEARS

logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')


class RiskMetricsCalculator:
    """Calculator for comprehensive risk and performance metrics"""
    
    def __init__(self, risk_free_rate: float = DEFAULT_RISK_FREE_RATE):
        self.risk_free_rate = risk_free_rate
    
    def calculate_comprehensive_metrics(
        self,
        nav_dataframe: pd.DataFrame,
        analysis_period_years: int = DEFAULT_ANALYSIS_PERIOD_YEARS
    ) -> Dict:
        """
        Calculate comprehensive risk and performance metrics.
        
        Args:
            nav_dataframe: DataFrame with 'date' and 'nav' columns
            analysis_period_years: Number of years to analyze (default: 3)
            
        Returns:
            Dictionary containing all calculated metrics
            
        Raises:
            ValueError: If insufficient data for analysis
        """
        df = nav_dataframe.copy()
        df.set_index('date', inplace=True)
        
        # Filter to analysis period
        if analysis_period_years:
            cutoff_date = df.index[-1] - pd.DateOffset(years=analysis_period_years)
            df = df[df.index >= cutoff_date]
        
        if len(df) < 30:
            raise ValueError(
                f"Insufficient data for {analysis_period_years}-year analysis "
                f"(need at least 30 days, got {len(df)})"
            )
        
        # Resample to monthly returns (industry standard)
        monthly_nav = df['nav'].resample('M').last()
        monthly_returns = monthly_nav.pct_change().dropna()
        
        # Also keep daily returns for some metrics
        daily_returns = df['nav'].pct_change().dropna()
        
        if len(monthly_returns) < 2:
            raise ValueError("Insufficient data to calculate risk metrics")
        
        metrics = {}
        
        # Convert annual risk-free rate to monthly
        monthly_risk_free_rate = (1 + self.risk_free_rate) ** (1/12) - 1
        
        # Basic Metrics
        metrics['Total Return (%)'] = round(
            (df['nav'].iloc[-1] / df['nav'].iloc[0] - 1) * 100, 2
        )
        metrics['Annual Return (%)'] = round(
            ep.annual_return(monthly_returns, period='monthly') * 100, 2
        )
        metrics['Cumulative Return (%)'] = round(
            ep.cum_returns_final(monthly_returns) * 100, 2
        )
        
        # Volatility Metrics
        metrics['Annual Volatility (%)'] = round(
            ep.annual_volatility(monthly_returns, period='monthly') * 100, 2
        )
        metrics['Monthly Volatility (%)'] = round(
            monthly_returns.std() * 100, 2
        )
        
        # Risk-Adjusted Returns
        metrics['Sharpe Ratio'] = round(
            ep.sharpe_ratio(monthly_returns, risk_free=monthly_risk_free_rate, period='monthly'), 2
        )
        metrics['Sortino Ratio'] = round(
            ep.sortino_ratio(monthly_returns, required_return=monthly_risk_free_rate, period='monthly'), 2
        )
        metrics['Calmar Ratio'] = round(
            ep.calmar_ratio(monthly_returns, period='monthly'), 2
        )
        
        # Drawdown Metrics
        metrics['Max Drawdown (%)'] = round(
            ep.max_drawdown(daily_returns) * 100, 2
        )
        
        # Risk Metrics
        metrics['Value at Risk 95% (%)'] = round(
            ep.value_at_risk(daily_returns, cutoff=0.05) * 100, 2
        )
        metrics['Conditional VaR 95% (%)'] = round(
            ep.conditional_value_at_risk(daily_returns, cutoff=0.05) * 100, 2
        )
        
        # Downside Risk
        downside_returns = monthly_returns[monthly_returns < 0]
        if len(downside_returns) > 0:
            metrics['Downside Deviation (%)'] = round(
                downside_returns.std() * np.sqrt(12) * 100, 2
            )
        else:
            metrics['Downside Deviation (%)'] = 0.0
        
        # Additional Metrics
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
        metrics['Risk-Free Rate (%)'] = round(self.risk_free_rate * 100, 2)
        
        logger.info(f"Calculated metrics for period {metrics['Start Date']} to {metrics['End Date']}")
        return metrics
    
    def calculate_screening_metrics(
        self,
        nav_dataframe: pd.DataFrame,
        analysis_period_years: int = 5
    ) -> Optional[Dict]:
        """
        Calculate simplified metrics for fund screening.
        
        Args:
            nav_dataframe: DataFrame with 'date' and 'nav' columns
            analysis_period_years: Number of years to analyze
            
        Returns:
            Dictionary with key metrics or None if calculation fails
        """
        try:
            metrics = self.calculate_comprehensive_metrics(
                nav_dataframe, 
                analysis_period_years=analysis_period_years
            )
            
            return {
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
            logger.warning(f"Failed to calculate screening metrics: {str(e)[:50]}")
            return None
