/**
 * QuantumBotX Internationalization (i18n) System
 * Global language support across the entire application
 */

// Translation dictionary for all app languages
window.QuantumBotXI18n = {
  translations: {
    id: {
    // Navigation & Common
      "nav.dashboard": "Dasbor",
      "nav.bots": "Bot Trading",
      "nav.backtest": "Backtester",
      "nav.history": "Riwayat",
      "nav.ai_mentor": "AI Mentor",
      "nav.strategy_switcher": "Strategy Switcher",
      "nav.ramadan": "Ramadan Mode",
      "nav.settings": "Pengaturan",
      "nav.portfolio": "Portfolio",
      "nav.stocks": "Stocks",
      "nav.forex": "Forex",
      "nav.notifications": "Notifikasi",
      "nav.section.navigation": "Navigasi",
      "nav.section.market_data": "Data Pasar",

      // Dashboard
      "dashboard.title": "Dasbor QuantumBotX",
      "dashboard.welcome": "Selamat Datang",
      "dashboard.welcome_back": "Selamat datang kembali! Berikut ringkasan trading Anda hari ini.",
      "dashboard.total_bots": "Total Bot",
      "dashboard.active_bots": "Bot Aktif",
      "dashboard.inactive_bots": "Bot Tidak Aktif",
      "dashboard.total_profit": "Total Profit",
      "dashboard.today_pnl": "PnL Hari Ini",
      "dashboard.create_bot": "Buat Bot Baru",
      "dashboard.view_details": "Lihat Detail",
      "dashboard.total_equity": "Total Saldo (Equity)",
      "dashboard.today_profit": "Profit Hari Ini",
      "dashboard.ai_mentor": "🤖 AI Mentor",
      "dashboard.ai_mentor_ready": "Siap Membantu",
      "dashboard.ai_mentor_active": "Aktif Menganalisis",
      "dashboard.view_analysis": "Lihat Analisis →",
      "dashboard.emotion_status": "Status Emosi",
      "dashboard.update_status": "Update Status",
      "dashboard.ai_mentor_today": "🧠 AI Mentor Hari Ini",
      "dashboard.trading_analysis": "Analisis Trading:",
      "dashboard.daily_tip": "Tips Hari Ini:",
      "dashboard.view_full_report": "📊 Lihat Laporan Lengkap",
      "dashboard.recent_activities": "⚡ Aktivitas Terbaru",
      "dashboard.loading_activities": "Memuat aktivitas...",
      "dashboard.active_trading_bots": "Active Trading Bots",
      "dashboard.loading_bot_list": "Memuat daftar bot...",
      "dashboard.view_all_bots": "View All Bots",
      "dashboard.chat_with_ai_mentor": "Chat dengan AI Mentor",
      "dashboard.price_chart": "📈 Grafik Harga EUR/USD",
      "dashboard.loading": "Memuat...",
      "dashboard.rsi_chart": "📊 RSI EUR/USD (H1)",
      "dashboard.real_time": "Real-time",
      "dashboard.no_active_bots": "Tidak ada bot yang aktif",
      "dashboard.emotion_calm": "😌 Tenang",
      "dashboard.emotion_greedy": "🤑 Serakah",
      "dashboard.emotion_fear": "😰 Takut",
      "dashboard.emotion_frustrated": "😤 Frustasi",
      "dashboard.emotion_neutral": "😐 Netral",
      "dashboard.update_emotion_status": "🎯 Update Status Emosi",
      "dashboard.cancel": "Batal",
      "dashboard.emotion_updated": "Status emosi berhasil diupdate!",
      "dashboard.emotion_update_failed": "Gagal update status emosi",
      "dashboard.error_updating_emotion": "Error: Gagal update status emosi",

      // Bot Status
      "status.active": "Aktif",
      "status.inactive": "Dijeda",
      "status.error": "Error",
      "status.paused": "Dijeda",

      // Action Buttons
      "action.start": "Jalankan",
      "action.stop": "Hentikan",
      "action.edit": "Edit",
      "action.delete": "Hapus",
      "action.view": "Lihat",
      "action.analyze": "Analisis",
      "action.start_all": "Start All",
      "action.stop_all": "Stop All",
      "action.create_new_bot": "Buat Bot Baru",

      // Form Labels & Messages
      "label.name": "Nama",
      "label.market": "Pasar",
      "label.strategy": "Strategi",
      "label.status": "Status",
      "label.profit": "Profit",
      "label.trades": "Jumlah Trade",
      "label.win_rate": "Win Rate",
      "label.bot_name": "Nama Bot",
      "label.risk_per_trade": "Risk per Trade (%)",
      "label.sl_atr": "SL (ATR Multiplier)",
      "label.tp_atr": "TP (ATR Multiplier)",
      "label.timeframe": "Timeframe",
      "label.check_interval": "Interval Cek (detik)",
      "label.full_name": "Nama Lengkap",
      "label.email": "Alamat Email",
      "label.password": "Ganti Password (kosongkan jika tidak ingin diubah)",

      "msg.loading": "Memuat...",
      "msg.no_data": "Tidak ada data",
      "msg.success": "Berhasil",
      "msg.error": "Error",
      "msg.confirm": "Apakah Anda yakin?",
      "msg.save_changes": "Simpan Perubahan",
      "msg.save_preferences": "Simpan Preferensi",

      // Time & Date
      "time.today": "Hari Ini",
      "time.yesterday": "Kemarin",
      "time.week": "Minggu Ini",
      "time.month": "Bulan Ini",

      // Error Messages
      "error.connection": "Gagal terhubung ke server",
      "error.loading": "Gagal memuat data",
      "error.save": "Gagal menyimpan perubahan",
      "error.404_title": "Halaman Tidak Ditemukan - QuantumBotX",
      "error.404_heading": "Halaman Tidak Ditemukan",
      "error.404_message": "Maaf, halaman yang Anda cari tidak ada atau telah dipindahkan.",
      "error.500_title": "Terjadi Kesalahan Internal - QuantumBotX",
      "error.500_heading": "Terjadi Kesalahan Internal",
      "error.500_message": "Maaf, terjadi masalah pada server kami. Tim kami telah diberitahu dan sedang menanganinya.",
      "error.back_to_dashboard": "Kembali ke Dashboard",

      // AI Mentor
      "mentor.greeting": "Halo, Teman Trader!",
      "mentor.welcome": "Selamat datang di sistem trading AI saya",

      // Units & Currencies
      "currency.usd": "USD",
      "currency.idr": "IDR",
      "currency.percentage": "%",

      // Settings
      "settings.title": "Pengaturan",
      "settings.language": "Bahasa",
      "settings.theme": "Tema",
      "settings.save": "Simpan Perubahan",
      "settings.profile": "Profil",
      "settings.preferences": "Preferensi",
      "settings.api_keys": "API Keys Bursa",
      "settings.quick_settings": "Pengaturan Cepat",
      "settings.email_notifications": "Notifikasi Email",
      "settings.auto_update": "Update Otomatis Strategi",
      "settings.demo_mode": "Mode Demo",
      "settings.version": "Versi",
      "settings.last_updated": "Terakhir Update",
      "settings.light": "Terang",
      "settings.dark": "Gelap (Segera Hadir)",
      "settings.indonesian": "Indonesia",
      "settings.english": "English",
      "settings.api_info": "API Keys akan digunakan oleh versi QuantumBotX berikutnya untuk mengakses broker non-MT5.",
      "settings.api_placeholder": "Fitur ini akan tersedia di QuantumBotX API versi mendatang.",

      // Trading Bots
      "bots.title": "Trading Bots",
      "bots.manage": "Kelola semua bot dan strategi Anda.",
      "bots.start_all_title": "Jalankan semua bot yang dijeda",
      "bots.stop_all_title": "Hentikan semua bot yang aktif",
      "bots.name_market": "Nama / Pasar",
      "bots.parameters": "Parameter",
      "bots.configuration": "Konfigurasi",
      "bots.actions": "Aksi",
      "bots.create_edit_modal": "Modal untuk Membuat/Mengedit Bot",
      "bots.create_new": "🚀 Buat Bot Baru",
      "bots.close_modal": "Tutup modal",
      "bots.row_name_market": "Baris 1: Nama & Pasar",
      "bots.row_lot_sl_tp": "Baris 2: Lot, SL, TP",
      "bots.row_timeframe_interval": "Baris 3: Timeframe & Interval",
      "bots.enable_strategy_switching": "Aktifkan Automatic Strategy Switching",
      "bots.strategy_switching_info": "Jika diaktifkan, bot akan secara otomatis beralih ke strategi terbaik berdasarkan kinerja terkini.",
      "bots.row_strategy_params": "Baris 4: Strategi & Parameternya",
      "bots.strategy_params_loaded": "Parameter strategi akan dimuat di sini oleh JavaScript",
      "bots.create_bot": "Buat Bot",
      "bots.cancel": "Batal",
      "bots.example_name": "Contoh: XAUUSD Hybrid H1",
      "bots.example_market": "Contoh: XAUUSD atau EURUSD",
      "bots.timeframe_1m": "1 Menit",
      "bots.timeframe_5m": "5 Menit",
      "bots.timeframe_15m": "15 Menit",
      "bots.timeframe_30m": "30 Menit",
      "bots.timeframe_1h": "1 Jam",
      "bots.timeframe_4h": "4 Jam",
      "bots.timeframe_1d": "1 Hari",
      "bots.select_strategy": "Pilih sebuah strategi",
      "bots.detail_title": "Detail Bot - QuantumBotX",

      // Profile
      "profile.title": "Profil",
      "profile.my_profile": "Profil Saya",
      "profile.loading": "Memuat...",
      "profile.joined_since": "Bergabung sejak: Juli 2025",
      "profile.save_changes": "Simpan Perubahan",
      "profile.password_placeholder": "••••••••",

      // Holidays
      "holiday.countdown.iftar": "⏱️ Hitung Mundur Iftar",
      "holiday.countdown.christmas": "🎄 Hitung Mundur Natal",
      "holiday.countdown.new_year": "🎆 Hitung Mundur Tahun Baru",
      "holiday.countdown.days_until": "hari lagi sampai",
      "holiday.patience_reminder": "🧘‍♂️ Pengingat Kesabaran",
      "holiday.risk_adjustment": "🛡️ Penyesuaian Risiko",
      "holiday.risk_reduction": "Pengurangan risiko otomatis",
      "holiday.optimal_trading_hours": "⏰ Waktu Trading Optimal",
      "holiday.christmas_greeting": "✨ Salam Natal",
      "holiday.lot_adjustment": "📏 Penyesuaian Lot",
      "holiday.lot_reduction": "Pengurangan ukuran lot",
      "holiday.new_year_resolution": "🎯 Resolusi Trading",
      "holiday.new_year_goal_setting": "Waktu yang tepat untuk menetapkan tujuan trading tahun ini",

      // Backtesting
      "backtest.enhanced_engine_active": "🚀 Enhanced Backtesting Engine Active",
      "backtest.includes": "Your backtesting now includes:",
      "backtest.realistic_spread": "Realistic spread costs",
      "backtest.actual_costs": "Actual trading costs deducted",
      "backtest.atr_risk": "ATR-based risk management",
      "backtest.dynamic_sizing": "Dynamic position sizing",
      "backtest.instrument_protection": "Instrument protection",
      "backtest.gold_safeguards": "Gold trading safeguards",
      "backtest.slippage": "Slippage simulation",
      "backtest.accurate_modeling": "More accurate execution modeling",
      "backtest.upload_data": "Unggah Data Historis (CSV)",
      "backtest.enhanced": "🚀 Enhanced",
      "backtest.dynamic_sl": "Dynamic SL based on volatility",
      "backtest.dynamic_tp": "Dynamic TP based on volatility",
      "backtest.run": "Jalankan Backtest",
      "backtest.results": "Hasil Backtest",
      "backtest.history_title": "Riwayat Backtest - QuantumBotX",
      "backtest.running": "Menjalankan simulasi...",

      // History
      "history.title": "Riwayat Transaksi Global",
      "history.description": "Semua transaksi yang telah ditutup dari akun MetaTrader 5.",
      "history.symbol": "Simbol",
      "history.type": "Tipe",
      "history.volume": "Volume",
      "history.profit": "Profit",
      "history.close_time": "Waktu Penutupan",
      "history.magic": "Magic Number",
      "history.loading": "Memuat riwayat...",

      // Portfolio
      "portfolio.title": "Portfolio Real-Time",
      "portfolio.description": "Posisi trading yang sedang terbuka di akun MetaTrader 5.",
      "portfolio.pnl_chart": "Grafik Profit/Loss Terbuka (Real-Time)",
      "portfolio.allocation_chart": "Alokasi Aset",
      "portfolio.symbol": "Simbol",
      "portfolio.type": "Tipe",
      "portfolio.volume": "Volume",
      "portfolio.open_price": "Harga Buka",
      "portfolio.profit_loss": "Profit/Loss",
      "portfolio.magic": "Magic Number",
      "portfolio.loading": "Memuat posisi terbuka...",

      // Market Data
      "market.forex_title": "Pasar Forex",
      "market.forex_description": "Data harga real-time dari pasar valuta asing.",
      "market.stocks_title": "Pasar Saham",
      "market.stocks_description": "Data harga real-time dari pasar saham global.",
      "market.pair": "Pasangan",
      "market.bid_price": "Harga Bid",
      "market.ask_price": "Harga Ask",
      "market.spread": "Spread",
      "market.stock": "Saham",
      "market.price": "Harga",
      "market.change_24h": "Perubahan 24j",
      "market.time": "Waktu",
      "market.loading": "Memuat data...",
      "market.close": "Close",

      // AI Mentor
      "ai_mentor.title": "🧠 AI Mentor Trading - QuantumBotX",
      "ai_mentor.page_title": "🧠 AI Mentor Trading - QuantumBotX",
      "ai_mentor.header": "🧠 AI Mentor Trading Indonesia",
      "ai_mentor.subtitle": "Mentor digital Anda untuk sukses trading jangka panjang",
      "ai_mentor.language": "🇮🇩 Bahasa Indonesia",
      "ai_mentor.realtime": "📊 Analisis Real-time",
      "ai_mentor.personal": "🎯 Personal",
      "ai_mentor.total_sessions": "Total Sesi",
      "ai_mentor.win_rate": "Win Rate",
      "ai_mentor.today": "Hari Ini",
      "ai_mentor.not_traded": "belum trading",
      "ai_mentor.ai_status": "Status AI",
      "ai_mentor.ai_active": "🤖 Aktif",
      "ai_mentor.ai_ready": "siap menganalisis",
      "ai_mentor.today_trading": "📊 Trading Hari Ini",
      "ai_mentor.total_trades": "Total Trades:",
      "ai_mentor.pnl": "P&L:",
      "ai_mentor.emotion": "Emosi:",
      "ai_mentor.your_notes": "Catatan Anda:",
      "ai_mentor.view_full_analysis": "🧠 Lihat Analisis AI Lengkap",
      "ai_mentor.update_emotion": "✏️ Update Emosi & Catatan",
      "ai_mentor.not_traded_today": "Belum Ada Trading Hari Ini",
      "ai_mentor.start_trading": "Mulai trading untuk mendapatkan analisis AI yang personal!",
      "ai_mentor.record_emotion": "📝 Catat Emosi Trading",
      "ai_mentor.ai_insights": "🤖 AI Insights Terbaru",
      "ai_mentor.no_insights": "AI Siap Membantu!",
      "ai_mentor.start_trading_insights": "Mulai trading untuk mendapatkan insight personal dari AI mentor Anda.",
      "ai_mentor.view_history": "📚 Lihat Semua Riwayat",
      "ai_mentor.daily_tips": "💡 Tips Harian dari AI Mentor",
      "ai_mentor.consistency": "🎯 Konsistensi",
      "ai_mentor.consistency_tip": "Profit kecil tapi konsisten lebih baik daripada profit besar sekali terus loss.",
      "ai_mentor.risk_management": "🛡️ Risk Management",
      "ai_mentor.risk_tip": "Jangan pernah risiko lebih dari 2% modal per trade. Modal adalah nyawa trader!",
      "ai_mentor.emotions": "🧠 Emosi",
      "ai_mentor.emotion_tip": "Trading dengan emosi tenang adalah kunci trader profesional. Istirahat jika frustasi.",
      "ai_mentor.chat_with_mentor": "💬 Chat dengan AI Mentor",
      "ai_mentor.developing": "Fitur sedang dikembangkan...",
      "ai_mentor.use_dashboard": "Sementara ini, gunakan dashboard untuk melihat analisis AI.",
      "ai_mentor.history_page_title": "📊 Riwayat AI Mentor - QuantumBotX",
      "ai_mentor.report_page_title": "📊 Laporan AI Mentor - QuantumBotX",
      // Consolidated AI Mentor section (removed massive duplications)
      "ai_mentor.holiday_risk_reduction": "⚠️ Risk otomatis dikurangi {{ (100 - holiday_config.adjustments.risk_reduction * 100)|int }}% untuk periode liburan",
      "ai_mentor.holiday": "• {{ holiday_config.active_holiday.split()[0] }} 🎄",
      "ai_mentor.language_indonesian": "🇮🇩 Bahasa Indonesia",
      "ai_mentor.realtime_analysis": "📊 Analisis Real-time",
      "ai_mentor.sessions": "sesi trading",
      "ai_mentor.profit_sessions": "sesi profit",
      "ai_mentor.no_trading": "belum trading",
      "ai_mentor.ai_status": "Status AI",
      "ai_mentor.ai_active": "🤖 Aktif",
      "ai_mentor.ready_to_analyze": "siap menganalisis",
      "ai_mentor.todays_trading": "Trading Hari Ini",
      "ai_mentor.view_full_analysis": "🧠 Lihat Analisis AI Lengkap",
      "ai_mentor.update_emotion": "✏️ Update Emosi & Catatan",
      "ai_mentor.record_emotion": "📝 Catat Emosi Trading",
      "ai_mentor.latest_insights": "AI Insights Terbaru",
      "ai_mentor.view_all_history": "📚 Lihat Semua Riwayat",
      "ai_mentor.ai_ready": "AI Siap Membantu!",
      "ai_mentor.start_trading_for_insights": "Mulai trading untuk mendapatkan insight personal dari AI mentor Anda.",
      "ai_mentor.daily_tips": "Tips Harian dari AI Mentor",
      "ai_mentor.consistency": "🎯 Konsistensi",
      "ai_mentor.consistency_tip": "Profit kecil tapi konsisten lebih baik daripada profit besar sekali terus loss.",
      "ai_mentor.risk_management": "🛡️ Risk Management",
      "ai_mentor.risk_management_tip": "Jangan pernah risiko lebih dari 2% modal per trade. Modal adalah nyawa trader!",
      "ai_mentor.emotion": "🧠 Emosi",
      "ai_mentor.emotion_tip": "Trading dengan emosi tenang adalah kunci trader profesional. Istirahat jika frustasi.",
      "ai_mentor.chat_with_mentor": "💬 Chat dengan AI Mentor",
      "ai_mentor.feature_development": "Fitur sedang dikembangkan...",
      "ai_mentor.use_dashboard": "Sementara ini, gunakan dashboard untuk melihat analisis AI.",
      "ai_mentor.report_title": "📊 Laporan AI Mentor",
      "ai_mentor.report_subtitle": "Analisis personal untuk {{ session_data.session_date if session_data else 'Hari Ini' }}",
      "ai_mentor.created_by_ai": "🤖 Dibuat oleh AI",
      "ai_mentor.real_data": "📈 Data Real",
      "ai_mentor.trades": "trades",
      "ai_mentor.no_data": "No data",
      "ai_mentor.back_to_dashboard": "Kembali ke Dashboard",
      "ai_mentor.report_history": "Riwayat Laporan",
      "ai_mentor.trading_summary": "Ringkasan Trading",
      "ai_mentor.profit_loss": "Profit/Loss",
      "ai_mentor.emotional_condition": "Kondisi Emosi",
      "ai_mentor.market_conditions": "Kondisi Market",
      "ai_mentor.trading_patterns": "Analisis Pola Trading",
      "ai_mentor.main_pattern": "Pola Utama:",
      "ai_mentor.strength": "Kekuatan:",
      "ai_mentor.improvement_areas": "Area Perbaikan:",
      "ai_mentor.emotional_analysis": "Analisis Emosi vs Performa",
      "ai_mentor.emotional_feedback": "Feedback Emosi:",
      "ai_mentor.tip": "Tip:",
      "ai_mentor.risk_management_analysis": "Evaluasi Manajemen Risiko",
      "ai_mentor.recommendations": "Rekomendasi AI Mentor",
      "ai_mentor.motivational_message": "Pesan Motivasi",
      "ai_mentor.trade_details": "Detail Trades Hari Ini",
      "ai_mentor.lot_size": "Lot: {{ trade.lot_size }}",
      "ai_mentor.sl": "SL: {{ '✅' if trade.stop_loss_used else '❌' }}",
      "ai_mentor.tp": "TP: {{ '✅' if trade.take_profit_used else '❌' }}",
      "ai_mentor.personal_notes": "Catatan Pribadi Anda",
      "ai_mentor.no_trading_data": "Belum Ada Data Trading",
      "ai_mentor.back_to_dashboard_button": "Kembali ke Dashboard",
      "ai_mentor.full_report": "Laporan AI Lengkap",
      "ai_mentor.view_full_report": "Lihat Laporan Lengkap",
      "ai_mentor.history_title": "📊 Riwayat AI Mentor Trading",
      "ai_mentor.history_subtitle": "Analisis lengkap perjalanan trading Anda dengan bantuan AI Indonesia",
      "ai_mentor.performance_analysis": "📈 Analisis Performa",
      "ai_mentor.ai_insights": "🧠 AI Insights",
      "ai_mentor.total_reports": "Total Laporan",
      "ai_mentor.sessions_analyzed": "sesi dianalisis",
      "ai_mentor.period": "Periode",
      "ai_mentor.days": "hari",
      "ai_mentor.last_history": "riwayat terakhir",
      "ai_mentor.performance": "Performa",
      "ai_mentor.total_pnl": "total P&L",
      "ai_mentor.profit_sessions": "sesi profit",
      "ai_mentor.period_filter": "Filter Periode",
      "ai_mentor.filter_7_days": "7 Hari",
      "ai_mentor.filter_30_days": "30 Hari",
      "ai_mentor.filter_90_days": "90 Hari",
      "ai_mentor.filter_1_year": "1 Tahun",
      "ai_mentor.trading_session": "Sesi Trading",
      "ai_mentor.ai_summary": "🤖 AI Summary:",
      "ai_mentor.market": "Market",
      "ai_mentor.view_details": "Lihat Detail →",
      "ai_mentor.load_more": "Muat Lebih Banyak",
      "ai_mentor.no_history": "Belum Ada Riwayat Trading",
      "ai_mentor.start_trading_for_history": "Mulai trading untuk mendapatkan analisis AI dan saran personal dari mentor digital Anda.",
      "ai_mentor.start_trading_session": "Mulai Trading Session",
      "ai_mentor.view_trading_bots": "Lihat Trading Bots",
      "ai_mentor.how_are_you_feeling": "🧠 Bagaimana perasaan Anda saat trading hari ini?",
      "ai_mentor.emotion_calm": "😌 Tenang",
      "ai_mentor.calm_description": "Pikiran jernih, tidak terburu-buru",
      "ai_mentor.emotion_greedy": "🤑 Serakah",
      "ai_mentor.greedy_description": "Ingin profit besar, agresif",
      "ai_mentor.emotion_fearful": "😰 Takut",
      "ai_mentor.fearful_description": "Khawatir loss, ragu-ragu",
      "ai_mentor.emotion_frustrated": "😤 Frustasi",
      "ai_mentor.frustrated_description": "Kesal karena loss beruntun",
      "ai_mentor.today_pnl": "💰 P&L Hari Ini (USD)",
      "ai_mentor.pnl_placeholder": "Contoh: 25.50 atau -15.30",
      "ai_mentor.today_notes": "📝 Catatan Trading Hari Ini",
      "ai_mentor.notes_placeholder": "Contoh: Hari ini fokus EURUSD, pakai SL ketat. Market agak volatile karena berita NFP...",
      "ai_mentor.instant_feedback": "⚡ Feedback Instan",
      "ai_mentor.save_data": "💾 Simpan Data",
      "ai_mentor.ai_feedback": "🤖 Feedback AI Mentor:",
      "ai_mentor.analyzing": "🤖 AI sedang menganalisis trading Anda...",
      "ai_mentor.emotional_analysis": "🧠 Analisis Emosi:",
      "ai_mentor.motivation": "💪 Motivasi:",
      "ai_mentor.quick_tips": "💡 Tips Cepat:",
      "ai_mentor.failed_feedback": "❌ Gagal mendapatkan feedback. Silakan coba lagi.",
      "ai_mentor.session_trading_detail": "📈 Detail Sesi Trading",
      "ai_mentor.full_analysis": "Analisis lengkap dari AI Mentor Indonesia",
      "ai_mentor.ai_analysis": "🇮🇩 AI Analysis",
      "ai_mentor.personal_insights": "🧠 Personal Insights",
      "ai_mentor.performance_review": "📊 Performance Review",
      "ai_mentor.total_pnl": "Total P&L",
      "ai_mentor.total_trades": "Total Trades",
      "ai_mentor.emotional_state": "Emotional State",
      "ai_mentor.trading_summary": "📊 Ringkasan Trading",
      "ai_mentor.market_context": "🌐 Konteks Pasar",
      "ai_mentor.market_conditions": "Kondisi Pasar",
      "ai_mentor.personal_notes": "📝 Catatan Pribadi Anda",
      "ai_mentor.ai_mentor_report": "🤖 Laporan AI Mentor",
      "ai_mentor.emotional_analysis_vs_performance": "💭 Analisis Emosi vs Performa",
      "ai_mentor.emotional_status": "Status Emosi: {{ session_data.emotions|title if session_data.emotions else 'Tidak Tercatat' }}",
      "ai_mentor.emotional_advice": "💡 Saran Emosional",
      "ai_mentor.ai_recommendations": "🎯 Rekomendasi AI",
      "ai_mentor.motivation_inspiration": "🚀 Motivasi & Inspirasi",
      "ai_mentor.learning_points": "📚 Poin Pembelajaran",
      "ai_mentor.back_to_history": "Kembali ke Riwayat",
      "ai_mentor.back_to_history_button": "← Kembali ke Riwayat",
      "ai_mentor.ai_mentor_dashboard": "Dashboard AI Mentor",
      "ai_mentor.reanalyze": "🔄 Analisis Ulang",
      "ai_mentor.session_detail_title": "📈 Detail Sesi {{ session_date }} - AI Mentor - QuantumBotX",
      "ai_mentor.settings_title": "⚙️ Pengaturan AI Mentor",
      "ai_mentor.settings_subtitle": "Kustomisasi pengalaman AI Trading Mentor sesuai preferensi Anda",
      "ai_mentor.indonesia_setup": "🇮🇩 Indonesia Setup",
      "ai_mentor.realtime_config": "⚡ Real-time Config",
      "ai_mentor.personal": "🎯 Personal",
      "ai_mentor.language_regional": "🌏 Bahasa & Regional",
      "ai_mentor.interface_language": "Bahasa Interface",
      "ai_mentor.language_choice": "Pilih bahasa untuk AI Mentor",
      "ai_mentor.timezone": "Zona Waktu",
      "ai_mentor.timezone_description": "Zona waktu untuk analisis trading",
      "ai_mentor.timezone_wib": "WIB (UTC+7) - Jakarta Time",
      "ai_mentor.currency_format": "Format Mata Uang",
      "ai_mentor.currency_display": "Format tampilan profit/loss",
      "ai_mentor.ai_behavior": "🧠 Perilaku AI Mentor",
      "ai_mentor.automatic_analysis": "Analisis Otomatis",
      "ai_mentor.automatic_analysis_description": "AI menganalisis setiap sesi trading secara otomatis",
      "ai_mentor.emotional_feedback": "Feedback Emosional",
      "ai_mentor.emotional_feedback_description": "AI memberikan feedback berdasarkan kondisi emosi",
      "ai_mentor.daily_motivation": "Motivasi Harian",
      "ai_mentor.daily_motivation_description": "Terima pesan motivasi setiap hari",
      "ai_mentor.analysis_detail_level": "Level Detail Analisis",
      "ai_mentor.analysis_detail_description": "Tingkat detail feedback AI",
      "ai_mentor.basic": "Basic",
      "ai_mentor.detailed": "Detailed",
      "ai_mentor.expert": "Expert",
      "ai_mentor.notifications": "🔔 Notifikasi",
      "ai_mentor.daily_report": "Laporan Harian",
      "ai_mentor.daily_report_time": "Waktu pengiriman laporan AI harian",
      "ai_mentor.timezone_wib_short": "WIB",
      "ai_mentor.trading_reminder": "Reminder Trading",
      "ai_mentor.trading_reminder_description": "Pengingat untuk input emosi dan catatan",
      "ai_mentor.overtrading_alert": "Alert Overtrading",
      "ai_mentor.overtrading_alert_description": "Peringatan jika terlalu banyak trading",
      "ai_mentor.cultural_preferences": "🎭 Preferensi Budaya",
      "ai_mentor.automatic_holiday_mode": "Mode Liburan Otomatis",
      "ai_mentor.automatic_holiday_mode_description": "Aktifkan mode Ramadan dan Natal secara otomatis",
      "ai_mentor.ramadan_risk_adjustment": "Penyesuaian Risk Ramadan",
      "ai_mentor.ramadan_risk_adjustment_description": "Kurangi risk otomatis selama bulan Ramadan",
      "ai_mentor.sahur_iftar_pause": "Pause Trading Sahur/Iftar",
      "ai_mentor.sahur_iftar_pause_description": "Hentikan trading otomatis saat waktu sahur dan iftar",
      "ai_mentor.data_privacy": "🔒 Data & Privacy",
      "ai_mentor.save_ai_history": "Simpan Riwayat AI",
      "ai_mentor.save_ai_history_description": "Berapa lama menyimpan analisis AI",
      "ai_mentor.30_days": "30 Hari",
      "ai_mentor.90_days": "90 Hari",
      "ai_mentor.1_year": "1 Tahun",
      "ai_mentor.unlimited": "Unlimited",
      "ai_mentor.export_data": "Export Data",
      "ai_mentor.export_data_description": "Download semua data AI Mentor Anda",
      "ai_mentor.export": "📥 Export",
      "ai_mentor.reset_all_data": "Reset Semua Data",
      "ai_mentor.reset_all_data_description": "⚠️ Hapus semua riwayat dan analisis AI",
      "ai_mentor.reset": "🗑️ Reset",
      "ai_mentor.save_settings": "💾 Simpan Pengaturan",
      "ai_mentor.reset_to_defaults": "🔄 Reset ke Default",

      // Strategy Switcher
      "strategy_switcher.title": "Dasbor Strategy Switcher",
      "strategy_switcher.header": "🔄 Automatic Strategy Switcher",
      "strategy_switcher.subtitle": "Pemantauan real-time dan analitik performa untuk pengalihan strategi otomatis",
      "strategy_switcher.current_status": "Status Saat Ini",
      "strategy_switcher.manual_evaluate": "Evaluasi Manual",
      "strategy_switcher.loading": "Memuat...",
      "strategy_switcher.cooldown_active": "Cooldown Aktif",
      "strategy_switcher.active": "Aktif",
      "strategy_switcher.active_strategy": "Strategi Aktif",
      "strategy_switcher.active_symbol": "Simbol Aktif",
      "strategy_switcher.last_switch": "Peralihan Terakhir",
      "strategy_switcher.never": "Tidak Pernah",
      "strategy_switcher.performance_rankings": "📊 Peringkat Performa Strategi",
      "strategy_switcher.refresh_rankings": "Segarkan Peringkat",
      "strategy_switcher.rank": "Peringkat",
      "strategy_switcher.strategy_symbol": "Strategi/Simbol",
      "strategy_switcher.composite_score": "Skor Komposit",
      "strategy_switcher.profitability": "Profitabilitas",
      "strategy_switcher.risk_control": "Kontrol Risiko",
      "strategy_switcher.market_fit": "Kesesuaian Pasar",
      "strategy_switcher.no_rankings": "Tidak ada peringkat strategi yang tersedia",
      "strategy_switcher.recent_switches": "⚡ Peralihan Strategi Terbaru",
      "strategy_switcher.refresh_switches": "Segarkan Peralihan",
      "strategy_switcher.no_switches": "Belum ada peralihan strategi yang dicatat.",
      "strategy_switcher.monitored_instruments": "🔍 Instrumen & Strategi yang Dipantau",
      "strategy_switcher.instruments": "Instrumen",
      "strategy_switcher.strategies": "Strategi",
      "strategy_switcher.none": "Tidak Ada",
      "strategy_switcher.switch_from": "Beralih dari",
      "strategy_switcher.switch_to": "ke",
      "strategy_switcher.initialized_with": "Diinisialisasi dengan",
      "strategy_switcher.manual_trigger_confirm": "Apakah Anda yakin ingin memicu evaluasi strategi secara manual?",
      "strategy_switcher.loading_strategy_rankings": "Memuat peringkat strategi...",
      "strategy_switcher.loading_recent_switches": "Memuat peralihan terbaru...",
      "strategy_switcher.monitored_instruments_strategies": "🔍 Instrumen & Strategi yang Dipantau",
      "strategy_switcher.score": "Skor:",
      "strategy_switcher.no_strategy_rankings": "Tidak ada peringkat strategi yang tersedia",
      "strategy_switcher.switched_from": "Beralih dari",
      "strategy_switcher.switched_to": "ke",
      "strategy_switcher.no_strategy_switches": "Belum ada peralihan strategi yang dicatat.",
      "strategy_switcher.strategy_performance_rankings": "📊 Peringkat Performa Strategi",
      "strategy_switcher.recent_strategy_switches": "⚡ Peralihan Strategi Terbaru",

      // Ramadan
      "ramadan.title": "Ramadan Trading Mode",
      "ramadan.page_title": "🌙 Ramadan Trading Mode - QuantumBotX",
      "ramadan.header": "🌙 Ramadan Trading Mode",
      "ramadan.subtitle": "Bulan suci dengan fitur trading yang menghormati ibadah puasa",
      "ramadan.info": "Mode ini aktif secara otomatis selama bulan Ramadan dan akan menyesuaikan pengaturan trading Anda untuk menghormati waktu ibadah. Anda tidak perlu mengaktifkannya secara manual.",
      "ramadan.status": "Status Ramadan",
      "ramadan.period": "Periode Ramadan",
      "ramadan.greeting": "Salam Ramadan",
      "ramadan.iftar_countdown": "⏱️ Hitung Mundur Iftar",
      "ramadan.hours": "Jam",
      "ramadan.minutes": "Menit",
      "ramadan.until": "Sampai",
      "ramadan.trading_adjustments": "⚙️ Penyesuaian Trading",
      "ramadan.fasting_times": "Waktu Istirahat Puasa",
      "ramadan.suhoor": "Sahur",
      "ramadan.suhoor_time": "03:30 - 05:00 WIB",
      "ramadan.iftar_time": "Iftar",
      "ramadan.iftar_time_range": "18:00 - 19:30 WIB",
      "ramadan.tarawih": "Tarawih",
      "ramadan.tarawih_time": "20:00 - 21:30 WIB",
      "ramadan.risk_adjustments": "Penyesuaian Risiko",
      "ramadan.reduced_risk_mode": "Reduced Risk Mode",
      "ramadan.reduced_risk_description": "20% pengurangan risiko selama puasa",
      "ramadan.patience_mode": "Patience Mode",
      "ramadan.patience_mode_description": "Fokus pada kualitas bukan kuantitas",
      "ramadan.optimal_hours": "Optimal Hours",
      "ramadan.optimal_hours_time": "22:00 - 03:00 WIB",
      "ramadan.zakat_calculator": "💰 Kalkulator Zakat Trading",
      "ramadan.zakat_information": "Informasi Zakat",
      "ramadan.gold_nisab": "Nisab Emas",
      "ramadan.silver_nisab": "Nisab Perak",
      "ramadan.zakat_percentage": "Persentase Zakat",
      "ramadan.zakat_reminder": "Pengingat Zakat",
      "ramadan.zakat_trading_reminder": "Zakat perdagangan: 2.5% dari profit trading selama 1 tahun hijriah. Jangan lupa menghitung zakat dari profit trading Anda selama Ramadan.",
      "ramadan.patience_reminder": "🧘‍♂️ Pengingat Kesabaran",
      "ramadan.loading": "Loading...",
      "ramadan.active": "Aktif",
      "ramadan.inactive": "Tidak Aktif",
      "ramadan.not_ramadan": "Bukan periode Ramadan",
      "ramadan.default_greeting": "Saatnya berpuasa, saatnya trading dengan berkah",

      // Other
      "common.close": "Tutup",
      "common.yes": "Ya",
      "common.no": "Tidak",
      
      // Notifications
      "notifications.loading": "Memuat notifikasi...",
      
      // AI Mentor Settings
      "ai_mentor.settings_title": "⚙️ Pengaturan AI Mentor - QuantumBotX"
    },
    en: {
      // Navigation & Common
      "nav.dashboard": "Dashboard",
      "nav.bots": "Trading Bots",
      "nav.backtest": "Backtester",
      "nav.history": "History",
      "nav.ai_mentor": "AI Mentor",
      "nav.strategy_switcher": "Strategy Switcher",
      "nav.ramadan": "Ramadan Mode",
      "nav.settings": "Settings",
      "nav.portfolio": "Portfolio",
      "nav.stocks": "Stocks",
      "nav.forex": "Forex",
      "nav.notifications": "Notifications",
      "nav.section.navigation": "Navigation",
      "nav.section.market_data": "Market Data",

      // Dashboard
      "dashboard.title": "QuantumBotX Dashboard",
      "dashboard.welcome": "Welcome",
      "dashboard.welcome_back": "Welcome back! Here's your trading summary for today.",
      "dashboard.total_bots": "Total Bots",
      "dashboard.active_bots": "Active Bots",
      "dashboard.inactive_bots": "Inactive Bots",
      "dashboard.total_profit": "Total Profit",
      "dashboard.today_pnl": "Today's P&L",
      "dashboard.create_bot": "Create New Bot",
      "dashboard.view_details": "View Details",
      "dashboard.total_equity": "Total Balance (Equity)",
      "dashboard.today_profit": "Today's Profit",
      "dashboard.ai_mentor": "🤖 AI Mentor",
      "dashboard.ai_mentor_ready": "Ready to Help",
      "dashboard.ai_mentor_active": "Actively Analyzing",
      "dashboard.view_analysis": "View Analysis →",
      "dashboard.emotion_status": "Emotion Status",
      "dashboard.update_status": "Update Status",
      "dashboard.ai_mentor_today": "🧠 AI Mentor Today",
      "dashboard.trading_analysis": "Trading Analysis:",
      "dashboard.daily_tip": "Daily Tip:",
      "dashboard.view_full_report": "📊 View Full Report",
      "dashboard.recent_activities": "⚡ Recent Activities",
      "dashboard.loading_activities": "Loading activities...",
      "dashboard.active_trading_bots": "Active Trading Bots",
      "dashboard.loading_bot_list": "Loading bot list...",
      "dashboard.view_all_bots": "View All Bots",
      "dashboard.chat_with_ai_mentor": "Chat with AI Mentor",
      "dashboard.price_chart": "📈 EUR/USD Price Chart",
      "dashboard.loading": "Loading...",
      "dashboard.rsi_chart": "📊 EUR/USD RSI (H1)",
      "dashboard.real_time": "Real-time",
      "dashboard.no_active_bots": "No active bots",
      "dashboard.emotion_calm": "😌 Calm",
      "dashboard.emotion_greedy": "🤑 Greedy",
      "dashboard.emotion_fear": "😰 Fear",
      "dashboard.emotion_frustrated": "😤 Frustrated",
      "dashboard.emotion_neutral": "😐 Neutral",
      "dashboard.update_emotion_status": "🎯 Update Emotion Status",
      "dashboard.cancel": "Cancel",
      "dashboard.emotion_updated": "Emotion status updated successfully!",
      "dashboard.emotion_update_failed": "Failed to update emotion status",
      "dashboard.error_updating_emotion": "Error: Failed to update emotion status",

      // Bot Status
      "status.active": "Active",
      "status.inactive": "Inactive",
      "status.error": "Error",
      "status.paused": "Paused",

      // Action Buttons
      "action.start": "Start",
      "action.stop": "Stop",
      "action.edit": "Edit",
      "action.delete": "Delete",
      "action.view": "View",
      "action.analyze": "Analyze",
      "action.start_all": "Start All",
      "action.stop_all": "Stop All",
      "action.create_new_bot": "Create New Bot",

      // Form Labels & Messages
      "label.name": "Name",
      "label.market": "Market",
      "label.strategy": "Strategy",
      "label.status": "Status",
      "label.profit": "Profit",
      "label.trades": "Trades",
      "label.win_rate": "Win Rate",
      "label.bot_name": "Bot Name",
      "label.risk_per_trade": "Risk per Trade (%)",
      "label.sl_atr": "SL (ATR Multiplier)",
      "label.tp_atr": "TP (ATR Multiplier)",
      "label.timeframe": "Timeframe",
      "label.check_interval": "Check Interval (seconds)",
      "label.full_name": "Full Name",
      "label.email": "Email Address",
      "label.password": "Change Password (leave blank if you don't want to change it)",

      "msg.loading": "Loading...",
      "msg.no_data": "No data available",
      "msg.success": "Success",
      "msg.error": "Error",
      "msg.confirm": "Are you sure?",
      "msg.save_changes": "Save Changes",
      "msg.save_preferences": "Save Preferences",

      // Time & Date
      "time.today": "Today",
      "time.yesterday": "Yesterday",
      "time.week": "This Week",
      "time.month": "This Month",

      // Error Messages
      "error.connection": "Failed to connect to server",
      "error.loading": "Failed to load data",
      "error.save": "Failed to save changes",
      "error.404_title": "Page Not Found - QuantumBotX",
      "error.404_heading": "Page Not Found",
      "error.404_message": "Sorry, the page you're looking for doesn't exist or has been moved.",
      "error.500_title": "Internal Server Error - QuantumBotX",
      "error.500_heading": "Internal Server Error",
      "error.500_message": "Sorry, there was a problem with our server. Our team has been notified and is working on it.",
      "error.back_to_dashboard": "Back to Dashboard",

      // AI Mentor
      "mentor.greeting": "Hello, Trading Friend!",
      "mentor.welcome": "Welcome to my AI trading system",

      // Units & Currencies
      "currency.usd": "USD",
      "currency.idr": "IDR",
      "currency.percentage": "%",

      // Settings
      "settings.title": "Settings",
      "settings.language": "Language",
      "settings.theme": "Theme",
      "settings.save": "Save Changes",
      "settings.profile": "Profile",
      "settings.preferences": "Preferences",
      "settings.api_keys": "Exchange API Keys",
      "settings.quick_settings": "Quick Settings",
      "settings.email_notifications": "Email Notifications",
      "settings.auto_update": "Auto Update Strategies",
      "settings.demo_mode": "Demo Mode",
      "settings.version": "Version",
      "settings.last_updated": "Last Updated",
      "settings.light": "Light",
      "settings.dark": "Dark (Coming Soon)",
      "settings.indonesian": "Indonesian",
      "settings.english": "English",
      "settings.api_info": "API Keys will be used by the next version of QuantumBotX to access non-MT5 brokers.",
      "settings.api_placeholder": "This feature will be available in the next QuantumBotX API version.",

      // Trading Bots
      "bots.title": "Trading Bots",
      "bots.manage": "Manage all your bots and strategies.",
      "bots.start_all_title": "Start all paused bots",
      "bots.stop_all_title": "Stop all active bots",
      "bots.name_market": "Name / Market",
      "bots.parameters": "Parameters",
      "bots.configuration": "Configuration",
      "bots.actions": "Actions",
      "bots.create_edit_modal": "Modal for Creating/Editing Bot",
      "bots.create_new": "🚀 Create New Bot",
      "bots.close_modal": "Close modal",
      "bots.row_name_market": "Row 1: Name & Market",
      "bots.row_lot_sl_tp": "Row 2: Lot, SL, TP",
      "bots.row_timeframe_interval": "Row 3: Timeframe & Interval",
      "bots.enable_strategy_switching": "Enable Automatic Strategy Switching",
      "bots.strategy_switching_info": "If enabled, the bot will automatically switch to the best strategy based on current performance.",
      "bots.row_strategy_params": "Row 4: Strategy & Its Parameters",
      "bots.strategy_params_loaded": "Strategy parameters will be loaded here by JavaScript",
      "bots.create_bot": "Create Bot",
      "bots.cancel": "Cancel",
      "bots.example_name": "Example: XAUUSD Hybrid H1",
      "bots.example_market": "Example: XAUUSD or EURUSD",
      "bots.timeframe_1m": "1 Minute",
      "bots.timeframe_5m": "5 Minutes",
      "bots.timeframe_15m": "15 Minutes",
      "bots.timeframe_30m": "30 Minutes",
      "bots.timeframe_1h": "1 Hour",
      "bots.timeframe_4h": "4 Hours",
      "bots.timeframe_1d": "1 Day",
      "bots.select_strategy": "Select a strategy",
      "bots.detail_title": "Bot Detail - QuantumBotX",

      // Profile
      "profile.title": "Profile",
      "profile.my_profile": "My Profile",
      "profile.loading": "Loading...",
      "profile.joined_since": "Joined since: July 2025",
      "profile.save_changes": "Save Changes",
      "profile.password_placeholder": "••••••••",

      // Holidays
      "holiday.countdown.iftar": "⏱️ Iftar Countdown",
      "holiday.countdown.christmas": "🎄 Christmas Countdown",
      "holiday.countdown.new_year": "🎆 New Year Countdown",
      "holiday.countdown.days_until": "days until",
      "holiday.patience_reminder": "🧘‍♂️ Patience Reminder",
      "holiday.risk_adjustment": "🛡️ Risk Adjustment",
      "holiday.risk_reduction": "Automatic risk reduction",
      "holiday.optimal_trading_hours": "⏰ Optimal Trading Hours",
      "holiday.christmas_greeting": "✨ Christmas Greeting",
      "holiday.lot_adjustment": "📏 Lot Adjustment",
      "holiday.lot_reduction": "Lot size reduction",
      "holiday.new_year_resolution": "🎯 Trading Resolution",
      "holiday.new_year_goal_setting": "The perfect time to set your trading goals for the year",

      // Backtesting
      "backtest.enhanced_engine_active": "🚀 Enhanced Backtesting Engine Active",
      "backtest.includes": "Your backtesting now includes:",
      "backtest.realistic_spread": "Realistic spread costs",
      "backtest.actual_costs": "Actual trading costs deducted",
      "backtest.atr_risk": "ATR-based risk management",
      "backtest.dynamic_sizing": "Dynamic position sizing",
      "backtest.instrument_protection": "Instrument protection",
      "backtest.gold_safeguards": "Gold trading safeguards",
      "backtest.slippage": "Slippage simulation",
      "backtest.accurate_modeling": "More accurate execution modeling",
      "backtest.upload_data": "Upload Historical Data (CSV)",
      "backtest.enhanced": "🚀 Enhanced",
      "backtest.dynamic_sl": "Dynamic SL based on volatility",
      "backtest.dynamic_tp": "Dynamic TP based on volatility",
      "backtest.run": "Run Backtest",
      "backtest.results": "Backtest Results",
      "backtest.history_title": "Backtest History - QuantumBotX",
      "backtest.running": "Running simulation...",

      // History
      "history.title": "Global Transaction History",
      "history.description": "All closed transactions from the MetaTrader 5 account.",
      "history.symbol": "Symbol",
      "history.type": "Type",
      "history.volume": "Volume",
      "history.profit": "Profit",
      "history.close_time": "Close Time",
      "history.magic": "Magic Number",
      "history.loading": "Loading history...",

      // Portfolio
      "portfolio.title": "Real-Time Portfolio",
      "portfolio.description": "Open trading positions in the MetaTrader 5 account.",
      "portfolio.pnl_chart": "Open Profit/Loss Chart (Real-Time)",
      "portfolio.allocation_chart": "Asset Allocation",
      "portfolio.symbol": "Symbol",
      "portfolio.type": "Type",
      "portfolio.volume": "Volume",
      "portfolio.open_price": "Open Price",
      "portfolio.profit_loss": "Profit/Loss",
      "portfolio.magic": "Magic Number",
      "portfolio.loading": "Loading open positions...",

      // Market Data
      "market.forex_title": "Forex Market",
      "market.forex_description": "Real-time price data from the foreign exchange market.",
      "market.stocks_title": "Stocks Market",
      "market.stocks_description": "Real-time price data from the global stock market.",
      "market.pair": "Pair",
      "market.bid_price": "Bid Price",
      "market.ask_price": "Ask Price",
      "market.spread": "Spread",
      "market.stock": "Stock",
      "market.price": "Price",
      "market.change_24h": "24h Change",
      "market.time": "Time",
      "market.loading": "Loading data...",
      "market.close": "Close",

      // AI Mentor
      "ai_mentor.title": "🧠 AI Trading Mentor - QuantumBotX",
      "ai_mentor.page_title": "🧠 AI Mentor Trading - QuantumBotX",
      "ai_mentor.header": "🧠 AI Trading Mentor",
      "ai_mentor.subtitle": "Your digital mentor for long-term trading success",
      "ai_mentor.language": "🇺🇸 English Language",
      "ai_mentor.realtime": "📊 Real-time Analysis",
      "ai_mentor.personal": "🎯 Personal",
      "ai_mentor.total_sessions": "Total Sessions",
      "ai_mentor.win_rate": "Win Rate",
      "ai_mentor.today": "Today",
      "ai_mentor.not_traded": "not traded yet",
      "ai_mentor.ai_status": "AI Status",
      "ai_mentor.ai_active": "🤖 Active",
      "ai_mentor.ai_ready": "ready to analyze",
      "ai_mentor.today_trading": "📊 Today's Trading",
      "ai_mentor.total_trades": "Total Trades:",
      "ai_mentor.pnl": "P&L:",
      "ai_mentor.emotion": "Emotion:",
      "ai_mentor.your_notes": "Your Notes:",
      "ai_mentor.view_full_analysis": "🧠 View Full AI Analysis",
      "ai_mentor.update_emotion": "✏️ Update Emotion & Notes",
      "ai_mentor.not_traded_today": "No Trading Today Yet",
      "ai_mentor.start_trading": "Start trading to get personalized AI analysis!",
      "ai_mentor.record_emotion": "📝 Record Trading Emotion",
      "ai_mentor.ai_insights": "🤖 Latest AI Insights",
      "ai_mentor.no_insights": "AI is Ready to Help!",
      "ai_mentor.start_trading_insights": "Start trading to get personalized insights from your AI mentor.",
      "ai_mentor.view_history": "📚 View All History",
      "ai_mentor.daily_tips": "💡 Daily Tips from AI Mentor",
      "ai_mentor.consistency": "🎯 Consistency",
      "ai_mentor.consistency_tip": "Small but consistent profits are better than one big profit followed by losses.",
      "ai_mentor.risk_management": "🛡️ Risk Management",
      "ai_mentor.risk_tip": "Never risk more than 2% of your capital per trade. Capital is a trader's life!",
      "ai_mentor.emotions": "🧠 Emotions",
      "ai_mentor.emotion_tip": "Trading with a calm emotion is the key to professional trading. Take a break if frustrated.",
      "ai_mentor.chat_with_mentor": "💬 Chat with AI Mentor",
      "ai_mentor.developing": "Feature under development...",
      "ai_mentor.use_dashboard": "For now, use the dashboard to view AI analysis.",
      "ai_mentor.history_page_title": "📊 AI Mentor History - QuantumBotX",
      "ai_mentor.report_page_title": "📊 AI Mentor Report - QuantumBotX",
      "ai_mentor.session_detail_title": "📈 Session Detail {{ session_date }} - AI Mentor - QuantumBotX",
      "ai_mentor.holiday": "• {{ holiday_config.active_holiday.split()[0] }} 🎄",

      // Strategy Switcher
      "strategy_switcher.title": "Strategy Switcher Dashboard",
      "strategy_switcher.header": "🔄 Automatic Strategy Switcher",
      "strategy_switcher.subtitle": "Real-time monitoring and performance analytics for automatic strategy switching",
      "strategy_switcher.current_status": "Current Status",
      "strategy_switcher.manual_evaluate": "Manual Evaluate",
      "strategy_switcher.loading": "Loading...",
      "strategy_switcher.cooldown_active": "Cooldown Active",
      "strategy_switcher.active": "Active",
      "strategy_switcher.active_strategy": "Active Strategy",
      "strategy_switcher.active_symbol": "Active Symbol",
      "strategy_switcher.last_switch": "Last Switch",
      "strategy_switcher.never": "Never",
      "strategy_switcher.performance_rankings": "📊 Strategy Performance Rankings",
      "strategy_switcher.refresh_rankings": "Refresh Rankings",
      "strategy_switcher.rank": "Rank",
      "strategy_switcher.strategy_symbol": "Strategy/Symbol",
      "strategy_switcher.composite_score": "Composite Score",
      "strategy_switcher.profitability": "Profitability",
      "strategy_switcher.risk_control": "Risk Control",
      "strategy_switcher.market_fit": "Market Fit",
      "strategy_switcher.no_rankings": "No strategy rankings available",
      "strategy_switcher.recent_switches": "⚡ Recent Strategy Switches",
      "strategy_switcher.refresh_switches": "Refresh Switches",
      "strategy_switcher.no_switches": "No strategy switches recorded yet.",
      "strategy_switcher.monitored_instruments": "🔍 Monitored Instruments & Strategies",
      "strategy_switcher.instruments": " Instruments",
      "strategy_switcher.strategies": "Strategies",
      "strategy_switcher.none": "None",
      "strategy_switcher.switch_from": "Switched from",
      "strategy_switcher.switch_to": "to",
      "strategy_switcher.initialized_with": "Initialized with",
      "strategy_switcher.manual_trigger_confirm": "Are you sure you want to manually trigger strategy evaluation?",
      "strategy_switcher.loading_strategy_rankings": "Loading strategy rankings...",
      "strategy_switcher.loading_recent_switches": "Loading recent switches...",
      "strategy_switcher.monitored_instruments_strategies": "🔍 Monitored Instruments & Strategies",
      "strategy_switcher.score": "Score:",
      "strategy_switcher.no_strategy_rankings": "No strategy rankings available",
      "strategy_switcher.switched_from": "Switched from",
      "strategy_switcher.switched_to": "to",
      "strategy_switcher.no_strategy_switches": "No strategy switches recorded yet.",
      "strategy_switcher.strategy_performance_rankings": "📊 Strategy Performance Rankings",
      "strategy_switcher.recent_strategy_switches": "⚡ Recent Strategy Switches",

      // Ramadan
      "ramadan.title": "Ramadan Trading Mode",
      "ramadan.page_title": "🌙 Ramadan Trading Mode - QuantumBotX",
      "ramadan.header": "🌙 Ramadan Trading Mode",
      "ramadan.subtitle": "Holy month with trading features that respect fasting worship",
      "ramadan.info": "This mode is automatically active during Ramadan and will adjust your trading settings to respect worship times. You don't need to activate it manually.",
      "ramadan.status": "Ramadan Status",
      "ramadan.period": "Ramadan Period",
      "ramadan.greeting": "Ramadan Greeting",
      "ramadan.iftar_countdown": "⏱️ Iftar Countdown",
      "ramadan.hours": "Hours",
      "ramadan.minutes": "Minutes",
      "ramadan.sampai": "Until",
      "ramadan.trading_adjustments": "⚙️ Trading Adjustments",
      "ramadan.rest_times": "Fasting Rest Times",
      "ramadan.sahur": "Sahur",
      "ramadan.iftar": "Iftar",
      "ramadan.tarawih": "Tarawih",
      "ramadan.risk_adjustments": "Risk Adjustments",
      "ramadan.reduced_risk": "Reduced Risk Mode",
      "ramadan.risk_reduction_detail": "20% risk reduction during fasting",
      "ramadan.patience_mode": "Patience Mode",
      "ramadan.patience_detail": "Focus on quality not quantity",
      "ramadan.optimal_hours": "Optimal Hours",
      "ramadan.zakat_calculator": "💰 Trading Zakat Calculator",
      "ramadan.zakat_info": "Zakat Information",
      "ramadan.nisab_gold": "Gold Nisab",
      "ramadan.nisab_silver": "Silver Nisab",
      "ramadan.zakat_percentage": "Zakat Percentage",
      "ramadan.zakat_reminder": "Zakat Reminder",
      "ramadan.zakat_reminder_text": "Trading zakat: 2.5% of trading profits during 1 hijri year. Don't forget to calculate zakat from your trading profits during Ramadan.",
      "ramadan.patience_reminder": "🧘‍♂️ Patience Reminder",
      "ramadan.patience_loading": "Loading...",
      "ramadan.active": "Active",
      "ramadan.inactive": "Inactive",
      "ramadan.not_ramadan": "Not Ramadan period",
      "ramadan.default_greeting": "Time to fast, time to trade with blessings",

      // Other
      "common.close": "Close",
      "common.yes": "Yes",
      "common.no": "No",
      
      // AI Mentor Settings
      "ai_mentor.settings_title": "⚙️ AI Mentor Settings - QuantumBotX"
    }
  },

  // Current language
  currentLang: localStorage.getItem('quantumBotX_language') || 'id',

  // Initialize i18n system
  init: function() {
    this.loadLanguage();
    this.createLanguageSwitcher();
    this.applyTranslations();
  },

  // Load saved language preference
  loadLanguage: function() {
    const saved = localStorage.getItem('quantumBotX_language');
    if (saved && this.translations[saved]) {
      this.currentLang = saved;
    }
  },

  // Create global language switcher (can be embedded anywhere)
  createLanguageSwitcher: function() {
    // Check if already exists
    if (document.getElementById('global-lang-switcher')) return;

    const switcher = document.createElement('div');
    switcher.id = 'global-lang-switcher';
    switcher.className = 'fixed top-4 right-4 z-50 flex items-center space-x-2 bg-white rounded-lg shadow-lg border p-1';

    switcher.innerHTML = `
      <button class="lang-btn px-3 py-1 rounded text-sm ${this.currentLang === 'id' ? 'bg-blue-500 text-white' : 'text-gray-600 hover:bg-gray-100'}"
              data-lang="id">ID</button>
      <button class="lang-btn px-3 py-1 rounded text-sm ${this.currentLang === 'en' ? 'bg-blue-500 text-white' : 'text-gray-600 hover:bg-gray-100'}"
              data-lang="en">EN</button>
    `;

    // Add event listeners
    switcher.querySelectorAll('.lang-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const newLang = btn.dataset.lang;
        this.setLanguage(newLang);
      });
    });

    // Insert into page (after body loads)
    document.addEventListener('DOMContentLoaded', () => {
      document.body.appendChild(switcher);
    });
  },

  // Set active language
  setLanguage: function(lang) {
    if (!this.translations[lang]) {
      console.warn(`Language '${lang}' not available`);
      return;
    }

    this.currentLang = lang;
    localStorage.setItem('quantumBotX_language', lang);

    // Update switcher buttons
    const switcher = document.getElementById('global-lang-switcher');
    if (switcher) {
      switcher.querySelectorAll('.lang-btn').forEach(btn => {
        const isActive = btn.dataset.lang === lang;
        btn.className = `lang-btn px-3 py-1 rounded text-sm ${isActive ? 'bg-blue-500 text-white' : 'text-gray-600 hover:bg-gray-100'}`;
      });
    }

    this.applyTranslations();
    this.onLanguageChange(lang);
  },

  // Get translated text
  t: function(key, fallback = null) {
    const translation = this.translations[this.currentLang]?.[key];
    if (translation) return translation;

    // Fallback to English if available
    if (this.currentLang !== 'en' && this.translations.en?.[key]) {
      return this.translations.en[key];
    }

    // Use fallback or return key
    return fallback || key;
  },

  // Apply translations to all elements with data-i18n attribute
  applyTranslations: function() {
    // Elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(element => {
      const key = element.getAttribute('data-i18n');
      const translation = this.t(key);

      // Different element types handle text differently
      if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
        if (element.type === 'submit' || element.type === 'button') {
          element.value = translation;
        } else if (element.placeholder) {
          element.placeholder = translation;
        } else {
          element.textContent = translation;
        }
      } else if (element.tagName === 'OPTION') {
        element.textContent = translation;
      } else {
        element.textContent = translation;
      }
    });

    // Title attributes
    document.querySelectorAll('[data-i18n-title]').forEach(element => {
      const key = element.getAttribute('data-i18n-title');
      element.title = this.t(key);
    });

    // Placeholder attributes
    document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
      const key = element.getAttribute('data-i18n-placeholder');
      element.placeholder = this.t(key);
    });
  },

  // Callback when language changes
  onLanguageChange: function(newLang) {
    // Update page title if it contains translatable text
    const titleKey = document.documentElement.getAttribute('data-page-title');
    if (titleKey) {
      document.title = this.t(titleKey);
    }

    // Trigger custom event for pages to handle
    const event = new CustomEvent('languageChanged', { detail: { language: newLang } });
    document.dispatchEvent(event);

    // Show feedback
    this.showLanguageChangeFeedback(newLang);
  },

  // Show brief feedback when language changes
  showLanguageChangeFeedback: function(lang) {
    const langName = lang === 'id' ? 'Indonesia' : 'English';
    const feedback = document.createElement('div');
    feedback.className = 'fixed bottom-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50 transition-opacity';
    feedback.textContent = `Language: ${langName}`;

    document.body.appendChild(feedback);

    // Auto remove after 2 seconds
    setTimeout(() => {
      feedback.style.opacity = '0';
      setTimeout(() => feedback.remove(), 300);
    }, 2000);
  },

  // Add new translation key dynamically
  addTranslation: function(lang, key, value) {
    if (!this.translations[lang]) {
      this.translations[lang] = {};
    }
    this.translations[lang][key] = value;
  },

  // Get current language
  getCurrentLanguage: function() {
    return this.currentLang;
  },

  // Check if language is available
  isLanguageAvailable: function(lang) {
    return Boolean(this.translations[lang]);
  }
};

// Initialize when DOM loads
document.addEventListener('DOMContentLoaded', function() {
  window.QuantumBotXI18n.init();
});

// Export for module use (optional)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = window.QuantumBotXI18n;
}
