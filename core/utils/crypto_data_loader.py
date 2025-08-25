#!/usr/bin/env python3
"""
Crypto Data Loader for QuantumBotX
Handles CSV data loading with proper datetime conversion and validation
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
# Disable crypto data loader logs for silent backtesting
logger.disabled = True

def load_crypto_csv(file_path, symbol_name="BTCUSD"):
    """
    Load crypto CSV data with proper datetime handling and validation.
    
    Args:
        file_path: Path to the CSV file
        symbol_name: Name of the crypto symbol (for logging)
    
    Returns:
        pandas.DataFrame: Processed dataframe ready for backtesting
    """
    try:
        # Load the CSV file
        df = pd.read_csv(file_path)
        
        logger.info(f"Loading {symbol_name} data from {file_path}")
        logger.info(f"Original data shape: {df.shape}")
        logger.info(f"Columns: {list(df.columns)}")
        
        # Ensure required columns exist
        required_columns = ['time', 'open', 'high', 'low', 'close']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Convert time column to datetime
        if not pd.api.types.is_datetime64_any_dtype(df['time']):
            logger.info("Converting time column to datetime...")
            df['time'] = pd.to_datetime(df['time'])
        
        # Sort by time to ensure chronological order
        df = df.sort_values('time').reset_index(drop=True)
        
        # Validate OHLC integrity
        logger.info("Validating OHLC data integrity...")
        
        # Ensure high >= max(open, close) and low <= min(open, close)
        df['high'] = df[['high', 'open', 'close']].max(axis=1)
        df['low'] = df[['low', 'open', 'close']].min(axis=1)
        
        # Remove any rows with invalid data
        before_clean = len(df)
        df = df.dropna(subset=['open', 'high', 'low', 'close'])
        
        # Remove zero or negative prices
        df = df[(df['open'] > 0) & (df['high'] > 0) & (df['low'] > 0) & (df['close'] > 0)]
        
        after_clean = len(df)
        
        if before_clean != after_clean:
            logger.warning(f"Removed {before_clean - after_clean} invalid data rows")
        
        # Add volume column if missing (use tick_volume or default)
        if 'volume' not in df.columns:
            if 'tick_volume' in df.columns:
                df['volume'] = df['tick_volume']
            else:
                # Generate realistic volume data for crypto
                df['volume'] = np.random.randint(100000, 1000000, len(df))
                logger.info("Generated synthetic volume data")
        
        # Calculate basic statistics
        price_stats = {
            'min_price': df['close'].min(),
            'max_price': df['close'].max(),
            'avg_price': df['close'].mean(),
            'volatility': df['close'].std() / df['close'].mean() * 100
        }
        
        logger.info(f"Data statistics:")
        logger.info(f"  Price range: ${price_stats['min_price']:.2f} - ${price_stats['max_price']:.2f}")
        logger.info(f"  Average price: ${price_stats['avg_price']:.2f}")
        logger.info(f"  Volatility: {price_stats['volatility']:.2f}%")
        logger.info(f"  Data period: {df['time'].min()} to {df['time'].max()}")
        logger.info(f"  Final data shape: {df.shape}")
        
        return df
        
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error loading crypto data: {e}")
        raise

def prepare_for_backtesting(df, symbol_name="BTCUSD"):
    """
    Prepare loaded crypto data specifically for backtesting.
    
    Args:
        df: Raw crypto dataframe
        symbol_name: Symbol name for context
    
    Returns:
        pandas.DataFrame: Backtesting-ready dataframe
    """
    logger.info(f"Preparing {symbol_name} data for backtesting...")
    
    # Ensure chronological order
    df = df.sort_values('time').reset_index(drop=True)
    
    # Validate minimum data requirements
    if len(df) < 200:
        raise ValueError(f"Insufficient data: {len(df)} rows (minimum 200 required)")
    
    # Calculate returns and volatility metrics
    df['returns'] = df['close'].pct_change()
    df['price_change'] = df['close'].diff()
    df['range_pct'] = (df['high'] - df['low']) / df['close'] * 100
    
    # Remove extreme outliers that could skew backtesting
    # Remove rows with extreme returns (> 20% single period change)
    extreme_returns = abs(df['returns']) > 0.20
    
    if extreme_returns.sum() > 0:
        logger.warning(f"Removing {extreme_returns.sum()} extreme return outliers")
        df = df[~extreme_returns].reset_index(drop=True)
    
    # Recalculate after cleaning
    df['returns'] = df['close'].pct_change()
    
    logger.info(f"Backtesting data prepared: {len(df)} rows ready")
    
    return df

def validate_crypto_data(df):
    """
    Validate crypto data quality and provide warnings.
    
    Args:
        df: Crypto dataframe to validate
    
    Returns:
        dict: Validation results and recommendations
    """
    results = {
        'is_valid': True,
        'warnings': [],
        'recommendations': []
    }
    
    # Check data completeness
    if len(df) < 500:
        results['warnings'].append(f"Limited data: {len(df)} rows (recommended: 1000+)")
        
    if len(df) < 200:
        results['is_valid'] = False
        results['warnings'].append("Insufficient data for reliable backtesting")
    
    # Check for data gaps
    if 'time' in df.columns:
        time_diff = df['time'].diff().dt.total_seconds() / 3600  # Hours
        expected_interval = time_diff.mode()[0] if len(time_diff.mode()) > 0 else 1
        
        gaps = time_diff > expected_interval * 2
        if gaps.sum() > 0:
            results['warnings'].append(f"Found {gaps.sum()} potential data gaps")
    
    # Check volatility characteristics
    if 'returns' not in df.columns:
        df_temp = df.copy()
        df_temp['returns'] = df_temp['close'].pct_change()
    else:
        df_temp = df
    
    volatility = df_temp['returns'].std() * 100
    
    if volatility > 10:
        results['warnings'].append(f"High volatility data ({volatility:.2f}%): Consider conservative parameters")
        results['recommendations'].append("Use smaller position sizes and tighter risk management")
    elif volatility < 0.5:
        results['warnings'].append(f"Low volatility data ({volatility:.2f}%): May produce fewer trading signals")
        
    # Check for unusual price patterns
    price_jumps = abs(df_temp['returns']) > 0.05  # 5% single period moves
    
    if price_jumps.sum() > len(df) * 0.05:  # More than 5% of data points
        results['warnings'].append(f"Frequent large price moves detected: {price_jumps.sum()} instances")
        results['recommendations'].append("Consider using ATR-based position sizing for better risk management")
    
    return results