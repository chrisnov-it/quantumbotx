import json
import logging
import os
import threading
import time
from datetime import datetime
from typing import Optional, Tuple

import pandas as pd

from core.db.queries import add_history_log
from core.strategies.strategy_map import resolve_strategy_class
from core.utils.ccxt_spot import create_spot_exchange, get_spot_mode

logger = logging.getLogger(__name__)


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def _env_int(name: str, default: int = 0) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw.strip())
    except (TypeError, ValueError):
        return default


def _env_str(name: str, default: str = "") -> str:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip()


def _normalize_ccxt_symbol(raw_symbol: str) -> str:
    symbol = (raw_symbol or "").strip().upper().replace("-", "").replace("_", "").replace("/", "")
    if not symbol:
        return raw_symbol
    if "/" in (raw_symbol or ""):
        return raw_symbol.strip().upper()

    quote_candidates = ("USDT", "USDC", "BUSD", "USD", "BTC", "ETH", "BNB", "EUR", "TRY")
    for quote in quote_candidates:
        if symbol.endswith(quote) and len(symbol) > len(quote):
            base = symbol[: -len(quote)]
            return f"{base}/{quote}"
    return raw_symbol.strip().upper()


class CCXTTradingBot(threading.Thread):
    """Minimal CCXT spot-trading bot thread for BROKER_TYPE=CCXT."""

    TF_MAP = {
        "M1": "1m",
        "M5": "5m",
        "M15": "15m",
        "M30": "30m",
        "H1": "1h",
        "H4": "4h",
        "D1": "1d",
    }

    def __init__(
        self,
        id,
        name,
        market,
        risk_percent,
        sl_pips,
        tp_pips,
        timeframe,
        check_interval,
        strategy,
        strategy_params=None,
        status="Dijeda",
        enable_strategy_switching=False,
    ):
        super().__init__()
        self.id = id
        self.name = name
        self.market = market
        self.risk_percent = float(risk_percent or 0)
        self.sl_pips = sl_pips
        self.tp_pips = tp_pips
        self.timeframe = timeframe
        self.check_interval = int(check_interval or 60)
        self.strategy_name = strategy
        self.strategy_params = strategy_params or {}
        self.enable_strategy_switching = enable_strategy_switching
        self.status = status
        self._stop_event = threading.Event()
        self.last_analysis = {"signal": "MEMUAT", "explanation": "CCXT bot sedang memulai..."}
        self.strategy_instance = None
        self.exchange = None
        self.symbol = _normalize_ccxt_symbol(market)
        self.market_for_mt5 = self.symbol  # keep compatibility for strategy code
        self.ccxt_dry_run = _env_bool("CCXT_DRY_RUN", False)
        self.trade_cooldown_candles = max(0, _env_int("CCXT_TRADE_COOLDOWN_CANDLES", 3))
        self.last_trade_candle_open = None
        self.last_action_result = "INIT"
        self.last_position_qty = 0.0
        self.last_cooldown_remaining = 0
        self.loop_log_mode = (_env_str("CCXT_LOOP_LOG_MODE", "transactions").lower() or "transactions")
        self.loop_log_heartbeat_sec = max(0, _env_int("CCXT_LOOP_LOG_HEARTBEAT_SEC", 0))
        self._last_logged_signal = None
        self._last_logged_action = None
        self._last_heartbeat_ts = 0

    def stop(self):
        self._stop_event.set()

    def is_stopped(self):
        return self._stop_event.is_set()

    def log_activity(self, action, details, exc_info=False, is_notification=False):
        try:
            add_history_log(self.id, action, details, is_notification)
            msg = f"Bot {self.id} [{action}]: {details}"
            if exc_info:
                logger.error(msg, exc_info=True)
            else:
                logger.info(msg)
        except Exception as e:
            logger.error(f"Gagal mencatat riwayat untuk bot {self.id}: {e}")

    def _build_exchange(self):
        exchange_id = (os.getenv("EXCHANGE_ID") or os.getenv("CCXT_EXCHANGE") or "binance").strip().lower()
        api_key = (os.getenv("CCXT_API_KEY") or "").strip()
        api_secret = (os.getenv("CCXT_API_SECRET") or "").strip()
        api_password = (os.getenv("CCXT_API_PASSWORD") or "").strip()
        exchange = create_spot_exchange(
            exchange_id=exchange_id,
            api_key=api_key,
            api_secret=api_secret,
            api_password=api_password,
        )

        exchange.load_markets()
        if self.symbol not in exchange.markets:
            raise RuntimeError(f"Symbol '{self.symbol}' tidak tersedia di exchange.")
        return exchange

    def _fetch_rates(self, limit=250) -> pd.DataFrame:
        tf = self.TF_MAP.get((self.timeframe or "").upper(), "1h")
        rows = self.exchange.fetch_ohlcv(self.symbol, timeframe=tf, limit=limit)
        if not rows:
            return pd.DataFrame()
        df = pd.DataFrame(rows, columns=["time", "open", "high", "low", "close", "volume"])
        df["time"] = pd.to_datetime(df["time"], unit="ms", utc=True)
        df.set_index("time", inplace=True)
        return df

    def _get_spot_position_qty(self) -> float:
        base = self.symbol.split("/")[0]
        bal = self.exchange.fetch_balance()
        total = bal.get("total", {}) if isinstance(bal, dict) else {}
        qty = float(total.get(base, 0.0) or 0.0)
        return qty

    def _calc_buy_amount(self) -> Tuple[float, float]:
        quote = self.symbol.split("/")[1]
        ticker = self.exchange.fetch_ticker(self.symbol)
        last = float(ticker.get("last") or ticker.get("ask") or 0.0)
        if last <= 0:
            raise RuntimeError(f"Harga ticker invalid untuk {self.symbol}.")

        bal = self.exchange.fetch_balance()
        quote_total = float((bal.get("total", {}) or {}).get(quote, 0.0) or 0.0)
        spend_quote = max(0.0, quote_total * (self.risk_percent / 100.0))
        if spend_quote <= 0:
            raise RuntimeError(f"Saldo {quote} tidak cukup untuk BUY.")
        amount = spend_quote / last
        return amount, last

    def _place_market_buy(self):
        amount, last = self._calc_buy_amount()
        market = self.exchange.market(self.symbol)
        min_amt = (((market.get("limits") or {}).get("amount") or {}).get("min")) or 0.0
        if amount < float(min_amt or 0.0):
            raise RuntimeError(f"Amount {amount:.8f} < min amount {min_amt} untuk {self.symbol}.")
        amount = float(self.exchange.amount_to_precision(self.symbol, amount))
        if amount <= 0:
            raise RuntimeError("Amount BUY menjadi 0 setelah precision.")

        if self.ccxt_dry_run:
            self.log_activity("DRY BUY", f"[DRY] BUY {self.symbol} amount={amount} @~{last}", is_notification=True)
            return

        order = self.exchange.create_market_buy_order(self.symbol, amount)
        self.log_activity("OPEN BUY", f"BUY {self.symbol} amount={amount} order={order.get('id')}", is_notification=True)

    def _place_market_sell(self):
        qty = self._get_spot_position_qty()
        if qty <= 0:
            return
        qty = float(self.exchange.amount_to_precision(self.symbol, qty))
        if qty <= 0:
            return

        if self.ccxt_dry_run:
            self.log_activity("DRY SELL", f"[DRY] SELL {self.symbol} amount={qty}", is_notification=True)
            return

        order = self.exchange.create_market_sell_order(self.symbol, qty)
        self.log_activity("CLOSE BUY", f"SELL {self.symbol} amount={qty} order={order.get('id')}", is_notification=True)

    def _timeframe_delta(self) -> pd.Timedelta:
        tf = self.TF_MAP.get((self.timeframe or "").upper(), "1h")
        try:
            value = int(tf[:-1])
            unit = tf[-1]
        except (TypeError, ValueError):
            return pd.Timedelta(minutes=1)

        if unit == "m":
            return pd.Timedelta(minutes=value)
        if unit == "h":
            return pd.Timedelta(hours=value)
        if unit == "d":
            return pd.Timedelta(days=value)
        return pd.Timedelta(minutes=1)

    def _cooldown_remaining(self, current_candle) -> int:
        if self.trade_cooldown_candles <= 0 or self.last_trade_candle_open is None or current_candle is None:
            return 0
        tf_delta = self._timeframe_delta()
        if tf_delta <= pd.Timedelta(0):
            return 0
        elapsed = int((current_candle - self.last_trade_candle_open) / tf_delta)
        remaining = self.trade_cooldown_candles - elapsed
        self.last_cooldown_remaining = remaining if remaining > 0 else 0
        return self.last_cooldown_remaining

    def _handle_trade_signal(self, signal: str, has_long: Optional[bool] = None, current_candle=None) -> str:
        signal = (signal or "HOLD").upper()
        if has_long is None:
            has_long = self._get_spot_position_qty() > 0

        if signal in ("BUY", "SELL"):
            remaining = self._cooldown_remaining(current_candle)
            if remaining > 0:
                self.last_action_result = f"{signal} skipped: cooldown {remaining} candle(s) remaining"
                return self.last_action_result

        if signal == "BUY" and not has_long:
            self._place_market_buy()
            self.last_trade_candle_open = current_candle
            self.last_action_result = "BUY executed"
            return self.last_action_result
        elif signal == "SELL" and has_long:
            self._place_market_sell()
            self.last_trade_candle_open = current_candle
            self.last_action_result = "SELL executed"
            return self.last_action_result
        elif signal == "BUY" and has_long:
            self.last_action_result = "BUY skipped: existing spot position detected"
            return self.last_action_result
        elif signal == "SELL" and not has_long:
            self.last_action_result = "SELL skipped: no spot position to close"
            return self.last_action_result
        self.last_action_result = f"{signal} no action"
        return self.last_action_result

    def _should_log_loop(self, signal: str, action_result: str) -> bool:
        mode = self.loop_log_mode
        if mode in ("all", "verbose"):
            return True
        if mode in ("off", "none"):
            return False
        if mode in ("transactions", "trades", "tx"):
            return "executed" in (action_result or "").lower()
        if mode in ("changes", "change"):
            changed = signal != self._last_logged_signal or action_result != self._last_logged_action
            if changed:
                return True
            if self.loop_log_heartbeat_sec > 0:
                now = time.time()
                if now - self._last_heartbeat_ts >= self.loop_log_heartbeat_sec:
                    self._last_heartbeat_ts = now
                    return True
            return False
        # Fallback safe mode
        return "executed" in (action_result or "").lower()

    def run(self):
        self.status = "Aktif"
        self.log_activity("START", f"Bot '{self.name}' dimulai (CCXT {self.symbol}).", is_notification=True)
        logger.info(
            "Bot %s [CONFIG]: symbol=%s timeframe=%s spot_mode=%s cooldown_candles=%s dry_run=%s loop_log_mode=%s",
            self.id,
            self.symbol,
            self.timeframe,
            get_spot_mode(),
            self.trade_cooldown_candles,
            self.ccxt_dry_run,
            self.loop_log_mode,
        )

        try:
            self.exchange = self._build_exchange()
            strategy_class = resolve_strategy_class(self.strategy_name)
            if not strategy_class:
                raise RuntimeError(f"Strategi '{self.strategy_name}' tidak ditemukan.")
            self.strategy_instance = strategy_class(bot_instance=self, params=self.strategy_params)
        except Exception as e:
            self.status = "Error"
            self.last_analysis = {"signal": "ERROR", "explanation": str(e)}
            self.log_activity("ERROR", f"Inisialisasi CCXT gagal: {e}", exc_info=True, is_notification=True)
            return

        while not self._stop_event.is_set():
            try:
                df = self._fetch_rates(limit=250)
                if df.empty:
                    self.last_analysis = {"signal": "ERROR", "explanation": f"No OHLCV for {self.symbol}"}
                    self.log_activity("WARNING", f"Gagal mengambil OHLCV {self.symbol}.")
                    time.sleep(self.check_interval)
                    continue

                analysis = self.strategy_instance.analyze(df)
                if isinstance(analysis, dict):
                    self.last_analysis = analysis
                    signal = analysis.get("signal", "HOLD")
                    explanation = analysis.get("explanation", "")
                    analyzed_price = analysis.get("price")
                elif isinstance(analysis, tuple) and len(analysis) >= 1:
                    signal = analysis[0]
                    self.last_analysis = {"signal": signal, "explanation": analysis[1] if len(analysis) > 1 else ""}
                    explanation = analysis[1] if len(analysis) > 1 else ""
                    analyzed_price = None
                else:
                    signal = "HOLD"
                    self.last_analysis = {"signal": "ERROR", "explanation": f"Invalid strategy response: {type(analysis).__name__}"}
                    explanation = self.last_analysis["explanation"]
                    analyzed_price = None

                pos_qty = self._get_spot_position_qty()
                self.last_position_qty = pos_qty
                has_long = pos_qty > 0
                current_candle = df.index[-1] if not df.empty else None
                self.last_cooldown_remaining = self._cooldown_remaining(current_candle)
                action_result = self._handle_trade_signal(signal, has_long=has_long, current_candle=current_candle)

                if self._should_log_loop(signal, action_result):
                    logger.info(
                        "Bot %s [LOOP]: symbol=%s signal=%s price=%s pos_qty=%.8f action=%s explanation=%s",
                        self.id,
                        self.symbol,
                        signal,
                        analyzed_price,
                        pos_qty,
                        action_result,
                        explanation,
                    )
                self._last_logged_signal = signal
                self._last_logged_action = action_result
                time.sleep(self.check_interval)
            except Exception as e:
                self.last_analysis = {"signal": "ERROR", "explanation": str(e)}
                self.log_activity("ERROR", f"Error loop CCXT: {e}", exc_info=True, is_notification=True)
                time.sleep(max(self.check_interval, 5))

        self.status = "Dijeda"
        self.log_activity("STOP", f"Bot '{self.name}' dihentikan (CCXT).", is_notification=True)
