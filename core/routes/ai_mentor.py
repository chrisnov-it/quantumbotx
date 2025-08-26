# core/routes/ai_mentor.py
"""
🧠 AI Trading Mentor Routes - Web Interface untuk Mentor AI Indonesia
Routes untuk menampilkan laporan AI mentor dan interaksi pengguna
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from datetime import datetime, date, timedelta
from core.ai.trading_mentor_ai import IndonesianTradingMentorAI, TradingSession
from core.db.models import (
    get_trading_session_data, save_ai_mentor_report, 
    update_session_emotions_and_notes, get_recent_mentor_reports,
    get_or_create_today_session
)
import logging

logger = logging.getLogger(__name__)

# Create blueprint
ai_mentor_bp = Blueprint('ai_mentor', __name__, url_prefix='/ai-mentor')

@ai_mentor_bp.route('/')
def dashboard():
    """Dashboard utama AI Mentor"""
    try:
        # Get recent reports
        recent_reports = get_recent_mentor_reports(7)
        
        # Get today's session data
        today_session = get_trading_session_data(date.today())
        
        # Statistics
        total_sessions = len(recent_reports)
        profitable_sessions = len([r for r in recent_reports if r['profit_loss'] > 0])
        win_rate = (profitable_sessions / total_sessions * 100) if total_sessions > 0 else 0
        
        return render_template('ai_mentor/dashboard.html', 
                             recent_reports=recent_reports,
                             today_session=today_session,
                             win_rate=win_rate,
                             total_sessions=total_sessions)
    except Exception as e:
        logger.error(f"Error in AI mentor dashboard: {e}")
        flash("Terjadi kesalahan saat memuat dashboard AI Mentor", "error")
        return render_template('ai_mentor/dashboard.html', 
                             recent_reports=[], today_session=None,
                             win_rate=0, total_sessions=0)

@ai_mentor_bp.route('/today-report')
def today_report():
    """Laporan AI mentor untuk hari ini"""
    try:
        today = date.today()
        session_data = get_trading_session_data(today)
        
        if not session_data:
            flash("Belum ada data trading untuk hari ini. Mulai trading untuk mendapatkan analisis AI!", "info")
            return render_template('ai_mentor/no_data.html')
        
        # Generate AI analysis
        mentor = IndonesianTradingMentorAI()
        
        # Convert to TradingSession format
        trading_session = TradingSession(
            date=today,
            trades=session_data['trades'],
            emotions=session_data['emotions'],
            market_conditions=session_data['market_conditions'],
            profit_loss=session_data['total_profit_loss'],
            notes=session_data['personal_notes']
        )
        
        # Generate AI report
        ai_report = mentor.generate_daily_report(trading_session)
        analysis = mentor.analyze_trading_session(trading_session)
        
        # Save to database
        save_ai_mentor_report(session_data['session_id'], analysis)
        
        return render_template('ai_mentor/daily_report.html',
                             session_data=session_data,
                             ai_report=ai_report,
                             analysis=analysis)
                             
    except Exception as e:
        logger.error(f"Error generating today's AI report: {e}")
        flash("Gagal membuat laporan AI untuk hari ini", "error")
        return redirect(url_for('ai_mentor.dashboard'))

@ai_mentor_bp.route('/update-emotions', methods=['POST'])
def update_emotions():
    """Update emosi dan catatan untuk sesi hari ini"""
    try:
        data = request.get_json()
        emotions = data.get('emotions', 'netral')
        notes = data.get('notes', '')
        
        success = update_session_emotions_and_notes(date.today(), emotions, notes)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Emosi dan catatan berhasil disimpan!'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Gagal menyimpan data'
            }), 500
            
    except Exception as e:
        logger.error(f"Error updating emotions: {e}")
        return jsonify({
            'success': False,
            'message': 'Terjadi kesalahan sistem'
        }), 500

@ai_mentor_bp.route('/history')
def history():
    """Riwayat laporan AI mentor"""
    try:
        # Get date range from query params
        days = request.args.get('days', 30, type=int)
        reports = get_recent_mentor_reports(days)
        
        return render_template('ai_mentor/history.html', 
                             reports=reports, days=days)
                             
    except Exception as e:
        logger.error(f"Error loading AI mentor history: {e}")
        flash("Gagal memuat riwayat laporan AI", "error")
        return render_template('ai_mentor/history.html', 
                             reports=[], days=30)

@ai_mentor_bp.route('/session/<session_date>')
def view_session(session_date):
    """Lihat laporan AI untuk tanggal tertentu"""
    try:
        # Parse date
        target_date = datetime.strptime(session_date, '%Y-%m-%d').date()
        session_data = get_trading_session_data(target_date)
        
        if not session_data:
            flash(f"Tidak ada data trading untuk tanggal {session_date}", "info")
            return redirect(url_for('ai_mentor.history'))
        
        # Generate AI analysis if not exists
        mentor = IndonesianTradingMentorAI()
        trading_session = TradingSession(
            date=target_date,
            trades=session_data['trades'],
            emotions=session_data['emotions'],
            market_conditions=session_data['market_conditions'],
            profit_loss=session_data['total_profit_loss'],
            notes=session_data['personal_notes']
        )
        
        ai_report = mentor.generate_daily_report(trading_session)
        analysis = mentor.analyze_trading_session(trading_session)
        
        return render_template('ai_mentor/session_detail.html',
                             session_data=session_data,
                             ai_report=ai_report,
                             analysis=analysis,
                             session_date=session_date)
                             
    except ValueError:
        flash("Format tanggal tidak valid", "error")
        return redirect(url_for('ai_mentor.history'))
    except Exception as e:
        logger.error(f"Error viewing session {session_date}: {e}")
        flash("Gagal memuat detail sesi", "error")
        return redirect(url_for('ai_mentor.history'))

@ai_mentor_bp.route('/quick-feedback')
def quick_feedback():
    """Quick feedback modal untuk input cepat emosi dan catatan"""
    try:
        session_id = get_or_create_today_session()
        today_session = get_trading_session_data(date.today())
        
        return render_template('ai_mentor/quick_feedback.html',
                             session_data=today_session)
                             
    except Exception as e:
        logger.error(f"Error loading quick feedback: {e}")
        return jsonify({
            'success': False,
            'message': 'Gagal memuat form feedback'
        }), 500

@ai_mentor_bp.route('/api/generate-instant-feedback', methods=['POST'])
def generate_instant_feedback():
    """Generate instant feedback dari AI berdasarkan input emosi"""
    try:
        data = request.get_json()
        emotions = data.get('emotions', 'netral')
        notes = data.get('notes', '')
        current_pnl = data.get('current_pnl', 0)
        
        # Get today's session
        today_session = get_trading_session_data(date.today())
        
        if not today_session:
            return jsonify({
                'success': False,
                'message': 'Belum ada data trading hari ini'
            }), 400
        
        # Generate quick AI feedback
        mentor = IndonesianTradingMentorAI()
        
        # Create temporary session for instant feedback
        temp_session = TradingSession(
            date=date.today(),
            trades=today_session.get('trades', []),
            emotions=emotions,
            market_conditions=today_session.get('market_conditions', 'normal'),
            profit_loss=current_pnl,
            notes=notes
        )
        
        analysis = mentor.analyze_trading_session(temp_session)
        
        return jsonify({
            'success': True,
            'feedback': {
                'emotional_analysis': analysis['emosi_vs_performa']['feedback'],
                'motivation': analysis['motivasi'],
                'quick_tips': analysis['rekomendasi'][:3]  # First 3 recommendations
            }
        })
        
    except Exception as e:
        logger.error(f"Error generating instant feedback: {e}")
        return jsonify({
            'success': False,
            'message': 'Gagal membuat feedback AI'
        }), 500

@ai_mentor_bp.route('/settings')
def settings():
    """Pengaturan AI Mentor"""
    return render_template('ai_mentor/settings.html')

# Helper function untuk integration dengan dashboard utama
def get_ai_mentor_summary():
    """Fungsi helper untuk mendapatkan ringkasan AI mentor untuk dashboard utama"""
    try:
        today_session = get_trading_session_data(date.today())
        recent_reports = get_recent_mentor_reports(3)
        
        return {
            'today_has_data': today_session is not None,
            'today_profit_loss': today_session['total_profit_loss'] if today_session else 0,
            'today_emotions': today_session['emotions'] if today_session else 'netral',
            'recent_performance': recent_reports[:3] if recent_reports else []
        }
    except Exception as e:
        logger.error(f"Error getting AI mentor summary: {e}")
        return {
            'today_has_data': False,
            'today_profit_loss': 0,
            'today_emotions': 'netral',
            'recent_performance': []
        }