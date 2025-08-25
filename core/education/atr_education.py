# core/education/atr_education.py
"""
📚 ATR-Based Risk Management Education for Beginners
Helps new traders understand the brilliant ATR system implementation
"""

class ATREducationHelper:
    """Educational helper for ATR-based risk management"""
    
    def __init__(self):
        self.examples = self._create_examples()
        self.explanations = self._create_explanations()
    
    def _create_examples(self):
        """Create real-world examples of ATR-based risk management"""
        return {
            'EURUSD': {
                'typical_atr': 0.0050,  # 50 pips
                'safe_risk': 1.0,       # 1%
                'sl_multiplier': 2.0,   # 2x ATR = 100 pips SL
                'tp_multiplier': 4.0,   # 4x ATR = 200 pips TP
                'example_account': 10000,
                'calculated_lot': 0.20,
                'max_loss': 100,        # $100 max loss
                'explanation': 'EURUSD is stable - normal parameters work well'
            },
            'XAUUSD': {
                'typical_atr': 15.0,    # $15 ATR (very high!)
                'safe_risk': 1.0,       # Capped at 1%
                'sl_multiplier': 1.0,   # Capped at 1x ATR = $15 SL
                'tp_multiplier': 2.0,   # Capped at 2x ATR = $30 TP
                'example_account': 10000,
                'calculated_lot': 0.02, # Fixed small lot
                'max_loss': 30,         # $30 max loss (safe!)
                'explanation': 'Gold is volatile - system automatically protects you!'
            },
            'BTCUSD': {
                'typical_atr': 500.0,   # $500 ATR (crypto volatility)
                'safe_risk': 0.5,       # Lower risk for crypto
                'sl_multiplier': 1.5,   # Moderate SL
                'tp_multiplier': 3.0,   # Conservative TP
                'example_account': 10000,
                'calculated_lot': 0.01, # Very small lot
                'max_loss': 75,         # $75 max loss
                'explanation': 'Crypto is ultra-volatile - extra conservative approach'
            }
        }
    
    def _create_explanations(self):
        """Create beginner-friendly explanations"""
        return {
            'atr_concept': {
                'title': 'What is ATR (Average True Range)?',
                'simple': 'ATR measures how much a price typically moves in one period',
                'detailed': [
                    '📊 ATR = Average daily price movement',
                    '🔍 High ATR = Volatile market (big price swings)',
                    '🔍 Low ATR = Calm market (small price movements)',
                    '🎯 Used to set realistic stop losses and take profits',
                    '💡 Example: If EUR/USD ATR = 50 pips, expect ~50 pip daily moves'
                ],
                'visual_analogy': 'Think of ATR like a speedometer for market volatility'
            },
            'risk_percentage': {
                'title': 'Risk Percentage - Your Safety Net',
                'simple': 'Maximum % of your account you\'re willing to lose per trade',
                'detailed': [
                    '🛡️ 1% risk = $100 max loss on $10,000 account',
                    '🎯 Professional traders rarely risk more than 1-2%',
                    '📉 Even with 10 losses in a row at 1%, you only lose 10%',
                    '💰 Compared to 10% risk = account blown in 2 bad trades',
                    '🏆 Consistent small risks = long-term success'
                ],
                'visual_analogy': 'Like wearing a seatbelt - protects you when things go wrong'
            },
            'atr_multipliers': {
                'title': 'ATR Multipliers - Smart Distance Setting',
                'simple': 'How many ATRs away to place your stop loss and take profit',
                'detailed': [
                    '🔻 SL at 2x ATR = Stop loss at 2 times normal movement',
                    '🔺 TP at 4x ATR = Take profit at 4 times normal movement',
                    '⚖️ This gives 1:2 risk-to-reward ratio (smart!)',
                    '🎲 Accounts for normal market noise vs real moves',
                    '📈 Adapts automatically to each market\'s personality'
                ],
                'visual_analogy': 'Like setting alarm distances based on your running speed'
            },
            'gold_protection': {
                'title': 'Special Gold Protection - Your Guardian Angel',
                'simple': 'Automatic safety system for volatile gold trading',
                'detailed': [
                    '🥇 Gold moves 10x more than forex (extremely dangerous!)',
                    '🛡️ System automatically caps risk at 1% for gold',
                    '📉 Reduces ATR multipliers to prevent big losses',
                    '🚨 Uses tiny lot sizes instead of calculations',
                    '💰 Example: Normal trade risks $100, gold trade risks $30'
                ],
                'visual_analogy': 'Like having training wheels automatically appear on dangerous roads'
            }
        }
    
    def get_interactive_example(self, symbol: str, account_size: float, 
                              risk_percent: float, current_atr: float):
        """Generate interactive example with real calculations"""
        
        # Apply your system's protections
        if 'XAU' in symbol.upper() or 'GOLD' in symbol.upper():
            # Gold protection
            risk_percent = min(risk_percent, 1.0)
            sl_multiplier = min(2.0, 1.0)  # Your system caps at 1.0
            tp_multiplier = min(4.0, 2.0)  # Your system caps at 2.0
            max_lot = 0.03  # Your system's max
            protection_active = True
        else:
            # Normal forex/crypto
            sl_multiplier = 2.0
            tp_multiplier = 4.0
            max_lot = 1.0
            protection_active = False
        
        # Calculate distances
        sl_distance = current_atr * sl_multiplier
        tp_distance = current_atr * tp_multiplier
        
        # Calculate risk
        amount_to_risk = account_size * (risk_percent / 100)
        
        # Simplified lot calculation (your system is more sophisticated)
        if protection_active:
            # Use your fixed lot system for gold
            if risk_percent <= 0.5:
                lot_size = 0.01
            elif risk_percent <= 1.0:
                lot_size = 0.02
            else:
                lot_size = 0.03
        else:
            # Standard calculation for forex
            pip_value = 1.0 if 'JPY' not in symbol else 0.01
            lot_size = min(amount_to_risk / (sl_distance * 100), max_lot)
            lot_size = max(0.01, round(lot_size, 2))
        
        # Calculate actual risk
        actual_risk = sl_distance * lot_size * 100  # Simplified
        
        return {
            'symbol': symbol,
            'account_size': account_size,
            'risk_percent_input': risk_percent,
            'risk_percent_actual': min(risk_percent, 1.0) if protection_active else risk_percent,
            'current_atr': current_atr,
            'sl_multiplier': sl_multiplier,
            'tp_multiplier': tp_multiplier,
            'sl_distance': sl_distance,
            'tp_distance': tp_distance,
            'lot_size': lot_size,
            'amount_to_risk_target': amount_to_risk,
            'actual_risk_amount': actual_risk,
            'protection_active': protection_active,
            'risk_to_reward_ratio': f"1:{tp_multiplier/sl_multiplier:.1f}",
            'explanation': self._generate_explanation(symbol, protection_active, 
                                                    risk_percent, actual_risk, amount_to_risk)
        }
    
    def _generate_explanation(self, symbol, protection_active, 
                            target_risk, actual_risk, target_amount):
        """Generate personalized explanation"""
        explanations = []
        
        if protection_active:
            explanations.append("🥇 GOLD PROTECTION ACTIVE!")
            explanations.append(f"   System automatically reduced your risk for safety")
            explanations.append(f"   This prevents the catastrophic losses that destroy beginner accounts")
        
        explanations.append(f"💰 You wanted to risk: ${target_amount:.0f}")
        explanations.append(f"🛡️ System will actually risk: ${actual_risk:.0f}")
        
        if actual_risk < target_amount:
            savings = target_amount - actual_risk
            explanations.append(f"✅ Safety system saved you ${savings:.0f} of potential loss!")
        
        explanations.append(f"📊 This is how professional traders manage risk")
        explanations.append(f"🎯 Better to make small consistent profits than blow up your account")
        
        return explanations
    
    def get_beginner_tutorial(self):
        """Get complete beginner tutorial on ATR-based risk management"""
        return {
            'title': '🎓 ATR-Based Risk Management Tutorial',
            'steps': [
                {
                    'step': 1,
                    'title': 'Understanding ATR',
                    'content': self.explanations['atr_concept'],
                    'practice': 'Look at EURUSD vs XAUUSD ATR values - notice the huge difference!'
                },
                {
                    'step': 2,
                    'title': 'Risk Percentage Mastery',
                    'content': self.explanations['risk_percentage'],
                    'practice': 'Calculate: If you have $1000 and risk 2%, what\'s your max loss?'
                },
                {
                    'step': 3,
                    'title': 'ATR Multiplier Magic',
                    'content': self.explanations['atr_multipliers'],
                    'practice': 'Try different multipliers and see how it affects risk-to-reward'
                },
                {
                    'step': 4,
                    'title': 'Gold Protection System',
                    'content': self.explanations['gold_protection'],
                    'practice': 'Compare EURUSD vs XAUUSD position sizing with same parameters'
                }
            ],
            'examples': self.examples,
            'key_takeaways': [
                '🎯 ATR adapts to market conditions automatically',
                '🛡️ Risk % protects your account from catastrophic losses',
                '⚖️ ATR multipliers give you proper risk-to-reward ratios',
                '🥇 Special protections prevent beginner mistakes on volatile instruments',
                '📈 System does the math so you can focus on trading psychology'
            ]
        }
    
    def validate_beginner_parameters(self, symbol: str, risk_percent: float, 
                                   sl_multiplier: float, tp_multiplier: float):
        """Validate parameters and provide beginner-friendly feedback"""
        warnings = []
        suggestions = []
        
        # Risk percentage validation
        if risk_percent > 2.0:
            warnings.append(f"Risk {risk_percent}% is too high for beginners")
            suggestions.append("Start with 0.5-1.0% risk while learning")
        
        # ATR multiplier validation
        if sl_multiplier < 1.5:
            warnings.append("SL multiplier too small - may hit random noise")
            suggestions.append("Use 2.0x ATR for SL to avoid false signals")
        
        if tp_multiplier < sl_multiplier * 1.5:
            warnings.append("Risk-to-reward ratio is poor")
            suggestions.append("TP should be at least 1.5x your SL distance")
        
        # Symbol-specific advice
        if 'XAU' in symbol.upper() or 'GOLD' in symbol.upper():
            if risk_percent > 1.0:
                warnings.append("Gold is extremely volatile - system will cap risk at 1%")
            suggestions.append("Gold moves fast - perfect for learning ATR concepts!")
        
        return {
            'is_beginner_safe': len(warnings) == 0,
            'warnings': warnings,
            'suggestions': suggestions,
            'will_be_protected': 'XAU' in symbol.upper() or 'GOLD' in symbol.upper()
        }

# Helper functions for easy integration
def get_atr_tutorial():
    """Quick access to ATR tutorial"""
    helper = ATREducationHelper()
    return helper.get_beginner_tutorial()

def explain_atr_example(symbol, account_size, risk_percent, atr_value):
    """Quick access to interactive example"""
    helper = ATREducationHelper()
    return helper.get_interactive_example(symbol, account_size, risk_percent, atr_value)

def validate_beginner_atr_settings(symbol, risk_percent, sl_mult, tp_mult):
    """Quick validation of beginner ATR settings"""
    helper = ATREducationHelper()
    return helper.validate_beginner_parameters(symbol, risk_percent, sl_mult, tp_mult)