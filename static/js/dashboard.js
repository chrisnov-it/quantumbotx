// --- ENHANCED DASHBOARD WITH AI MENTOR INTEGRATION ---

// Formatter untuk nilai USD
const formatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
});

// Global chart variables
let priceChart, rsiChart;

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Check if Chart.js is loaded before initializing charts
    if (typeof Chart !== 'undefined') {
        initializeCharts();
    }
    
    // Load all dashboard data
    loadDashboardData();
    loadAIMentorSummary();
    loadRecentActivities();
    
    // Legacy compatibility - call existing functions if charts exist
    const priceChartEl = document.getElementById('priceChart');
    const rsiChartEl = document.getElementById('rsiChart');
    
    if (priceChartEl && typeof Chart !== 'undefined') {
        updatePriceChart();
    }
    if (rsiChartEl && typeof Chart !== 'undefined') {
        updateRsiChart();
    }
    
    // Auto-refresh every 30 seconds
    setInterval(() => {
        refreshDashboardData();
    }, 30000);
    
    // Legacy intervals for compatibility
    setInterval(updateDashboardStats, 10000);
    setInterval(fetchAllBots, 5000);
});

// Enhanced chart initialization
function initializeCharts() {
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js not loaded, skipping chart initialization');
        return;
    }
    
    // Initialize Price Chart
    const priceCtx = document.getElementById('priceChart');
    if (priceCtx && !priceChart) {
        priceChart = new Chart(priceCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'EUR/USD',
                    data: [],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: false, grid: { color: '#f3f4f6' } },
                    x: { grid: { color: '#f3f4f6' } }
                }
            }
        });
    }

    // Initialize RSI Chart
    const rsiCtx = document.getElementById('rsiChart');
    if (rsiCtx && !rsiChart) {
        rsiChart = new Chart(rsiCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'RSI',
                    data: [],
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    borderWidth: 2,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: {
                        min: 0,
                        max: 100,
                        grid: { color: '#f3f4f6' },
                        ticks: {
                            callback: function(value) {
                                if (value === 70) return '70 (Overbought)';
                                if (value === 30) return '30 (Oversold)';
                                return value;
                            }
                        }
                    },
                    x: { grid: { color: '#f3f4f6' } }
                }
            }
        });
    }
}

// Enhanced dashboard data loading
function loadDashboardData() {
    // Load account info
    loadAccountInfo();
    // Load bot status
    loadBotStatus();
    // Load chart data
    loadChartData();
}

function loadAccountInfo() {
    fetch('/api/account-info')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const equityEl = document.getElementById('total-equity');
                const profitEl = document.getElementById('todays-profit');
                
                if (equityEl) equityEl.textContent = formatter.format(data.equity);
                if (profitEl) {
                    profitEl.textContent = formatter.format(data.todays_profit);
                    profitEl.className = data.todays_profit >= 0 ? 
                        'mt-1 text-2xl font-semibold profit-positive' : 
                        'mt-1 text-2xl font-semibold profit-negative';
                }
            }
        })
        .catch(error => {
            console.error('Error loading account info:', error);
            const equityEl = document.getElementById('total-equity');
            const profitEl = document.getElementById('todays-profit');
            if (equityEl) equityEl.textContent = 'Error';
            if (profitEl) profitEl.textContent = 'Error';
        });
}

function loadBotStatus() {
    fetch('/api/bots/status')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const activeCountEl = document.getElementById('active-bots-count');
                const totalCountEl = document.getElementById('total-bots-count');
                
                if (activeCountEl) activeCountEl.textContent = data.active_count;
                if (totalCountEl) totalCountEl.textContent = data.total_count;
                
                // Update active bots list
                updateActiveBotsList(data.active_bots);
            }
        })
        .catch(error => {
            console.error('Error loading bot status:', error);
            const activeCountEl = document.getElementById('active-bots-count');
            const totalCountEl = document.getElementById('total-bots-count');
            if (activeCountEl) activeCountEl.textContent = 'Error';
            if (totalCountEl) totalCountEl.textContent = 'Error';
        });
}

function updateActiveBotsList(activeBots) {
    const botsList = document.getElementById('active-bots-list');
    if (!botsList) return;
    
    if (activeBots.length > 0) {
        botsList.innerHTML = activeBots.map(bot => `
            <div class="p-4 flex justify-between items-center hover:bg-gray-50 transition">
                <div>
                    <h4 class="font-medium text-gray-800">${bot.name}</h4>
                    <p class="text-sm text-gray-600">${bot.symbol} • ${bot.strategy}</p>
                </div>
                <div class="text-right">
                    <div class="text-sm font-medium ${bot.profit >= 0 ? 'profit-positive' : 'profit-negative'}">
                        ${formatter.format(bot.profit)}
                    </div>
                    <div class="text-xs text-gray-500">${bot.trades} trades</div>
                </div>
            </div>
        `).join('');
    } else {
        botsList.innerHTML = '<p class="p-4 text-gray-500">Tidak ada bot yang aktif</p>';
    }
}

function loadChartData() {
    fetch('/api/market-data/EURUSD')
        .then(response => response.json())
        .then(data => {
            if (data.success && priceChart && rsiChart) {
                // Update price chart
                priceChart.data.labels = data.timestamps;
                priceChart.data.datasets[0].data = data.prices;
                priceChart.update();
                
                // Update RSI chart
                rsiChart.data.labels = data.timestamps;
                rsiChart.data.datasets[0].data = data.rsi;
                rsiChart.update();
                
                // Update timestamp
                const timestampEl = document.getElementById('last-updated');
                if (timestampEl) {
                    timestampEl.innerHTML = `<i class="fas fa-clock"></i> ${new Date().toLocaleTimeString('id-ID')}`;
                }
            }
        })
        .catch(error => {
            console.error('Error loading chart data:', error);
            const timestampEl = document.getElementById('last-updated');
            if (timestampEl) {
                timestampEl.innerHTML = `<i class="fas fa-exclamation-triangle"></i> Error loading data`;
            }
        });
}

// AI Mentor Integration
function loadAIMentorSummary() {
    fetch('/ai-mentor/api/dashboard-summary')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update emotion status
                const emotionMap = {
                    'tenang': '😌 Tenang',
                    'serakah': '🤑 Serakah',
                    'takut': '😰 Takut',
                    'frustasi': '😤 Frustasi',
                    'netral': '😐 Netral'
                };
                
                const emotionEl = document.getElementById('emotion-status');
                if (emotionEl) {
                    emotionEl.textContent = emotionMap[data.today_emotions] || '😐 Netral';
                }
                
                // Update AI analysis
                const analysisEl = document.getElementById('trading-analysis');
                if (analysisEl) {
                    analysisEl.textContent = data.trading_analysis || 'Belum ada data hari ini';
                }
                
                // Update daily tip
                const tipEl = document.getElementById('daily-tip');
                if (tipEl) {
                    tipEl.textContent = data.daily_tip || 'Mulai trading untuk mendapat tips personal!';
                }
                
                // Update AI mentor status
                const statusEl = document.getElementById('ai-mentor-status');
                if (statusEl) {
                    if (data.today_has_data) {
                        statusEl.textContent = 'Aktif Menganalisis';
                        statusEl.className = 'text-xl font-bold text-green-100';
                    } else {
                        statusEl.textContent = 'Siap Membantu';
                        statusEl.className = 'text-xl font-bold';
                    }
                }
            }
        })
        .catch(error => {
            console.error('Error loading AI mentor summary:', error);
        });
}

function loadRecentActivities() {
    fetch('/api/recent-activities')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const activitiesEl = document.getElementById('recent-activities');
                if (activitiesEl) {
                    const activitiesHtml = data.activities.map(activity => `
                        <div class="activity-item p-4 hover:bg-gray-50 transition-colors">
                            <div class="flex items-start space-x-3">
                                <div class="text-lg">${activity.icon}</div>
                                <div class="flex-1">
                                    <p class="text-sm font-medium text-gray-900">${activity.title}</p>
                                    <p class="text-xs text-gray-500">${activity.description}</p>
                                    <p class="text-xs text-gray-400 mt-1">${activity.time}</p>
                                </div>
                            </div>
                        </div>
                    `).join('');
                    
                    activitiesEl.innerHTML = activitiesHtml || '<div class="p-4 text-gray-500 text-center">Belum ada aktivitas</div>';
                }
            }
        })
        .catch(error => {
            console.error('Error loading recent activities:', error);
        });
}

// Legacy functions for compatibility
function updateDashboardStats() {
    loadAccountInfo();
}

function fetchAllBots() {
    loadBotStatus();
}

// Updated chart functions for legacy compatibility
function updatePriceChart(symbol = 'EURUSD') {
    if (typeof Chart === 'undefined') return;
    
    fetch(`/api/chart/data?symbol=${symbol}`)
        .then(response => response.json())
        .then(chartData => {
            const ctx = document.getElementById('priceChart');
            if (!ctx) return;
            
            const config = {
                type: 'line',
                data: {
                    labels: chartData.labels,
                    datasets: [{
                        label: symbol,
                        data: chartData.data,
                        borderColor: '#3B82F6',
                        backgroundColor: 'rgba(59, 130, 246, 0.05)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { beginAtZero: false },
                        x: { grid: { display: false } }
                    }
                }
            };

            if (priceChart) {
                priceChart.data.labels = chartData.labels;
                priceChart.data.datasets[0].data = chartData.data;
                priceChart.update();
            } else {
                priceChart = new Chart(ctx, config);
            }
        })
        .catch(error => {
            console.error('[Chart] Gagal update grafik:', error);
        });
}

function updateRsiChart(symbol = 'EURUSD') {
    if (typeof Chart === 'undefined') return;
    
    fetch(`/api/rsi_data?symbol=${symbol}&timeframe=H1`)
        .then(response => response.json())
        .then(rsiData => {
            const ctx = document.getElementById('rsiChart');
            if (!ctx) return;
            
            const config = {
                type: 'line',
                data: {
                    labels: rsiData.timestamps,
                    datasets: [{
                        label: 'RSI',
                        data: rsiData.rsi_values,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderWidth: 2,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: {
                            min: 0,
                            max: 100,
                            ticks: { stepSize: 10 },
                            grid: { color: 'rgba(0,0,0,0.05)' }
                        }
                    }
                }
            };

            if (rsiChart) {
                rsiChart.data.labels = rsiData.timestamps;
                rsiChart.data.datasets[0].data = rsiData.rsi_values;
                rsiChart.update();
            } else {
                rsiChart = new Chart(ctx, config);
            }
        })
        .catch(error => {
            console.error('[RSI Chart] Gagal update grafik RSI:', error);
        });
}

// Lighter refresh for auto-refresh
function refreshDashboardData() {
    loadAccountInfo();
}

// Quick emotion check functions (from template)
function quickEmotionCheck() {
    const emotions = ['tenang', 'serakah', 'takut', 'frustasi', 'netral'];
    const emotionNames = ['😌 Tenang', '🤑 Serakah', '😰 Takut', '😤 Frustasi', '😐 Netral'];
    
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center';
    modal.innerHTML = `
        <div class="bg-white rounded-lg p-6 max-w-sm w-full mx-4">
            <h3 class="text-lg font-semibold mb-4">🎯 Update Status Emosi</h3>
            <div class="space-y-2">
                ${emotions.map((emotion, index) => `
                    <button onclick="updateEmotion('${emotion}')" 
                            class="w-full text-left p-3 rounded-lg border hover:bg-gray-50 transition-colors">
                        ${emotionNames[index]}
                    </button>
                `).join('')}
            </div>
            <button onclick="closeEmotionModal()" 
                    class="mt-4 w-full bg-gray-200 text-gray-800 py-2 rounded-lg hover:bg-gray-300 transition-colors">
                Batal
            </button>
        </div>
    `;
    
    document.body.appendChild(modal);
    window.currentEmotionModal = modal;
}

function updateEmotion(emotion) {
    fetch('/ai-mentor/update-emotions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ emotions: emotion })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const emotionMap = {
                'tenang': '😌 Tenang',
                'serakah': '🤑 Serakah', 
                'takut': '😰 Takut',
                'frustasi': '😤 Frustasi',
                'netral': '😐 Netral'
            };
            
            const emotionEl = document.getElementById('emotion-status');
            if (emotionEl) {
                emotionEl.textContent = emotionMap[emotion];
            }
            
            showNotification('Status emosi berhasil diupdate!', 'success');
            loadAIMentorSummary();
        } else {
            showNotification('Gagal update status emosi', 'error');
        }
    })
    .catch(error => {
        console.error('Error updating emotion:', error);
        showNotification('Error: Gagal update status emosi', 'error');
    })
    .finally(() => {
        closeEmotionModal();
    });
}

function closeEmotionModal() {
    if (window.currentEmotionModal) {
        document.body.removeChild(window.currentEmotionModal);
        window.currentEmotionModal = null;
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transition-all duration-300 ${
        type === 'success' ? 'bg-green-500 text-white' : 
        type === 'error' ? 'bg-red-500 text-white' : 
        'bg-blue-500 text-white'
    }`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 3000);
}
