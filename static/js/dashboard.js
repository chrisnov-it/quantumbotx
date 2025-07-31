// --- PUSAT KONTROL DASHBOARD ---

// Formatter untuk nilai USD
const formatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
});

// Update statistik MT5 di dashboard
async function updateDashboardStats() {
    try {
        const response = await fetch('/api/dashboard/stats');
        if (!response.ok) throw new Error('Gagal mengambil statistik dasbor');
        const stats = await response.json();

        document.getElementById('total-equity').textContent = formatter.format(stats.equity);
        document.getElementById('todays-profit').textContent = formatter.format(stats.todays_profit);
        document.getElementById('active-bots-count').textContent = stats.active_bots_count;
        document.getElementById('total-bots-count').textContent = stats.total_bots;

        // Warna profit/loss
        const profitEl = document.getElementById('todays-profit');
        if (profitEl) {
            profitEl.classList.remove('text-green-500', 'text-red-500');
            profitEl.classList.add(stats.todays_profit < 0 ? 'text-red-500' : 'text-green-500');
        }

    } catch (error) {
        console.error('[DashboardStats] Error:', error);
    }
}

// Tampilkan daftar bot aktif
async function fetchAllBots() {
    try {
        const response = await fetch('/api/bots');
        if (!response.ok) throw new Error('Gagal mengambil daftar bot');
        const bots = await response.json();

        const listEl = document.getElementById('active-bots-list');
        listEl.innerHTML = '';

        const activeBots = bots.filter(bot => bot.status === 'Aktif');

        if (activeBots.length === 0) {
            listEl.innerHTML = '<p class="p-4 text-gray-500">Tidak ada bot yang sedang aktif.</p>';
        } else {
            activeBots.forEach(bot => {
                const badge = bot.strategy === 'MERCY_EDGE'
                    ? `<span class="ml-2 px-2 py-0.5 text-xs bg-purple-100 text-purple-800 rounded-full">AI</span>`
                    : '';

                const html = `
                    <div class="p-4 hover:bg-gray-50 transition">
                        <div class="flex items-center justify-between">
                            <div class="flex items-center">
                                <div class="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center text-green-600">
                                    <i class="fas fa-robot"></i>
                                </div>
                                <div class="ml-3">
                                    <p class="font-medium text-gray-800">
                                        ${bot.name} ${badge}
                                    </p>
                                    <p class="text-xs text-gray-500">${bot.market}</p>
                                </div>
                            </div>
                            <div class="text-right">
                                <p class="text-xs text-gray-500">
                                    Running <span class="inline-block w-2 h-2 rounded-full bg-green-500 ml-1"></span>
                                </p>
                            </div>
                        </div>
                    </div>
                `;
                listEl.innerHTML += html;
            });
        }

    } catch (error) {
        console.error('[FetchBots] Error:', error);
    }
}

// Grafik harga
let priceChart;
async function updatePriceChart(symbol = 'EURUSD') {
    try {
        const response = await fetch(`/api/chart/data?symbol=${symbol}`);
        const chartData = await response.json();

        const ctx = document.getElementById('priceChart');
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

    } catch (error) {
        console.error('[Chart] Gagal update grafik:', error);
    }
}

// Grafik RSI
let rsiChart;
async function updateRsiChart(symbol = 'EURUSD') {
    try {
        const response = await fetch(`/api/rsi_data?symbol=${symbol}&timeframe=H1`);
        const rsiData = await response.json();

        const ctx = document.getElementById('rsiChart');
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

    } catch (error) {
        console.error('[AI] Gagal memuat sinyal AI:', error);
        if (aiSignalSymbolEl) aiSignalSymbolEl.textContent = 'Error';
        if (aiSignalDecisionEl) aiSignalDecisionEl.textContent = 'Error';
        if (aiSignalExplanationEl) aiSignalExplanationEl.textContent = 'Error loading AI signal.';
        if (strategyNameEl) strategyNameEl.textContent = 'Error';
    }
}

// DOM ready
document.addEventListener('DOMContentLoaded', () => {
    // --- Elemen Global AI Signal ---
    const aiSignalSymbolEl = document.getElementById('ai-signal-symbol');
    const aiSignalDecisionEl = document.getElementById('ai-signal-decision');
    const aiSignalExplanationEl = document.getElementById('ai-signal-explanation');
    const refreshAiSignalButton = document.getElementById('refresh-ai-signal-button');

    updateDashboardStats();
    fetchAllBots();
    updatePriceChart();
    updateRsiChart();

    // Event listener untuk tombol refresh AI Signal
    let isAiSignalLoading = false;
    if (refreshAiSignalButton) {
        refreshAiSignalButton.addEventListener('click', async () => {
            if (isAiSignalLoading) return;
            isAiSignalLoading = true;
            refreshAiSignalButton.disabled = true;
            refreshAiSignalButton.textContent = 'Refreshing...';

            await fetchAiSignal();

            isAiSignalLoading = false;
            refreshAiSignalButton.disabled = false;
            refreshAiSignalButton.textContent = 'Refresh AI Signal';
        });
    }

    // Interval refresh
    setInterval(updateDashboardStats, 10000);
    setInterval(fetchAllBots, 5000);
});
