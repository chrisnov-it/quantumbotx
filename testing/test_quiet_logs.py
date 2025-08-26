#!/usr/bin/env python3
"""
🔇 Test Log Noise Filtering
Quick test to verify werkzeug logs are filtered properly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import logging
from core import RequestLogFilter

def test_log_filter():
    """Test the RequestLogFilter to ensure it blocks noise"""
    print("🔍 Testing RequestLogFilter...")
    
    filter_obj = RequestLogFilter()
    
    # Test cases - these should be FILTERED OUT (return False)
    noisy_logs = [
        'INFO:werkzeug:127.0.0.1 - - [24/Aug/2025 11:17:48] "GET /api/notifications/unread HTTP/1.1" 200 -',
        'INFO:werkzeug:127.0.0.1 - - [24/Aug/2025 11:17:48] "GET /api/notifications/unread-count HTTP/1.1" 200 -',
        'INFO:werkzeug:127.0.0.1 - - [24/Aug/2025 11:17:58] "GET /api/bots/analysis HTTP/1.1" 200 -',
        'INFO:werkzeug:127.0.0.1 - - [24/Aug/2025 11:18:00] "GET /favicon.ico HTTP/1.1" 200 -',
        'INFO:werkzeug:127.0.0.1 - - [24/Aug/2025 11:18:00] "GET /api/dashboard/stats HTTP/1.1" 200 -',
    ]
    
    # Test cases - these should be ALLOWED (return True)
    important_logs = [
        'INFO:werkzeug:127.0.0.1 - - [24/Aug/2025 11:17:48] "POST /api/bots HTTP/1.1" 201 -',
        'INFO:werkzeug:127.0.0.1 - - [24/Aug/2025 11:17:48] "PUT /api/bots/1/start HTTP/1.1" 200 -',
        'INFO:werkzeug:127.0.0.1 - - [24/Aug/2025 11:17:48] "DELETE /api/bots/1 HTTP/1.1" 200 -',
        'INFO:werkzeug:127.0.0.1 - - [24/Aug/2025 11:17:48] "GET /api/bots HTTP/1.1" 404 -',
        'INFO:core.bots.trading_bot:Bot 1 [BUY]: Executing trade on EURUSD',
        'ERROR:core.mt5.trade:Failed to connect to MT5',
        'WARNING:core.strategies:Risk level too high',
    ]
    
    print("\\n🚫 Testing NOISY logs (should be filtered):")
    for log_msg in noisy_logs:
        # Create a mock log record
        record = logging.LogRecord(
            name='test', level=logging.INFO, pathname='', lineno=0,
            msg=log_msg, args=(), exc_info=None
        )
        
        should_show = filter_obj.filter(record)
        status = "❌ FILTERED" if not should_show else "⚠️ SHOWING"
        print(f"  {status}: {log_msg[:80]}...")
        
        if should_show:
            print(f"    ⚠️ WARNING: This noisy log is still showing!")
    
    print("\\n✅ Testing IMPORTANT logs (should be shown):")
    for log_msg in important_logs:
        record = logging.LogRecord(
            name='test', level=logging.INFO, pathname='', lineno=0,
            msg=log_msg, args=(), exc_info=None
        )
        
        should_show = filter_obj.filter(record)
        status = "✅ SHOWING" if should_show else "❌ FILTERED"
        print(f"  {status}: {log_msg[:80]}...")
        
        if not should_show:
            print(f"    ⚠️ WARNING: This important log is being filtered!")
    
    print("\\n🎯 SUMMARY:")
    print("Your terminal will now only show:")
    print("  ✅ Trading bot activities")
    print("  ✅ POST/PUT/DELETE requests (important actions)")
    print("  ✅ Error messages (4xx, 5xx)")
    print("  ✅ Warnings and critical messages")
    print("\\n🚫 Filtered out (noise):")
    print("  ❌ GET requests with 200 status")
    print("  ❌ Notification polling")
    print("  ❌ Dashboard data polling")
    print("  ❌ Static files and favicon")
    print("\\n🎉 Your backtesting terminal will be MUCH quieter now!")

if __name__ == "__main__":
    test_log_filter()