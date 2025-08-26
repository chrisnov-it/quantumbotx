# core/db/models.py
import sqlite3
import json
from datetime import datetime, date
from typing import Dict, List, Optional, Any

def log_trade_action(bot_id, action, details):
    try:
        with sqlite3.connect('bots.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO trade_history (bot_id, action, details) VALUES (?, ?, ?)',
                (bot_id, action, details)
            )
            if action.startswith("POSISI") or action.startswith("GAGAL") or action.startswith("AUTO"):
                notif_msg = f"Bot ID {bot_id} - {details}"
                cursor.execute(
                    'INSERT INTO notifications (bot_id, message) VALUES (?, ?)',
                    (bot_id, notif_msg)
                )
            conn.commit()
    except Exception as e:
        print(f"[DB ERROR] Gagal mencatat aksi: {e}")

# ===== AI MENTOR DATABASE FUNCTIONS =====

def create_trading_session(session_date: date, emotions: str = 'netral', 
                          market_conditions: str = 'normal', notes: str = '') -> int:
    """Buat sesi trading baru dan return session_id"""
    try:
        with sqlite3.connect('bots.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO trading_sessions (session_date, emotions, market_conditions, personal_notes) VALUES (?, ?, ?, ?)',
                (session_date, emotions, market_conditions, notes)
            )
            session_id = cursor.lastrowid
            conn.commit()
            return session_id
    except Exception as e:
        print(f"[AI MENTOR DB ERROR] Gagal membuat sesi trading: {e}")
        return 0

def get_or_create_today_session() -> int:
    """Ambil session hari ini atau buat baru jika belum ada"""
    today = date.today()
    try:
        with sqlite3.connect('bots.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id FROM trading_sessions WHERE session_date = ?',
                (today,)
            )
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return create_trading_session(today)
    except Exception as e:
        print(f"[AI MENTOR DB ERROR] Gagal mengambil sesi hari ini: {e}")
        return create_trading_session(today)

def log_trade_for_ai_analysis(bot_id: int, symbol: str, profit_loss: float, 
                              lot_size: float, stop_loss_used: bool = False,
                              take_profit_used: bool = False, risk_percent: float = 1.0,
                              strategy_used: str = '') -> None:
    """Log trade data untuk analisis AI mentor"""
    session_id = get_or_create_today_session()
    
    try:
        with sqlite3.connect('bots.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO daily_trading_data 
                   (session_id, bot_id, symbol, profit_loss, lot_size, 
                    stop_loss_used, take_profit_used, risk_percent, strategy_used)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (session_id, bot_id, symbol, profit_loss, lot_size,
                 stop_loss_used, take_profit_used, risk_percent, strategy_used)
            )
            
            # Update trading session summary
            cursor.execute(
                '''UPDATE trading_sessions 
                   SET total_trades = total_trades + 1,
                       total_profit_loss = total_profit_loss + ?
                   WHERE id = ?''',
                (profit_loss, session_id)
            )
            
            conn.commit()
    except Exception as e:
        print(f"[AI MENTOR DB ERROR] Gagal log trade untuk AI: {e}")

def get_trading_session_data(session_date: date) -> Optional[Dict[str, Any]]:
    """Ambil data sesi trading untuk analisis AI"""
    try:
        with sqlite3.connect('bots.db') as conn:
            cursor = conn.cursor()
            
            # Get session info
            cursor.execute(
                '''SELECT id, total_trades, total_profit_loss, emotions, 
                          market_conditions, personal_notes, risk_score
                   FROM trading_sessions WHERE session_date = ?''',
                (session_date,)
            )
            session_result = cursor.fetchone()
            
            if not session_result:
                return None
                
            session_id = session_result[0]
            
            # Get trades for this session
            cursor.execute(
                '''SELECT symbol, profit_loss, lot_size, stop_loss_used, 
                          take_profit_used, risk_percent, strategy_used
                   FROM daily_trading_data WHERE session_id = ?''',
                (session_id,)
            )
            trades_data = cursor.fetchall()
            
            trades = []
            for trade in trades_data:
                trades.append({
                    'symbol': trade[0],
                    'profit': trade[1],
                    'lot_size': trade[2],
                    'stop_loss_used': bool(trade[3]),
                    'take_profit_used': bool(trade[4]),
                    'risk_percent': trade[5],
                    'strategy': trade[6]
                })
            
            return {
                'session_id': session_id,
                'total_trades': session_result[1],
                'total_profit_loss': session_result[2],
                'emotions': session_result[3],
                'market_conditions': session_result[4],
                'personal_notes': session_result[5] or '',
                'risk_score': session_result[6] or 5,
                'trades': trades
            }
            
    except Exception as e:
        print(f"[AI MENTOR DB ERROR] Gagal ambil data sesi: {e}")
        return None

def save_ai_mentor_report(session_id: int, analysis: Dict[str, Any]) -> bool:
    """Simpan laporan AI mentor ke database"""
    try:
        with sqlite3.connect('bots.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO ai_mentor_reports 
                   (session_id, trading_patterns_analysis, emotional_analysis,
                    risk_management_score, recommendations, motivation_message)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (session_id, 
                 json.dumps(analysis.get('pola_trading', {})),
                 json.dumps(analysis.get('emosi_vs_performa', {})),
                 analysis.get('manajemen_risiko', {}).get('nilai', '5/10'),
                 json.dumps(analysis.get('rekomendasi', [])),
                 analysis.get('motivasi', ''))
            )
            conn.commit()
            return True
    except Exception as e:
        print(f"[AI MENTOR DB ERROR] Gagal simpan laporan AI: {e}")
        return False

def update_session_emotions_and_notes(session_date: date, emotions: str, notes: str) -> bool:
    """Update emosi dan catatan untuk sesi trading"""
    try:
        with sqlite3.connect('bots.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''UPDATE trading_sessions 
                   SET emotions = ?, personal_notes = ?
                   WHERE session_date = ?''',
                (emotions, notes, session_date)
            )
            conn.commit()
            return True
    except Exception as e:
        print(f"[AI MENTOR DB ERROR] Gagal update emosi dan catatan: {e}")
        return False

def get_recent_mentor_reports(limit: int = 7) -> List[Dict[str, Any]]:
    """Ambil laporan mentor AI terbaru"""
    try:
        with sqlite3.connect('bots.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT ts.session_date, ts.total_profit_loss, ts.total_trades,
                          ts.emotions, mr.motivation_message, mr.created_at
                   FROM trading_sessions ts
                   LEFT JOIN ai_mentor_reports mr ON ts.id = mr.session_id
                   ORDER BY ts.session_date DESC
                   LIMIT ?''',
                (limit,)
            )
            
            reports = []
            for row in cursor.fetchall():
                reports.append({
                    'session_date': row[0],
                    'profit_loss': row[1],
                    'total_trades': row[2],
                    'emotions': row[3],
                    'motivation': row[4] or 'Belum ada analisis AI',
                    'created_at': row[5]
                })
            
            return reports
            
    except Exception as e:
        print(f"[AI MENTOR DB ERROR] Gagal ambil laporan terbaru: {e}")
        return []
