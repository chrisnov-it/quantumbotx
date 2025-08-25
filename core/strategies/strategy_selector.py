# core/strategies/strategy_selector.py
"""
🎯 Smart Strategy Selector for Beginners
Helps new traders choose the right strategy based on their experience
"""

from .beginner_defaults import BEGINNER_DEFAULTS, STRATEGY_RECOMMENDATIONS, LEARNING_TIPS

class StrategySelector:
    """Helper class to guide beginners in strategy selection"""
    
    def __init__(self):
        self.strategies = BEGINNER_DEFAULTS
        self.recommendations = STRATEGY_RECOMMENDATIONS
        self.tips = LEARNING_TIPS
    
    def get_beginner_dashboard(self) -> dict:
        """Get complete beginner-friendly dashboard"""
        return {
            'recommended_strategies': self._get_beginner_strategies(),
            'learning_path': self._get_learning_path(),
            'quick_start_guide': self._get_quick_start_guide(),
            'safety_tips': self._get_safety_tips()
        }
    
    def _get_beginner_strategies(self) -> list:
        """Get strategies perfect for beginners"""
        beginner_strategies = []
        
        for strategy_name, info in self.strategies.items():
            if info.get('difficulty') == 'BEGINNER' and info.get('recommended'):
                beginner_strategies.append({
                    'name': strategy_name,
                    'display_name': strategy_name.replace('_', ' ').title(),
                    'description': info['description'],
                    'difficulty': info['difficulty'],
                    'params': info['params'],
                    'explanations': info['explanation'],
                    'complexity_score': len(info['params'])  # Fewer params = simpler
                })
        
        # Sort by complexity (simplest first)
        beginner_strategies.sort(key=lambda x: x['complexity_score'])
        return beginner_strategies
    
    def _get_learning_path(self) -> list:
        """Get progressive learning path"""
        return [
            {
                'level': 'Week 1-2: Foundation',
                'strategy': 'MA_CROSSOVER',
                'goal': 'Learn basic trend following',
                'focus': 'Understand moving averages and crossovers',
                'practice': 'Demo trading with 0.01 lots'
            },
            {
                'level': 'Week 3-4: Momentum',
                'strategy': 'RSI_CROSSOVER', 
                'goal': 'Learn momentum analysis',
                'focus': 'Understand RSI and momentum concepts',
                'practice': 'Combine with moving averages'
            },
            {
                'level': 'Week 5-6: Breakouts',
                'strategy': 'TURTLE_BREAKOUT',
                'goal': 'Learn breakout trading',
                'focus': 'Identify support/resistance levels',
                'practice': 'Practice entry/exit timing'
            },
            {
                'level': 'Month 2: Intermediate',
                'strategy': 'BOLLINGER_REVERSION',
                'goal': 'Learn mean reversion',
                'focus': 'Market cycles and oversold/overbought',
                'practice': 'Different market conditions'
            },
            {
                'level': 'Month 3: Advanced',
                'strategy': 'PULSE_SYNC',
                'goal': 'Multi-indicator analysis',
                'focus': 'Confirmation signals and filtering',
                'practice': 'Strategy combination'
            }
        ]
    
    def _get_quick_start_guide(self) -> dict:
        """Get quick start guide for absolute beginners"""
        return {
            'step_1': {
                'title': 'Choose Your First Strategy',
                'action': 'Start with MA_CROSSOVER',
                'reason': 'Simplest and most educational',
                'settings': 'Use default parameters (10, 30)'
            },
            'step_2': {
                'title': 'Set Safe Parameters',
                'action': 'Lot size: 0.01, Stop Loss: 50 pips, Take Profit: 100 pips',
                'reason': 'Protect your capital while learning',
                'settings': 'Risk only 1-2% per trade'
            },
            'step_3': {
                'title': 'Start with Demo',
                'action': 'Trade demo account for at least 1 month',
                'reason': 'Learn without risking real money',
                'settings': 'Treat demo like real money'
            },
            'step_4': {
                'title': 'Track Everything',
                'action': 'Keep a trading journal',
                'reason': 'Learn from both wins and losses',
                'settings': 'Record entry/exit reasons'
            },
            'step_5': {
                'title': 'Gradual Progression',
                'action': 'Master one strategy before trying others',
                'reason': 'Deep knowledge beats shallow knowledge',
                'settings': 'Aim for 60%+ win rate on demo'
            }
        }
    
    def _get_safety_tips(self) -> list:
        """Get essential safety tips for beginners"""
        return [
            "🛡️ NEVER risk more than 2% of your account per trade",
            "📊 ALWAYS backtest strategies before live trading",
            "💰 Start with micro lots (0.01) while learning",
            "📈 Demo trade for at least 30 days before going live",
            "🎯 Set stop losses on EVERY trade - no exceptions",
            "📚 Focus on learning, not making money initially",
            "⏰ Trade only during your local market hours",
            "🔄 Review and analyze every trade (wins AND losses)",
            "💡 Use economic calendar to avoid high-impact news",
            "🎨 Master ONE strategy before trying others"
        ]
    
    def get_strategy_for_market(self, market_type: str, experience_level: str = 'BEGINNER') -> dict:
        """Recommend strategy based on market type and experience"""
        recommendations = {
            'FOREX': {
                'BEGINNER': 'MA_CROSSOVER',
                'INTERMEDIATE': 'RSI_CROSSOVER',
                'ADVANCED': 'PULSE_SYNC'
            },
            'GOLD': {
                'BEGINNER': 'TURTLE_BREAKOUT',
                'INTERMEDIATE': 'BOLLINGER_REVERSION',
                'ADVANCED': 'QUANTUM_VELOCITY'
            },
            'CRYPTO': {
                'BEGINNER': 'MA_CROSSOVER',  # Keep simple for crypto beginners
                'INTERMEDIATE': 'RSI_CROSSOVER',
                'ADVANCED': 'QUANTUMBOTX_CRYPTO'
            }
        }
        
        strategy_name = recommendations.get(market_type.upper(), {}).get(experience_level.upper(), 'MA_CROSSOVER')
        return {
            'recommended_strategy': strategy_name,
            'market_type': market_type,
            'experience_level': experience_level,
            'strategy_info': self.strategies.get(strategy_name, {}),
            'reasoning': f"Best {experience_level.lower()} strategy for {market_type.upper()} trading"
        }
    
    def validate_parameters(self, strategy_name: str, params: dict) -> dict:
        """Validate if parameters are beginner-safe"""
        strategy_info = self.strategies.get(strategy_name, {})
        beginner_params = strategy_info.get('params', {})
        
        warnings = []
        suggestions = []
        
        for param_name, param_value in params.items():
            if param_name in beginner_params:
                beginner_value = beginner_params[param_name]
                
                # Check if significantly different from beginner defaults
                if isinstance(param_value, (int, float)) and isinstance(beginner_value, (int, float)):
                    difference_pct = abs(param_value - beginner_value) / beginner_value * 100
                    
                    if difference_pct > 50:  # More than 50% different
                        warnings.append(f"{param_name}: {param_value} is very different from beginner-safe value ({beginner_value})")
                        suggestions.append(f"Consider using {param_name}: {beginner_value} while learning")
        
        return {
            'is_beginner_safe': len(warnings) == 0,
            'warnings': warnings,
            'suggestions': suggestions,
            'beginner_params': beginner_params
        }

# Convenience functions
def get_beginner_strategy_info(strategy_name: str) -> dict:
    """Quick access to beginner strategy info"""
    selector = StrategySelector()
    return selector.strategies.get(strategy_name, {})

def get_recommended_strategies_for_level(level: str) -> list:
    """Get strategies recommended for experience level"""
    return STRATEGY_RECOMMENDATIONS.get(level.upper(), [])

def is_strategy_beginner_friendly(strategy_name: str) -> bool:
    """Check if strategy is beginner-friendly"""
    strategy_info = BEGINNER_DEFAULTS.get(strategy_name, {})
    return strategy_info.get('difficulty') == 'BEGINNER' and strategy_info.get('recommended', False)