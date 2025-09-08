# core/routes/api_strategy_switcher.py
"""
API endpoints for the automatic strategy switching system

This module provides REST API endpoints for monitoring and controlling
the automatic strategy switching system.
"""

from flask import Blueprint, jsonify, request
import pandas as pd
import os
from datetime import datetime

from ..strategies.strategy_switcher import (
    strategy_switcher, 
    evaluate_strategy_switch, 
    get_switcher_status, 
    get_recent_switches
)
from ..strategies.market_condition_detector import get_market_condition
from ..strategies.performance_scorer import calculate_strategy_score, rank_strategies
from ..backtesting.enhanced_engine import run_enhanced_backtest
from ..strategies.strategy_map import STRATEGY_MAP

# Create blueprint
api_strategy_switcher = Blueprint('api_strategy_switcher', __name__, url_prefix='/api/strategy-switcher')

@api_strategy_switcher.route('/status', methods=['GET'])
def get_status():
    """Get current strategy switcher status"""
    try:
        status = get_switcher_status()
        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_strategy_switcher.route('/recent-switches', methods=['GET'])
def get_recent_switches_api():
    """Get recent strategy switches"""
    try:
        count = request.args.get('count', 10, type=int)
        switches = get_recent_switches(count)
        return jsonify({
            'success': True,
            'data': switches
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_strategy_switcher.route('/evaluate', methods=['POST'])
def evaluate_switch():
    """Manually trigger strategy evaluation"""
    try:
        # Load current market data for monitored instruments
        current_data = {}
        data_directory = strategy_switcher.config.get('data_directory', 'lab/backtest_data')
        
        for symbol in strategy_switcher.monitored_instruments:
            file_path = os.path.join(data_directory, f'{symbol}_H1_data.csv')
            if os.path.exists(file_path):
                try:
                    df = pd.read_csv(file_path, parse_dates=['time'])
                    current_data[symbol] = df
                except Exception as e:
                    print(f"Error loading data for {symbol}: {e}")
                    continue
        
        if not current_data:
            return jsonify({
                'success': False,
                'error': 'No market data available for evaluation'
            }), 400
        
        # Evaluate and potentially switch
        switch_decision = evaluate_strategy_switch(current_data)
        
        return jsonify({
            'success': True,
            'data': {
                'switch_decision': switch_decision,
                'evaluation_time': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_strategy_switcher.route('/rankings', methods=['GET'])
def get_strategy_rankings():
    """Get current strategy performance rankings"""
    try:
        # Load current market data
        current_data = {}
        data_directory = strategy_switcher.config.get('data_directory', 'lab/backtest_data')
        
        for symbol in strategy_switcher.monitored_instruments:
            file_path = os.path.join(data_directory, f'{symbol}_H1_data.csv')
            if os.path.exists(file_path):
                try:
                    df = pd.read_csv(file_path, parse_dates=['time'])
                    current_data[symbol] = df
                except Exception as e:
                    print(f"Error loading data for {symbol}: {e}")
                    continue
        
        if not current_data:
            return jsonify({
                'success': False,
                'error': 'No market data available for evaluation'
            }), 400
        
        # Evaluate all combinations
        performance_scores = []
        
        for symbol, df in current_data.items():
            if df.empty:
                continue
            
            # Get market condition for this symbol
            market_condition = get_market_condition(df, symbol)
            
            # Test each strategy on this symbol
            for strategy_id in strategy_switcher.test_strategies:
                if strategy_id not in STRATEGY_MAP:
                    continue
                
                try:
                    # Run backtest with recent data
                    test_df = df.tail(strategy_switcher.config['performance_evaluation_period']).copy()
                    
                    # Get strategy-specific parameters
                    strategy_params = strategy_switcher._get_strategy_parameters(strategy_id, symbol)
                    
                    # Run backtest
                    backtest_results = run_enhanced_backtest(
                        strategy_id,
                        strategy_params,
                        test_df,
                        symbol_name=symbol
                    )
                    
                    if 'error' in backtest_results:
                        continue
                    
                    # Calculate performance score
                    score = calculate_strategy_score(
                        backtest_results, market_condition, strategy_id, symbol
                    )
                    
                    performance_scores.append(score)
                    
                except Exception as e:
                    print(f"Error evaluating {strategy_id}/{symbol}: {e}")
                    continue
        
        # Rank combinations
        ranked_combinations = rank_strategies(performance_scores)
        
        return jsonify({
            'success': True,
            'data': ranked_combinations[:20]  # Top 20 rankings
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_strategy_switcher.route('/market-conditions', methods=['GET'])
def get_market_conditions():
    """Get current market conditions for all monitored instruments"""
    try:
        # Load current market data
        current_data = {}
        data_directory = strategy_switcher.config.get('data_directory', 'lab/backtest_data')
        
        for symbol in strategy_switcher.monitored_instruments:
            file_path = os.path.join(data_directory, f'{symbol}_H1_data.csv')
            if os.path.exists(file_path):
                try:
                    df = pd.read_csv(file_path, parse_dates=['time'])
                    current_data[symbol] = df
                except Exception as e:
                    print(f"Error loading data for {symbol}: {e}")
                    continue
        
        market_conditions = {}
        
        for symbol, df in current_data.items():
            if not df.empty:
                condition = get_market_condition(df, symbol)
                market_conditions[symbol] = condition
        
        return jsonify({
            'success': True,
            'data': market_conditions
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_strategy_switcher.route('/configuration', methods=['GET', 'PUT'])
def manage_configuration():
    """Get or update strategy switcher configuration"""
    if request.method == 'GET':
        try:
            return jsonify({
                'success': True,
                'data': strategy_switcher.config
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    elif request.method == 'PUT':
        try:
            new_config = request.get_json()
            
            if not new_config:
                return jsonify({
                    'success': False,
                    'error': 'No configuration data provided'
                }), 400
            
            # Update configuration
            strategy_switcher.config.update(new_config)
            
            # Save to file
            try:
                with open(strategy_switcher.config_file, 'w') as f:
                    import json
                    json.dump(strategy_switcher.config, f, indent=2)
            except Exception as e:
                print(f"Warning: Could not save configuration to file: {e}")
            
            return jsonify({
                'success': True,
                'data': strategy_switcher.config,
                'message': 'Configuration updated successfully'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

@api_strategy_switcher.route('/test-combination', methods=['POST'])
def test_strategy_combination():
    """Test a specific strategy/symbol combination"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No test data provided'
            }), 400
        
        strategy_id = data.get('strategy_id')
        symbol = data.get('symbol')
        
        if not strategy_id or not symbol:
            return jsonify({
                'success': False,
                'error': 'Both strategy_id and symbol are required'
            }), 400
        
        if strategy_id not in STRATEGY_MAP:
            return jsonify({
                'success': False,
                'error': f'Strategy {strategy_id} not found'
            }), 404
        
        # Load data for symbol
        data_directory = strategy_switcher.config.get('data_directory', 'lab/backtest_data')
        file_path = os.path.join(data_directory, f'{symbol}_H1_data.csv')
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': f'Data file for {symbol} not found'
            }), 404
        
        try:
            df = pd.read_csv(file_path, parse_dates=['time'])
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Error loading data for {symbol}: {e}'
            }), 500
        
        if df.empty:
            return jsonify({
                'success': False,
                'error': f'No data available for {symbol}'
            }), 400
        
        # Get market condition
        market_condition = get_market_condition(df, symbol)
        
        # Get strategy parameters
        strategy_params = strategy_switcher._get_strategy_parameters(strategy_id, symbol)
        
        # Run backtest
        test_df = df.tail(strategy_switcher.config['performance_evaluation_period']).copy()
        backtest_results = run_enhanced_backtest(
            strategy_id,
            strategy_params,
            test_df,
            symbol_name=symbol
        )
        
        if 'error' in backtest_results:
            return jsonify({
                'success': False,
                'error': backtest_results['error']
            }), 500
        
        # Calculate performance score
        score = calculate_strategy_score(
            backtest_results, market_condition, strategy_id, symbol
        )
        
        return jsonify({
            'success': True,
            'data': {
                'backtest_results': backtest_results,
                'performance_score': score,
                'market_condition': market_condition
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_strategy_switcher.route('/manual-trigger', methods=['POST'])
def manual_trigger():
    """Manually trigger strategy evaluation and switch if needed"""
    try:
        # Load current market data for monitored instruments
        current_data = {}
        data_directory = strategy_switcher.config.get('data_directory', 'lab/backtest_data')
        
        for symbol in strategy_switcher.monitored_instruments:
            file_path = os.path.join(data_directory, f'{symbol}_H1_data.csv')
            if os.path.exists(file_path):
                try:
                    df = pd.read_csv(file_path, parse_dates=['time'])
                    current_data[symbol] = df
                except Exception as e:
                    print(f"Error loading data for {symbol}: {e}")
                    continue
        
        if not current_data:
            return jsonify({
                'success': False,
                'error': 'No market data available for evaluation'
            }), 400
        
        # Evaluate and potentially switch
        switch_decision = evaluate_strategy_switch(current_data)
        
        # Create notification about the manual trigger
        from core.db.queries import add_history_log
        if switch_decision:
            action = "MANUAL_STRATEGY_EVALUATION"
            details = f"Manual strategy evaluation completed. Switch decision: {switch_decision['action']}"
        else:
            action = "MANUAL_STRATEGY_EVALUATION"
            details = "Manual strategy evaluation completed. No switch needed."
            
        add_history_log(
            bot_id=0,
            action=action,
            details=details,
            is_notification=True
        )
        
        return jsonify({
            'success': True,
            'data': {
                'switch_decision': switch_decision,
                'evaluation_time': datetime.now().isoformat()
            },
            'message': 'Manual strategy evaluation completed successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
