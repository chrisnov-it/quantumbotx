# core/strategies/performance_scorer.py
"""
🏆 Performance Scoring System for Strategy Ranking

This module ranks strategy/instrument combinations based on multiple performance metrics
to enable automatic strategy switching.

Features:
- Multi-metric performance scoring
- Risk-adjusted returns calculation
- Recent performance weighting
- Strategy/instrument compatibility scoring
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class PerformanceScorer:
    """
    Scores and ranks strategy/instrument combinations for automatic switching
    """
    
    def __init__(self):
        # Scoring weights for different metrics
        self.scoring_weights = {
            'profitability': 0.30,      # 30% weight
            'risk_control': 0.25,       # 25% weight
            'consistency': 0.20,        # 20% weight
            'activity_level': 0.15,     # 15% weight
            'market_fit': 0.10          # 10% weight
        }
    
    def calculate_performance_score(self, backtest_results: dict, market_condition: dict, 
                                  strategy_id: str, symbol: str) -> dict:
        """
        Calculate comprehensive performance score for a strategy/instrument combination
        
        Args:
            backtest_results: Backtest results from enhanced engine
            market_condition: Market condition analysis
            strategy_id: Strategy identifier
            symbol: Trading symbol
            
        Returns:
            dict: Performance score and component metrics
        """
        try:
            # Extract key metrics
            metrics = self._extract_metrics(backtest_results)
            
            # Calculate component scores
            profitability_score = self._calculate_profitability_score(metrics)
            risk_score = self._calculate_risk_score(metrics)
            consistency_score = self._calculate_consistency_score(metrics)
            activity_score = self._calculate_activity_score(metrics)
            market_fit_score = self._calculate_market_fit_score(strategy_id, symbol, market_condition)
            
            # Weighted composite score
            composite_score = (
                profitability_score * self.scoring_weights['profitability'] +
                risk_score * self.scoring_weights['risk_control'] +
                consistency_score * self.scoring_weights['consistency'] +
                activity_score * self.scoring_weights['activity_level'] +
                market_fit_score * self.scoring_weights['market_fit']
            )
            
            return {
                'composite_score': composite_score,
                'components': {
                    'profitability': profitability_score,
                    'risk_control': risk_score,
                    'consistency': consistency_score,
                    'activity_level': activity_score,
                    'market_fit': market_fit_score
                },
                'metrics': metrics,
                'strategy_id': strategy_id,
                'symbol': symbol,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Performance scoring error: {e}")
            return self._default_score(strategy_id, symbol)
    
    def _extract_metrics(self, backtest_results: dict) -> dict:
        """Extract key performance metrics from backtest results"""
        return {
            'total_profit': backtest_results.get('total_profit_usd', 0),
            'net_profit': backtest_results.get('net_profit_after_costs', 0),
            'gross_profit': backtest_results.get('total_profit_usd', 0),
            'total_trades': backtest_results.get('total_trades', 0),
            'wins': backtest_results.get('wins', 0),
            'losses': backtest_results.get('losses', 0),
            'win_rate': backtest_results.get('win_rate_percent', 0),
            'max_drawdown': abs(backtest_results.get('max_drawdown_percent', 0)),
            'avg_win': backtest_results.get('avg_win', 0),
            'avg_loss': backtest_results.get('avg_loss', 0),
            'spread_costs': abs(backtest_results.get('total_spread_costs', 0)),
            'final_capital': backtest_results.get('final_capital', 10000),
            'initial_capital': backtest_results.get('initial_capital', 10000)
        }
    
    def _calculate_profitability_score(self, metrics: dict) -> float:
        """Calculate profitability component score (0-1)"""
        net_profit = metrics['net_profit']
        total_trades = metrics['total_trades']
        spread_costs = metrics['spread_costs']
        gross_profit = metrics['gross_profit']
        
        # Base score on net profit
        if total_trades == 0:
            return 0.5  # Neutral score for no trades
        
        # Profit factor (gross profit / absolute losses)
        if gross_profit <= 0:
            profit_factor = 0
        else:
            absolute_losses = abs(gross_profit - net_profit - spread_costs)
            profit_factor = gross_profit / (absolute_losses + 1e-10)
        
        # Normalize profit factor (capped at 5 for practical purposes)
        normalized_profit_factor = min(1.0, profit_factor / 5.0)
        
        # Win rate component (30-70% is good range)
        win_rate = metrics['win_rate'] / 100  # Convert to decimal
        win_rate_score = 1 - abs(win_rate - 0.5) * 2  # Peak at 50%, but we want higher win rates
        # Adjust for win rates above 50%
        if win_rate > 0.5:
            win_rate_score = min(1.0, win_rate_score + (win_rate - 0.5) * 2)
        
        # Combine factors
        profitability_score = (normalized_profit_factor * 0.6 + win_rate_score * 0.4)
        
        return min(1.0, max(0.0, profitability_score))
    
    def _calculate_risk_score(self, metrics: dict) -> float:
        """Calculate risk control component score (0-1)"""
        max_drawdown = metrics['max_drawdown']
        total_trades = metrics['total_trades']
        
        if total_trades == 0:
            return 0.5  # Neutral score
        
        # Drawdown score (lower is better)
        # Drawdown under 10% = full score, 50%+ = 0 score
        if max_drawdown <= 10:
            drawdown_score = 1.0
        elif max_drawdown >= 50:
            drawdown_score = 0.0
        else:
            # Linear interpolation between 10% and 50%
            drawdown_score = 1.0 - (max_drawdown - 10) / 40
        
        # Risk/reward ratio (estimated from avg win/loss)
        avg_win = abs(metrics['avg_win'])
        avg_loss = abs(metrics['avg_loss'])
        
        if avg_loss <= 0:
            risk_reward_score = 1.0 if avg_win > 0 else 0.5
        else:
            risk_reward_ratio = avg_win / avg_loss
            # 1:1 = 0.5 score, 1:2 = 0.75 score, 1:3+ = 1.0 score
            risk_reward_score = min(1.0, risk_reward_ratio / 3.0)
        
        # Combine risk metrics
        risk_score = (drawdown_score * 0.7 + risk_reward_score * 0.3)
        
        return min(1.0, max(0.0, risk_score))
    
    def _calculate_consistency_score(self, metrics: dict) -> float:
        """Calculate consistency component score (0-1)"""
        total_trades = metrics['total_trades']
        wins = metrics['wins']
        losses = metrics['losses']
        
        if total_trades == 0:
            return 0.5  # Neutral score
        
        # Trade frequency (want reasonable number of trades)
        # 20-100 trades is good range
        if total_trades >= 100:
            frequency_score = 1.0
        elif total_trades >= 20:
            # Linear interpolation
            frequency_score = 0.5 + (total_trades - 20) / 80 * 0.5
        else:
            # Below 20 trades, score decreases
            frequency_score = max(0.0, total_trades / 20 * 0.5)
        
        # Profit consistency (how steady the profits are)
        # This is a simplified measure - in reality we'd look at equity curve
        profit_per_trade = metrics['net_profit'] / max(1, total_trades)
        # Positive average = good, but we also want reasonable consistency
        profit_consistency = 1.0 if profit_per_trade > 0 else 0.5 if profit_per_trade >= -10 else 0.0
        
        # Win/loss distribution (more consistent wins = better)
        if wins + losses == 0:
            distribution_score = 0.5
        else:
            win_ratio = wins / (wins + losses)
            # Score higher for win ratios closer to 0.4-0.7 range (realistic)
            distribution_score = 1 - abs(win_ratio - 0.55) * 2
        
        # Combine consistency factors
        consistency_score = (frequency_score * 0.4 + profit_consistency * 0.4 + distribution_score * 0.2)
        
        return min(1.0, max(0.0, consistency_score))
    
    def _calculate_activity_score(self, metrics: dict) -> float:
        """Calculate trading activity component score (0-1)"""
        total_trades = metrics['total_trades']
        
        if total_trades == 0:
            return 0.0
        
        # Activity score based on trade count (20-200 trades is ideal)
        if total_trades >= 200:
            activity_score = 1.0
        elif total_trades >= 20:
            # Linear interpolation
            activity_score = (total_trades - 20) / 180
        else:
            # Below 20 trades, very low score
            activity_score = total_trades / 20 * 0.2
        
        return min(1.0, max(0.0, activity_score))
    
    def _calculate_market_fit_score(self, strategy_id: str, symbol: str, market_condition: dict) -> float:
        """Calculate market condition fit score (0-1)"""
        try:
            instrument_type = market_condition.get('instrument_type', 'FOREX')
            market_condition_type = market_condition.get('market_condition', 'ranging')
            confidence = market_condition.get('confidence', 0.5)
            
            # Strategy-to-market compatibility mapping
            compatibility_map = {
                # Indices
                ('INDEX_BREAKOUT_PRO', 'INDICES'): 1.0,
                ('INDEX_MOMENTUM', 'INDICES'): 0.9,
                ('TURTLE_BREAKOUT', 'INDICES'): 0.7,
                
                # Forex
                ('MA_CROSSOVER', 'FOREX'): 0.9,
                ('RSI_CROSSOVER', 'FOREX'): 0.8,
                ('BOLLINGER_REVERSION', 'FOREX'): 0.85,
                ('TURTLE_BREAKOUT', 'FOREX'): 0.7,
                
                # Gold
                ('QUANTUM_VELOCITY', 'GOLD'): 1.0,
                ('BOLLINGER_REVERSION', 'GOLD'): 0.8,
                ('MERCY_EDGE', 'GOLD'): 0.9,
                
                # Crypto
                ('QUANTUMBOTX_CRYPTO', 'CRYPTO'): 1.0,
                ('DYNAMIC_BREAKOUT', 'CRYPTO'): 0.9,
                ('QUANTUMBOTX_HYBRID', 'CRYPTO'): 0.8,
            }
            
            # Base compatibility score
            base_score = compatibility_map.get((strategy_id, instrument_type), 0.5)
            
            # Adjust for market condition
            strategy_preference = {
                'MA_CROSSOVER': 'trending',
                'RSI_CROSSOVER': 'ranging',
                'TURTLE_BREAKOUT': 'trending',
                'BOLLINGER_REVERSION': 'ranging',
                'INDEX_BREAKOUT_PRO': 'trending',
                'INDEX_MOMENTUM': 'trending',
                'QUANTUM_VELOCITY': 'trending',
                'DYNAMIC_BREAKOUT': 'trending',
                'QUANTUMBOTX_CRYPTO': 'trending',
                'QUANTUMBOTX_HYBRID': 'both'
            }
            
            preferred_condition = strategy_preference.get(strategy_id, 'both')
            
            if preferred_condition == 'both':
                condition_adjustment = 1.0  # Works in both conditions
            elif preferred_condition == market_condition_type:
                condition_adjustment = 1.0  # Perfect match
            else:
                condition_adjustment = 0.7  # Still works but less optimal
            
            # Combine base score with condition adjustment and confidence
            market_fit_score = base_score * condition_adjustment * confidence
            
            return min(1.0, max(0.0, market_fit_score))
            
        except Exception:
            return 0.5  # Neutral score on error
    
    def _default_score(self, strategy_id: str, symbol: str) -> dict:
        """Return default score when calculation fails"""
        return {
            'composite_score': 0.5,
            'components': {
                'profitability': 0.5,
                'risk_control': 0.5,
                'consistency': 0.5,
                'activity_level': 0.5,
                'market_fit': 0.5
            },
            'metrics': {},
            'strategy_id': strategy_id,
            'symbol': symbol,
            'timestamp': datetime.now().isoformat()
        }
    
    def rank_strategy_combinations(self, performance_scores: List[dict]) -> List[dict]:
        """
        Rank strategy/instrument combinations by composite score
        
        Args:
            performance_scores: List of performance score dictionaries
            
        Returns:
            List[dict]: Ranked combinations sorted by composite score (highest first)
        """
        # Sort by composite score (descending)
        ranked_combinations = sorted(
            performance_scores, 
            key=lambda x: x['composite_score'], 
            reverse=True
        )
        
        # Add rank numbers
        for i, combination in enumerate(ranked_combinations):
            combination['rank'] = i + 1
        
        return ranked_combinations

# Global instance
performance_scorer = PerformanceScorer()

def calculate_strategy_score(backtest_results: dict, market_condition: dict, 
                           strategy_id: str, symbol: str) -> dict:
    """
    Convenience function to calculate strategy performance score
    
    Args:
        backtest_results: Backtest results
        market_condition: Market condition analysis
        strategy_id: Strategy identifier
        symbol: Trading symbol
        
    Returns:
        dict: Performance score and ranking
    """
    return performance_scorer.calculate_performance_score(
        backtest_results, market_condition, strategy_id, symbol
    )

def rank_strategies(performance_scores: List[dict]) -> List[dict]:
    """
    Convenience function to rank strategy combinations
    
    Args:
        performance_scores: List of performance scores
        
    Returns:
        List[dict]: Ranked strategy combinations
    """
    return performance_scorer.rank_strategy_combinations(performance_scores)