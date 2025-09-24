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
      "nav.settings": "Pengaturan",
      "nav.logout": "Keluar",

      // Dashboard
      "dashboard.title": "Dasbor QuantumBotX",
      "dashboard.welcome": "Selamat Datang",
      "dashboard.total_bots": "Total Bot",
      "dashboard.active_bots": "Bot Aktif",
      "dashboard.inactive_bots": "Bot Tidak Aktif",
      "dashboard.total_profit": "Total Profit",
      "dashboard.today_pnl": "PnL Hari Ini",
      "dashboard.create_bot": "Buat Bot Baru",
      "dashboard.view_details": "Lihat Detail",

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

      // Form Labels & Messages
      "label.name": "Nama",
      "label.market": "Pasar",
      "label.strategy": "Strategi",
      "label.status": "Status",
      "label.profit": "Profit",
      "label.trades": "Jumlah Trade",
      "label.win_rate": "Win Rate",

      "msg.loading": "Memuat...",
      "msg.no_data": "Tidak ada data",
      "msg.success": "Berhasil",
      "msg.error": "Error",
      "msg.confirm": "Apakah Anda yakin?",

      // Time & Date
      "time.today": "Hari Ini",
      "time.yesterday": "Kemarin",
      "time.week": "Minggu Ini",
      "time.month": "Bulan Ini",

      // Error Messages
      "error.connection": "Gagal terhubung ke server",
      "error.loading": "Gagal memuat data",
      "error.save": "Gagal menyimpan perubahan",

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
      "settings.save": "Simpan Perubahan"

    },
    en: {
      // Navigation & Common
      "nav.dashboard": "Dashboard",
      "nav.bots": "Trading Bots",
      "nav.backtest": "Backtester",
      "nav.history": "History",
      "nav.settings": "Settings",
      "nav.logout": "Logout",

      // Dashboard
      "dashboard.title": "QuantumBotX Dashboard",
      "dashboard.welcome": "Welcome",
      "dashboard.total_bots": "Total Bots",
      "dashboard.active_bots": "Active Bots",
      "dashboard.inactive_bots": "Inactive Bots",
      "dashboard.total_profit": "Total Profit",
      "dashboard.today_pnl": "Today's P&L",
      "dashboard.create_bot": "Create New Bot",
      "dashboard.view_details": "View Details",

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

      // Form Labels & Messages
      "label.name": "Name",
      "label.market": "Market",
      "label.strategy": "Strategy",
      "label.status": "Status",
      "label.profit": "Profit",
      "label.trades": "Trades",
      "label.win_rate": "Win Rate",

      "msg.loading": "Loading...",
      "msg.no_data": "No data available",
      "msg.success": "Success",
      "msg.error": "Error",
      "msg.confirm": "Are you sure?",

      // Time & Date
      "time.today": "Today",
      "time.yesterday": "Yesterday",
      "time.week": "This Week",
      "time.month": "This Month",

      // Error Messages
      "error.connection": "Failed to connect to server",
      "error.loading": "Failed to load data",
      "error.save": "Failed to save changes",

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
      "settings.save": "Save Changes"
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
      if (element.tagName === 'INPUT') {
        if (element.type === 'placeholder') {
          element.placeholder = translation;
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
