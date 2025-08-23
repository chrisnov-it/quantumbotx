// static/js/backtesting.js
document.addEventListener('DOMContentLoaded', () => {
    const strategySelect = document.getElementById('strategy-select');
    const paramsContainer = document.getElementById('params-container');
    const form = document.getElementById('backtest-form');
    const runBtn = document.getElementById('run-backtest-btn');
    const resultsContainer = document.getElementById('results-container');
    const resultsSummary = document.getElementById('results-summary');
    const loadingSpinner = document.getElementById('loading-spinner');
    let equityChart = null; // Variabel untuk menyimpan instance grafik
    const resultsLog = document.getElementById('results-log');

    // Muat strategi ke dropdown
    async function loadStrategies() {
        try {
            const response = await fetch('/api/strategies');
            if (!response.ok) throw new Error('Gagal memuat strategi.');
            const strategies = await response.json();
            
            strategySelect.innerHTML = '<option value="" disabled selected>Pilih sebuah strategi</option>';
            strategies.forEach(strategy => {
                const option = document.createElement('option');
                option.value = strategy.id;
                option.textContent = strategy.name;
                strategySelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error loading strategies:', error);
            strategySelect.innerHTML = '<option value="">Gagal memuat strategi</option>';
        }
    }

    // Muat parameter saat strategi dipilih
    strategySelect.addEventListener('change', async () => {
        const strategyId = strategySelect.value;
        paramsContainer.innerHTML = '<p class="text-sm text-gray-500">Memuat parameter...</p>';
        if (!strategyId) {
            paramsContainer.innerHTML = '';
            return;
        }

        try {
            const res = await fetch(`/api/strategies/${strategyId}/params`);
            const params = await res.json();
            paramsContainer.innerHTML = ''; // Kosongkan lagi

            if (params.length > 0) {
                params.forEach(param => {
                    paramsContainer.innerHTML += `
                        <div>
                            <label for="${param.name}" class="block text-sm font-medium text-gray-700">${param.label}</label>
                            <input type="${param.type || 'number'}" name="${param.name}" id="${param.name}" value="${param.default}" step="${param.step || 'any'}" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
                        </div>`;
                });
            } else {
                paramsContainer.innerHTML = '<p class="text-sm text-gray-500">Strategi ini tidak memiliki parameter kustom.</p>';
            }
        } catch (err) {
            console.error('Gagal memuat parameter strategi:', err);
            paramsContainer.innerHTML = '<p class="text-sm text-red-500">Gagal memuat parameter.</p>';
        }
    });

    // Jalankan backtest saat form disubmit
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        loadingSpinner.classList.remove('hidden');
        resultsContainer.classList.add('hidden');
        runBtn.disabled = true;
        runBtn.textContent = 'Menjalankan...';

        const formData = new FormData(form);
        
        // Kumpulkan parameter kustom
        const params = {};
        // Ambil parameter dari form utama (SL/TP)
        params['sl_pips'] = parseFloat(document.getElementById('sl_atr_multiplier').value);
        params['tp_pips'] = parseFloat(document.getElementById('tp_atr_multiplier').value);

        // Kumpulkan parameter strategi kustom
        paramsContainer.querySelectorAll('input').forEach(input => {
            const value = parseFloat(input.value);
            // Pastikan hanya angka valid yang di-parse, selain itu ambil string
            params[input.name] = isNaN(value) ? input.value : value;
        });
        formData.append('params', JSON.stringify(params));

        try {
            const response = await fetch('/api/backtest/run', {
                method: 'POST',
                body: formData, // Kirim sebagai multipart/form-data
            });
            const results = await response.json();

            if (response.ok) {
                displayResults(results);
            } else {
                alert(`Error: ${results.error}`);
            }
        } catch (err) {
            console.error("Backtest failed:", err);
            alert('Gagal terhubung ke server.');
        } finally {
            loadingSpinner.classList.add('hidden');
            runBtn.disabled = false;
            runBtn.textContent = 'Jalankan Backtest';
        }
    });

    function displayResults(data) {
        resultsContainer.classList.remove('hidden');
        // PERBAIKAN: Tampilkan 6 metrik utama
        resultsSummary.innerHTML = `
                        <div class="p-4 bg-gray-50 rounded-lg"><p class="text-sm text-gray-500">Total Profit</p><p class="text-2xl font-bold text-green-600">${data.total_profit_usd.toFixed(2)} $</p></div>
            <div class="p-4 bg-gray-50 rounded-lg"><p class="text-sm text-gray-500">Max Drawdown</p><p class="text-2xl font-bold text-red-600">${data.max_drawdown_percent.toFixed(2)}%</p></div>
            <div class="p-4 bg-gray-50 rounded-lg"><p class="text-sm text-gray-500">Win Rate</p><p class="text-2xl font-bold text-blue-600">${data.win_rate_percent.toFixed(2)}%</p></div>
            <div class="p-4 bg-gray-50 rounded-lg"><p class="text-sm text-gray-500">Total Trades</p><p class="text-2xl font-bold">${data.total_trades}</p></div>
            <div class="p-4 bg-gray-50 rounded-lg"><p class="text-sm text-gray-500">Wins</p><p class="text-2xl font-bold">${data.wins}</p></div>
            <div class="p-4 bg-gray-50 rounded-lg"><p class="text-sm text-gray-500">Losses</p><p class="text-2xl font-bold">${data.losses}</p></div>
        `;

        // Tampilkan grafik kurva ekuitas
        displayEquityChart(data.equity_curve);

        // Tampilkan log trade (opsional)
        if (data.trades && data.trades.length > 0) {
            let logHtml = '<h4 class="text-lg font-semibold mt-6 mb-2">20 Trade Terakhir</h4><div class="text-xs font-mono border rounded p-2 bg-gray-50 max-h-64 overflow-y-auto">';
            data.trades.forEach(trade => {
                const profitClass = trade.profit > 0 ? 'text-green-600' : 'text-red-600';
                logHtml += `<p>Entry: ${trade.entry.toFixed(4)} | Exit: ${trade.exit.toFixed(4)} | Profit: <span class="${profitClass}">${trade.profit.toFixed(2)}</span> | Reason: ${trade.reason}</p>`;
            });
            logHtml += '</div>';
            resultsLog.innerHTML = logHtml;
        } else {
            resultsLog.innerHTML = '';
        }
    }

    function displayEquityChart(equityData) {
        const ctx = document.getElementById('equity-chart').getContext('2d');
        if (equityChart) {
            equityChart.destroy(); // Hancurkan grafik lama sebelum membuat yang baru
        }
        equityChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: Array.from({ length: equityData.length }, (_, i) => i + 1), // Label 1, 2, 3, ...
                datasets: [{
                    label: 'Equity Curve',
                    data: equityData,
                    borderColor: 'rgb(59, 130, 246)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.1,
                    pointRadius: 0,
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false },
                    title: { display: true, text: 'Pertumbuhan Modal (Equity Curve)' }
                },
                scales: { y: { beginAtZero: false } }
            }
        });
    }

    loadStrategies();
});
