# core/routes/api_bots.py

import json
import logging
import os
from types import SimpleNamespace
from flask import Blueprint, jsonify, request
from core.bots.controller import (
    mulai_bot,
    hentikan_bot,
    ambil_semua_bot,
    shutdown_all_bots,
    get_bot_instance_by_id,
)
from core.db import queries
from core.utils import market_data
from core.strategies.strategy_map import STRATEGY_MAP, resolve_strategy_class

api_bots = Blueprint('api_bots', __name__)
logger = logging.getLogger(__name__)


def is_strategy_switcher_enabled():
    """Read strategy switcher feature flag from env."""
    return os.getenv('ENABLE_STRATEGY_SWITCHER', '0').strip().lower() in ('1', 'true', 'yes', 'on')


def _normalize_param_type(raw_type):
    """Map strategy param types into HTML input types expected by current UI."""
    raw = (raw_type or '').strip().lower()
    if raw in ('int', 'integer', 'float', 'number', 'decimal'):
        return 'number'
    if raw in ('bool', 'boolean'):
        return 'text'
    if raw in ('string', 'str', 'text'):
        return 'text'
    return 'number'


def _normalize_strategy_param(param):
    """Normalize mixed strategy param schemas to a stable frontend shape."""
    if not isinstance(param, dict):
        return None

    name = param.get('name')
    if not name:
        return None

    normalized = {
        'name': name,
        'label': param.get('label') or param.get('display_name') or name,
        'type': _normalize_param_type(param.get('type')),
        'default': param.get('default', ''),
    }

    if 'step' in param:
        normalized['step'] = param['step']
    elif str(param.get('type', '')).lower() in ('float', 'decimal'):
        normalized['step'] = 0.1

    return normalized


def _iter_unique_strategies():
    """Yield canonical strategy id/class pairs and skip alias duplicates."""
    seen_classes = set()
    for strategy_id, strategy_class in STRATEGY_MAP.items():
        if strategy_class in seen_classes:
            continue
        seen_classes.add(strategy_class)
        yield strategy_id, strategy_class


# --- CRUD Endpoints ---

@api_bots.route('/api/strategies', methods=['GET'])
def get_strategies():
    """Return strategy list for bot form and backtesting dropdown."""
    strategies = []
    for strategy_id, strategy_class in _iter_unique_strategies():
        name = getattr(strategy_class, 'name', strategy_id)
        description = getattr(strategy_class, 'description', '')
        strategies.append({
            'id': strategy_id,
            'name': name,
            'description': description,
        })
    return jsonify(strategies)


@api_bots.route('/api/strategies/<strategy_id>/params', methods=['GET'])
def get_strategy_params(strategy_id):
    """Return definable params for a single strategy."""
    strategy_class = resolve_strategy_class(strategy_id)
    if not strategy_class:
        return jsonify({"error": "Strategy not found"}), 404

    try:
        raw_params = strategy_class.get_definable_params() or []
    except Exception as e:
        logger.error("Failed reading params for strategy %s: %s", strategy_id, e)
        return jsonify({"error": "Failed to load strategy params"}), 500

    normalized_params = []
    for param in raw_params:
        normalized = _normalize_strategy_param(param)
        if normalized is not None:
            normalized_params.append(normalized)

    return jsonify(normalized_params)

@api_bots.route('/api/bots', methods=['GET'])
def get_bots():
    """Get all bots"""
    bots = queries.get_all_bots()
    # Parse strategy_params JSON string to dict for frontend
    for bot in bots:
        if isinstance(bot.get('strategy_params'), str):
            try:
                bot['strategy_params'] = json.loads(bot['strategy_params'])
            except:
                bot['strategy_params'] = {}
    return jsonify(bots)

@api_bots.route('/api/bots/<int:bot_id>', methods=['GET'])
def get_bot_detail(bot_id):
    """Get single bot details"""
    bot = queries.get_bot_by_id(bot_id)
    if not bot:
        return jsonify({"error": "Bot not found"}), 404
        
    # Parse strategy_params
    if isinstance(bot.get('strategy_params'), str):
        try:
            bot['strategy_params'] = json.loads(bot['strategy_params'])
        except:
            bot['strategy_params'] = {}
            
    return jsonify(bot)

@api_bots.route('/api/bots', methods=['POST'])
def create_bot():
    """Create a new bot"""
    data = request.json
    try:
        # Extract fields
        name = data.get('name')
        market = data.get('market')
        # Handle risk_percent mapping to lot_size if needed, or just use passed value
        lot_size = data.get('risk_percent', data.get('lot_size', 0.01))
        sl_pips = data.get('sl_atr_multiplier', data.get('sl_pips', 0))
        tp_pips = data.get('tp_atr_multiplier', data.get('tp_pips', 0))
        timeframe = data.get('timeframe', 'H1')
        interval = data.get('check_interval_seconds', 60)
        strategy = data.get('strategy')
        strategy_params = json.dumps(data.get('params', {}))
        enable_strategy_switching = 1 if data.get('enable_strategy_switching') else 0
        if not is_strategy_switcher_enabled():
            enable_strategy_switching = 0

        bot_id = queries.add_bot(
            name, market, lot_size, sl_pips, tp_pips, timeframe, interval, 
            strategy, strategy_params, enable_strategy_switching
        )
        
        if bot_id:
            return jsonify({"message": "Bot created successfully", "id": bot_id}), 201
        else:
            return jsonify({"error": "Failed to create bot"}), 500
    except Exception as e:
        logger.error(f"Error creating bot: {e}")
        return jsonify({"error": str(e)}), 500

@api_bots.route('/api/bots/<int:bot_id>', methods=['PUT'])
def update_bot_route(bot_id):
    """Update an existing bot"""
    data = request.json
    try:
        # Extract fields
        name = data.get('name')
        market = data.get('market')
        lot_size = data.get('risk_percent', data.get('lot_size'))
        sl_pips = data.get('sl_atr_multiplier', data.get('sl_pips'))
        tp_pips = data.get('tp_atr_multiplier', data.get('tp_pips'))
        timeframe = data.get('timeframe')
        interval = data.get('check_interval_seconds')
        strategy = data.get('strategy')
        strategy_params = json.dumps(data.get('params', {}))
        enable_strategy_switching = 1 if data.get('enable_strategy_switching') else 0
        if not is_strategy_switcher_enabled():
            enable_strategy_switching = 0

        success = queries.update_bot(
            bot_id, name, market, lot_size, sl_pips, tp_pips, timeframe, interval, 
            strategy, strategy_params, enable_strategy_switching
        )
        
        if success:
            return jsonify({"message": "Bot updated successfully"})
        else:
            return jsonify({"error": "Failed to update bot"}), 500
    except Exception as e:
        logger.error(f"Error updating bot: {e}")
        return jsonify({"error": str(e)}), 500

@api_bots.route('/api/bots/<int:bot_id>', methods=['DELETE'])
def delete_bot_route(bot_id):
    """Delete a bot"""
    try:
        # Stop bot first if running
        hentikan_bot(bot_id)
        
        success = queries.delete_bot(bot_id)
        if success:
            return jsonify({"message": "Bot deleted successfully"})
        else:
            return jsonify({"error": "Failed to delete bot"}), 500
    except Exception as e:
        logger.error(f"Error deleting bot: {e}")
        return jsonify({"error": str(e)}), 500

# --- Control Endpoints ---

@api_bots.route('/api/bots/<int:bot_id>/start', methods=['POST'])
@api_bots.route('/api/bots/start', methods=['POST']) # Legacy support
def start_bot(bot_id=None):
    if not bot_id:
        data = request.json
        bot_id = data.get('id')
    
    bot_data = queries.get_bot_by_id(bot_id)
    if not bot_data:
        return jsonify({"status": "error", "message": "Bot tidak ditemukan"}), 404

    success, message = mulai_bot(bot_id)
    if success:
        return jsonify({"status": "success", "message": message})
    else:
        return jsonify({"status": "error", "message": message}), 500

@api_bots.route('/api/bots/<int:bot_id>/stop', methods=['POST'])
@api_bots.route('/api/bots/stop', methods=['POST']) # Legacy support
def stop_bot_route(bot_id=None):
    if not bot_id:
        data = request.json
        bot_id = data.get('id')
    
    success, message = hentikan_bot(bot_id)
    if success:
        return jsonify({"status": "success", "message": message})
    else:
        return jsonify({"status": "error", "message": message}), 500

@api_bots.route('/api/bots/start_all', methods=['POST'])
def start_all_bots_route():
    # Logic to start all paused bots
    # This requires a controller function or loop here
    # For now, placeholder
    return jsonify({"message": "Not implemented yet"}), 501

@api_bots.route('/api/bots/stop_all', methods=['POST'])
def stop_all_bots_route():
    shutdown_all_bots()
    return jsonify({"message": "All bots stopped"})

# --- Detail & Analysis Endpoints ---

@api_bots.route('/api/bots/<int:bot_id>/history', methods=['GET'])
def get_bot_history(bot_id):
    """Get trade history for a bot"""
    history = queries.get_history_by_bot_id(bot_id)
    return jsonify(history)

@api_bots.route('/api/bots/<int:bot_id>/analysis', methods=['GET'])
def get_bot_analysis(bot_id):
    """Run strategy analysis for a bot and return result"""
    try:
        active_bot = get_bot_instance_by_id(bot_id)
        if active_bot and getattr(active_bot, "last_analysis", None):
            analysis = active_bot.last_analysis
            if isinstance(analysis, tuple) and len(analysis) >= 2:
                return jsonify({
                    "signal": analysis[0],
                    "explanation": analysis[1],
                    "price": None,
                    "position_qty": getattr(active_bot, "last_position_qty", None),
                    "cooldown_remaining_candles": getattr(active_bot, "last_cooldown_remaining", None),
                    "last_action": getattr(active_bot, "last_action_result", None),
                })
            if isinstance(analysis, dict):
                return jsonify({
                    "signal": analysis.get("signal", "HOLD"),
                    "explanation": analysis.get("explanation", ""),
                    "price": analysis.get("price"),
                    "position_qty": getattr(active_bot, "last_position_qty", None),
                    "cooldown_remaining_candles": getattr(active_bot, "last_cooldown_remaining", None),
                    "last_action": getattr(active_bot, "last_action_result", None),
                })

        bot = queries.get_bot_by_id(bot_id)
        if not bot:
            return jsonify({"error": "Bot not found"}), 404
            
        symbol = bot['market']
        timeframe = bot['timeframe']
        strategy_name = bot['strategy']
        
        # Load Strategy
        strategy_class = resolve_strategy_class(strategy_name)
        if not strategy_class:
            return jsonify({"error": "Strategy not found", "signal": "ERROR"}), 400
            
        # Fetch Data using Market Data Facade
        df = market_data.get_market_rates(symbol, timeframe, 100)
        if df is None or df.empty:
            return jsonify({"error": "No market data", "signal": "NO DATA"}), 404
            
        # Instantiate and Analyze
        strategy_params = {}
        if isinstance(bot.get('strategy_params'), str):
            try:
                strategy_params = json.loads(bot['strategy_params'])
            except:
                pass
        elif isinstance(bot.get('strategy_params'), dict):
            strategy_params = bot['strategy_params']
            
        # Strategy contract in this codebase uses BaseStrategy(bot_instance, params)
        # Build a lightweight bot context so strategy code can still reference bot attrs.
        bot_ctx = SimpleNamespace(
            market=symbol,
            market_for_mt5=symbol,
            timeframe=timeframe,
            id=bot_id,
            name=bot.get('name', f'bot-{bot_id}')
        )
        strategy = strategy_class(bot_instance=bot_ctx, params=strategy_params)
        analysis = strategy.analyze(df)

        # Backward compatibility: some old strategy implementations may return tuples.
        if isinstance(analysis, tuple) and len(analysis) >= 2:
            signal, explanation = analysis[0], analysis[1]
            price = df['close'].iloc[-1] if not df.empty else 0
        elif isinstance(analysis, dict):
            signal = analysis.get('signal', 'HOLD')
            explanation = analysis.get('explanation', '')
            price = analysis.get('price', df['close'].iloc[-1] if not df.empty else 0)
        else:
            signal = 'ERROR'
            explanation = f'Invalid strategy response type: {type(analysis).__name__}'
            price = df['close'].iloc[-1] if not df.empty else 0
        
        # Return analysis result
        return jsonify({
            "signal": signal,
            "explanation": explanation,
            "price": price,
            "rsi": df['RSI'].iloc[-1] if 'RSI' in df.columns else None,
            "position_qty": None,
            "cooldown_remaining_candles": None,
            "last_action": None,
        })
        
    except Exception as e:
        logger.error(f"Error in bot analysis: {e}")
        return jsonify({"error": str(e), "signal": "ERROR"}), 500
