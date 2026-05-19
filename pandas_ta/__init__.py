"""Local pandas_ta compatibility layer for QuantumBotX.

The upstream pandas_ta package has had availability issues on modern Python
versions. This module implements the indicator subset used by the app so the
runtime stays installable on Python 3.12.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _series(values, index) -> pd.Series:
    return pd.Series(values, index=index, dtype="float64")


def _na_series(close: pd.Series) -> pd.Series:
    return _series(np.nan, close.index)


def sma(close: pd.Series, length: int = 14, **kwargs) -> pd.Series:
    return close.rolling(length, min_periods=1).mean()


def ema(close: pd.Series, length: int = 14, **kwargs) -> pd.Series:
    return close.ewm(span=length, adjust=False).mean()


def rsi(close: pd.Series, length: int = 14, **kwargs) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / length, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / length, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def atr(high: pd.Series, low: pd.Series, close: pd.Series, length: int = 14, **kwargs) -> pd.Series:
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            (high - low).abs(),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1 / length, adjust=False).mean()


def bbands(close: pd.Series, length: int = 20, std: float = 2.0, **kwargs) -> pd.DataFrame:
    middle = close.rolling(length, min_periods=1).mean()
    deviation = close.rolling(length, min_periods=1).std()
    lower = middle - (std * deviation)
    upper = middle + (std * deviation)
    width = (upper - lower) / middle.replace(0, np.nan)
    percent = (close - lower) / (upper - lower).replace(0, np.nan)
    std_label = f"{float(std):.1f}"
    return pd.DataFrame(
        {
            f"BBL_{length}_{std_label}": lower,
            f"BBM_{length}_{std_label}": middle,
            f"BBU_{length}_{std_label}": upper,
            f"BBB_{length}_{std_label}": width,
            f"BBP_{length}_{std_label}": percent,
        },
        index=close.index,
    )


def adx(high: pd.Series, low: pd.Series, close: pd.Series, length: int = 14, **kwargs) -> pd.DataFrame:
    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0.0)
    minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0.0)
    atr_value = atr(high, low, close, length=length)
    plus_di = 100 * plus_dm.ewm(alpha=1 / length, adjust=False).mean() / atr_value.replace(0, np.nan)
    minus_di = 100 * minus_dm.ewm(alpha=1 / length, adjust=False).mean() / atr_value.replace(0, np.nan)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    return pd.DataFrame(
        {
            f"ADX_{length}": dx.ewm(alpha=1 / length, adjust=False).mean(),
            f"DMP_{length}": plus_di,
            f"DMN_{length}": minus_di,
        },
        index=close.index,
    )


def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9, **kwargs) -> pd.DataFrame:
    macd_line = ema(close, fast) - ema(close, slow)
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return pd.DataFrame(
        {
            f"MACD_{fast}_{slow}_{signal}": macd_line,
            f"MACDh_{fast}_{slow}_{signal}": hist,
            f"MACDs_{fast}_{slow}_{signal}": signal_line,
        },
        index=close.index,
    )


def stoch(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    k: int = 14,
    d: int = 3,
    smooth_k: int = 3,
    **kwargs,
) -> pd.DataFrame:
    lowest_low = low.rolling(k, min_periods=1).min()
    highest_high = high.rolling(k, min_periods=1).max()
    raw_k = 100 * (close - lowest_low) / (highest_high - lowest_low).replace(0, np.nan)
    k_line = raw_k.rolling(smooth_k, min_periods=1).mean()
    d_line = k_line.rolling(d, min_periods=1).mean()
    return pd.DataFrame(
        {
            f"STOCHk_{k}_{d}_{smooth_k}": k_line,
            f"STOCHd_{k}_{d}_{smooth_k}": d_line,
        },
        index=close.index,
    )


def donchian(
    high: pd.Series,
    low: pd.Series,
    lower_length: int = 20,
    upper_length: int = 20,
    **kwargs,
) -> pd.DataFrame:
    lower = low.rolling(lower_length, min_periods=1).min()
    upper = high.rolling(upper_length, min_periods=1).max()
    middle = (lower + upper) / 2
    return pd.DataFrame(
        {
            f"DCL_{lower_length}_{upper_length}": lower,
            f"DCM_{lower_length}_{upper_length}": middle,
            f"DCU_{lower_length}_{upper_length}": upper,
        },
        index=high.index,
    )


def ichimoku(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series | None = None,
    tenkan: int = 9,
    kijun: int = 26,
    senkou: int = 52,
    **kwargs,
):
    tenkan_line = (high.rolling(tenkan, min_periods=1).max() + low.rolling(tenkan, min_periods=1).min()) / 2
    kijun_line = (high.rolling(kijun, min_periods=1).max() + low.rolling(kijun, min_periods=1).min()) / 2
    span_a = ((tenkan_line + kijun_line) / 2).shift(kijun)
    span_b = ((high.rolling(senkou, min_periods=1).max() + low.rolling(senkou, min_periods=1).min()) / 2).shift(kijun)
    frame = pd.DataFrame(
        {
            f"ITS_{tenkan}": tenkan_line,
            f"IKS_{kijun}": kijun_line,
            f"ISA_{tenkan}": span_a,
            f"ISB_{kijun}": span_b,
        },
        index=high.index,
    )
    return frame, None


def roc(close: pd.Series, length: int = 10, **kwargs) -> pd.Series:
    return close.pct_change(periods=length) * 100


class _TAAccessor:
    def __init__(self, df: pd.DataFrame):
        self._df = df

    def _col(self, name: str) -> pd.Series:
        return self._df[name]

    def _append_frame(self, frame: pd.DataFrame, append: bool):
        if append:
            for col in frame.columns:
                self._df[col] = frame[col]
        return frame

    def sma(self, close: str = "close", length: int = 14, append: bool = False, **kwargs):
        out = sma(self._col(close), length=length, **kwargs)
        if append:
            self._df[f"SMA_{length}"] = out
        return out

    def ema(self, close: str = "close", length: int = 14, append: bool = False, **kwargs):
        out = ema(self._col(close), length=length, **kwargs)
        if append:
            self._df[f"EMA_{length}"] = out
        return out

    def rsi(self, close: str = "close", length: int = 14, append: bool = False, **kwargs):
        out = rsi(self._col(close), length=length, **kwargs)
        if append:
            self._df[f"RSI_{length}"] = out
        return out

    def atr(self, high: str = "high", low: str = "low", close: str = "close", length: int = 14, append: bool = False, **kwargs):
        out = atr(self._col(high), self._col(low), self._col(close), length=length, **kwargs)
        if append:
            self._df[f"ATRr_{length}"] = out
            self._df[f"ATR_{length}"] = out
        return out

    def bbands(self, close: str = "close", length: int = 20, std: float = 2.0, append: bool = False, **kwargs):
        return self._append_frame(bbands(self._col(close), length=length, std=std, **kwargs), append)

    def adx(self, high: str = "high", low: str = "low", close: str = "close", length: int = 14, append: bool = False, **kwargs):
        return self._append_frame(adx(self._col(high), self._col(low), self._col(close), length=length, **kwargs), append)

    def macd(self, close: str = "close", fast: int = 12, slow: int = 26, signal: int = 9, append: bool = False, **kwargs):
        return self._append_frame(macd(self._col(close), fast=fast, slow=slow, signal=signal, **kwargs), append)

    def stoch(
        self,
        high: str = "high",
        low: str = "low",
        close: str = "close",
        k: int = 14,
        d: int = 3,
        smooth_k: int = 3,
        append: bool = False,
        **kwargs,
    ):
        return self._append_frame(stoch(self._col(high), self._col(low), self._col(close), k=k, d=d, smooth_k=smooth_k, **kwargs), append)

    def donchian(self, high: str = "high", low: str = "low", lower_length: int = 20, upper_length: int = 20, append: bool = False, **kwargs):
        return self._append_frame(donchian(self._col(high), self._col(low), lower_length=lower_length, upper_length=upper_length, **kwargs), append)

    def ichimoku(self, high: str = "high", low: str = "low", close: str = "close", append: bool = False, **kwargs):
        frame, extra = ichimoku(self._col(high), self._col(low), self._df[close] if close in self._df else None, **kwargs)
        if append:
            for col in frame.columns:
                self._df[col] = frame[col]
        return frame, extra


@pd.api.extensions.register_dataframe_accessor("ta")
class _PandasTAAccessor(_TAAccessor):
    pass


def __getattr__(name):
    def _fallback(*args, **kwargs):
        if args and isinstance(args[0], pd.Series):
            return _na_series(args[0])
        return pd.Series(dtype="float64")

    return _fallback
