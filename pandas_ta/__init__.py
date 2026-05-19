"""Minimal local pandas_ta compatibility shim for environments without pandas_ta.

This is intentionally lightweight and only provides a subset used by app startup
and basic indicators. For full indicator coverage, install official pandas_ta.
"""

from __future__ import annotations

import pandas as pd
import numpy as np


def _na_series(series: pd.Series) -> pd.Series:
    return pd.Series(np.nan, index=series.index, dtype="float64")


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
    return tr.rolling(length, min_periods=1).mean()


def sma(close: pd.Series, length: int = 14, **kwargs) -> pd.Series:
    return close.rolling(length, min_periods=1).mean()


def ema(close: pd.Series, length: int = 14, **kwargs) -> pd.Series:
    return close.ewm(span=length, adjust=False).mean()


def adx(high: pd.Series, low: pd.Series, close: pd.Series, length: int = 14, **kwargs) -> pd.DataFrame:
    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0.0)
    minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0.0)

    prev_close = close.shift(1)
    tr = pd.concat(
        [
            (high - low).abs(),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    atr_val = tr.ewm(alpha=1 / length, adjust=False).mean()
    plus_di = 100 * plus_dm.ewm(alpha=1 / length, adjust=False).mean() / atr_val.replace(0, np.nan)
    minus_di = 100 * minus_dm.ewm(alpha=1 / length, adjust=False).mean() / atr_val.replace(0, np.nan)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    adx_line = dx.ewm(alpha=1 / length, adjust=False).mean()

    return pd.DataFrame(
        {
            f"DMP_{length}": plus_di,
            f"DMN_{length}": minus_di,
            f"ADX_{length}": adx_line,
        },
        index=close.index,
    )


def bbands(close: pd.Series, length: int = 20, std: float = 2.0, **kwargs) -> pd.DataFrame:
    basis = close.rolling(length, min_periods=1).mean()
    dev = close.rolling(length, min_periods=1).std()
    lower = basis - (std * dev)
    upper = basis + (std * dev)
    width = (upper - lower) / basis.replace(0, np.nan)
    percent = (close - lower) / (upper - lower).replace(0, np.nan)
    std_lbl = f"{float(std):.1f}"
    return pd.DataFrame(
        {
            f"BBL_{length}_{std_lbl}": lower,
            f"BBM_{length}_{std_lbl}": basis,
            f"BBU_{length}_{std_lbl}": upper,
            f"BBB_{length}_{std_lbl}": width,
            f"BBP_{length}_{std_lbl}": percent,
        },
        index=close.index,
    )


class _TAAccessor:
    def __init__(self, df: pd.DataFrame):
        self._df = df

    def rsi(self, close: str = "close", length: int = 14, append: bool = False, **kwargs):
        out = rsi(self._df[close], length=length, **kwargs)
        if append:
            self._df[f"RSI_{length}"] = out
        return out

    def atr(self, high: str = "high", low: str = "low", close: str = "close", length: int = 14, append: bool = False, **kwargs):
        out = atr(self._df[high], self._df[low], self._df[close], length=length, **kwargs)
        if append:
            self._df[f"ATR_{length}"] = out
        return out

    def adx(self, high: str = "high", low: str = "low", close: str = "close", length: int = 14, append: bool = False, **kwargs):
        out = adx(self._df[high], self._df[low], self._df[close], length=length, **kwargs)
        if append:
            for col in out.columns:
                self._df[col] = out[col]
        return out

    def bbands(self, close: str = "close", length: int = 20, std: float = 2.0, append: bool = False, **kwargs):
        out = bbands(self._df[close], length=length, std=std, **kwargs)
        if append:
            for col in out.columns:
                self._df[col] = out[col]
        return out

    def __getattr__(self, name):
        # Unknown indicators return NA series with compatible index.
        def _fallback(*args, **kwargs):
            base = self._df["close"] if "close" in self._df.columns else self._df.iloc[:, 0]
            return _na_series(base)

        return _fallback


@pd.api.extensions.register_dataframe_accessor("ta")
class _PandasTAAccessor(_TAAccessor):
    pass


def __getattr__(name):
    def _fallback(*args, **kwargs):
        if args and isinstance(args[0], pd.Series):
            return _na_series(args[0])
        return pd.Series(dtype="float64")

    return _fallback
