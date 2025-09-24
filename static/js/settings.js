document.addEventListener('DOMContentLoaded', function() {
    // Toggle sidebar
    const sidebarToggle = document.getElementById('sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.getElementById('sidebar').classList.toggle('collapsed');
        });
    }

    // Language switching functionality
    const languageSelect = document.getElementById('language-select');
    const savePreferencesBtn = document.getElementById('save-preferences-btn');

    // Translation dictionary
    const translations = {
        id: {
            title: 'Pengaturan',
            profileTitle: 'Profil',
            fullNameLabel: 'Nama Lengkap',
            emailLabel: 'Alamat Email',
            saveProfileBtn: 'Simpan Perubahan',
            preferencesTitle: 'Preferensi',
            languageLabel: 'Bahasa',
            themeLabel: 'Tema',
            lightTheme: 'Terang',
            darkTheme: 'Gelap (Segera Hadir)',
            savePreferencesBtn: 'Simpan Preferensi',
            apiKeysTitle: 'API Keys Bursa',
            apiInfoText: 'API Keys akan digunakan oleh versi QuantumBotX berikutnya untuk mengakses broker non-MT5.',
            apiPlaceholderText: 'Fitur ini akan tersedia di QuantumBotX API versi mendatang.',
            quickSettingsTitle: 'Pengaturan Cepat',
            notificationsLabel: 'Notifikasi Email',
            autoUpdateLabel: 'Update Otomatis Strategi',
            demoModeLabel: 'Mode Demo'
        },
        en: {
            title: 'Settings',
            profileTitle: 'Profile',
            fullNameLabel: 'Full Name',
            emailLabel: 'Email Address',
            saveProfileBtn: 'Save Changes',
            preferencesTitle: 'Preferences',
            languageLabel: 'Language',
            themeLabel: 'Theme',
            lightTheme: 'Light',
            darkTheme: 'Dark (Coming Soon)',
            savePreferencesBtn: 'Save Preferences',
            apiKeysTitle: 'Broker API Keys',
            apiInfoText: 'API Keys will be used by the upcoming QuantumBotX API version to access non-MT5 brokers.',
            apiPlaceholderText: 'This feature will be available in the upcoming QuantumBotX API version.',
            quickSettingsTitle: 'Quick Settings',
            notificationsLabel: 'Email Notifications',
            autoUpdateLabel: 'Auto Strategy Updates',
            demoModeLabel: 'Demo Mode'
        }
    };

    // Get user language preference from localStorage, default to 'id'
    let currentLang = localStorage.getItem('quantumBotX_language') || 'id';

    // Set initial language
    setLanguage(currentLang);

    // Language change event
    if (languageSelect) {
        languageSelect.value = currentLang;
        languageSelect.addEventListener('change', function() {
            currentLang = this.value;
            setLanguage(currentLang);
        });
    }

    // Save preferences
    if (savePreferencesBtn) {
        savePreferencesBtn.addEventListener('click', function() {
            // Save language preference
            localStorage.setItem('quantumBotX_language', currentLang);

            // Save other preferences (theme, etc.)
            const theme = document.getElementById('theme-select').value;
            localStorage.setItem('quantumBotX_theme', theme);

            // Auto-update checkbox
            const autoUpdate = document.getElementById('auto-update').checked;
            localStorage.setItem('quantumBotX_autoUpdate', autoUpdate);

            // Notifications checkbox
            const notifications = document.getElementById('email-notifications').checked;
            localStorage.setItem('quantumBotX_notifications', notifications);

            // Demo mode checkbox
            const demoMode = document.getElementById('demo-mode').checked;
            localStorage.setItem('quantumBotX_demoMode', demoMode);

            // Show success message
            alert('Preferences saved successfully!');

            // If language changed, update the page title
            if (currentLang === 'en') {
                document.title = 'Settings - QuantumBotX';
            } else {
                document.title = 'Pengaturan - QuantumBotX';
            }
        });
    }

    // Load saved preferences on page load
    loadPreferences();

    function setLanguage(lang) {
        const translation = translations[lang];
        if (!translation) return;

        // Update page title
        const titleElement = document.querySelector('h2');
        if (titleElement && titleElement.textContent.includes('Pengaturan')) {
            titleElement.textContent = translation.title;
        }

        // Update all translatable elements
        Object.keys(translation).forEach(key => {
            const element = document.getElementById(key);
            if (element) {
                element.textContent = translation[key];
            }
        });

        // Update theme options
        const themeSelect = document.getElementById('theme-select');
        if (themeSelect && themeSelect.options.length >= 2) {
            themeSelect.options[0].text = translation.lightTheme;
            themeSelect.options[1].text = translation.darkTheme;
        }
    }

    function loadPreferences() {
        // Load theme preference
        const savedTheme = localStorage.getItem('quantumBotX_theme') || 'light';
        const themeSelect = document.getElementById('theme-select');
        if (themeSelect) themeSelect.value = savedTheme;

        // Load other checkbox preferences
        const autoUpdate = localStorage.getItem('quantumBotX_autoUpdate') === 'true';
        const autoUpdateCheckbox = document.getElementById('auto-update');
        if (autoUpdateCheckbox) autoUpdateCheckbox.checked = autoUpdate;

        const notifications = localStorage.getItem('quantumBotX_notifications') === 'true';
        const notificationsCheckbox = document.getElementById('email-notifications');
        if (notificationsCheckbox) notificationsCheckbox.checked = notifications;

        const demoMode = localStorage.getItem('quantumBotX_demoMode') !== 'false'; // Default true
        const demoModeCheckbox = document.getElementById('demo-mode');
        if (demoModeCheckbox) demoModeCheckbox.checked = demoMode;
    }

    // Profile save functionality (placeholder)
    const saveProfileBtn = document.getElementById('save-profile-btn');
    if (saveProfileBtn) {
        saveProfileBtn.addEventListener('click', function() {
            const fullName = document.getElementById('full-name-input').value;
            localStorage.setItem('quantumBotX_fullName', fullName);
            alert(currentLang === 'id' ? 'Profil berhasil disimpan!' : 'Profile saved successfully!');
        });
    }

    // Load saved profile data
    const savedName = localStorage.getItem('quantumBotX_fullName');
    if (savedName) {
        const nameInput = document.getElementById('full-name-input');
        if (nameInput) nameInput.value = savedName;
    }
});
