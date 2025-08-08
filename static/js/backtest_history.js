// static/js/backtest_history.js

document.addEventListener('DOMContentLoaded', () => {
    const historyListContainer = document.getElementById('history-list-container');
    const detailContainer = document.getElementById('detail-container');
    const detailView = document.getElementById('detail-view');
    const detailPlaceholder = document.getElementById('detail-placeholder');
    const detailId = document.getElementById('detail-id');
    const detailTimestamp = document.getElementById('detail-timestamp');
    const detailSummary = document.getElementById('detail-summary');
    const detailParams = document.getElementById('detail-params');
    const detailLog = document.getElementById('detail-log');
    let detailEquityChart = null; // Variabel untuk menyimpan instance grafik detail

    // Format timestamp dari ISO string ke format lokal
    const formatTimestamp = (isoString) => {
        return new Date(isoString).toLocaleString('id-ID', {
            day: '2-digit', month: 'short', year: 'numeric',
            hour: '2-digit', minute: '2-digit'
        });
    };

    // Fungsi untuk mengekstrak nama pasar dari nama file
    const extractMarketName = (filename) => {
        if (!filename) return 'N/A';
        const parts = filename.split('_');
        if (parts.length > 0) {
            return parts[0].toUpperCase();
        }
        return 'N/A';
    };

    // Muat daftar riwayat backtest
    async function loadHistoryList() {
        try {
            const response = await fetch('/api/backtest/history');
            if (!response.ok) throw new Error('Gagal memuat riwayat backtest.');
            const history = await response.json();

            historyListContainer.innerHTML = '';

            if (history.length === 0) {
                historyListContainer.innerHTML = '<p class="text-gray-500 text-center py-4">Tidak ada riwayat backtest.</p>';
                return;
            }

            // Urutkan berdasarkan timestamp terbaru
            history.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

            history.forEach(item => {
                const marketName = extractMarketName(item.data_filename);
                const itemElement = document.createElement('div');
                itemElement.className = 'p-3 mb-2 bg-gray-50 rounded cursor-pointer hover:bg-gray-100 border border-gray-200';
                itemElement.innerHTML = `
                    <p class="font-medium text-gray-800">${item.strategy_name || 'Tidak Diketahui'} (${marketName})</p>
                    <p class="text-xs text-gray-500">${formatTimestamp(item.timestamp)}</p>
                    <p class="text-sm mt-1"><span class="font-semibold">Profit:</span> ${parseFloat(item.total_profit_pips).toFixed(2)} pips</p>
                `;
                itemElement.addEventListener('click', () => showDetail(item));
                historyListContainer.appendChild(itemElement);
            });

        } catch (error) {
            console.error('Error loading history list:', error);
            historyListContainer.innerHTML = '<p class="text-red-500 text-center py-4">Gagal memuat riwayat: ' + error.message + '</p>';
        }
    }

    // Tampilkan detail backtest
    function showDetail(item) {
        // Sembunyikan placeholder, tampilkan detail view
        detailPlaceholder.classList.add('hidden');
        detailView.classList.remove('hidden');

        const marketName = extractMarketName(item.data_filename);

        // Isi data dasar
        detailId.textContent = item.id;
        detailTimestamp.textContent = formatTimestamp(item.timestamp);

        // Isi ringkasan
        detailSummary.innerHTML = `
            <div class="p-3 bg-gray-50 rounded"><p class="text-xs text-gray-500">Strategi</p><p class="font-bold">${item.strategy_name || 'N/A'}</p></div>
            <div class="p-3 bg-gray-50 rounded"><p class="text-xs text-gray-500">Pasar</p><p class="font-bold">${marketName}</p></div>
            <div class="p-3 bg-gray-50 rounded"><p class="text-xs text-gray-500">Total Profit</p><p class="font-bold">${parseFloat(item.total_profit_pips).toFixed(2)} pips</p></div>
            <div class="p-3 bg-gray-50 rounded"><p class="text-xs text-gray-500">Max Drawdown</p><p class="font-bold">${parseFloat(item.max_drawdown_percent).toFixed(2)}%</p></div>
            <div class="p-3 bg-gray-50 rounded"><p class="text-xs text-gray-500">Win Rate</p><p class="font-bold">${parseFloat(item.win_rate_percent).toFixed(2)}%</p></div>
            <div class="p-3 bg-gray-50 rounded"><p class="text-xs text-gray-500">Total Trades</p><p class="font-bold">${item.total_trades}</p></div>
            <div class="p-3 bg-gray-50 rounded"><p class="text-xs text-gray-500">Wins</p><p class="font-bold">${item.wins}</p></div>
            <div class="p-3 bg-gray-50 rounded"><p class="text-xs text-gray-500">Losses</p><p class="font-bold">${item.losses}</p></div>
        `;

        // Isi parameter (jika ada)
        try {
            const params = JSON.parse(item.parameters || '{}');
            let paramsHtml = '<h4 class="font-semibold mb-2">Parameter</h4><ul class="list-disc pl-5 text-sm">';
            for (const [key, value] of Object.entries(params)) {
                paramsHtml += `<li><span class="font-medium">${key}:</span> ${value}</li>`;
            }
            paramsHtml += '</ul>';
            detailParams.innerHTML = paramsHtml;
        } catch (e) {
            detailParams.innerHTML = '<h4 class="font-semibold mb-2">Parameter</h4><p class="text-gray-500">Tidak ada parameter atau format tidak valid.</p>';
        }

        // Isi log (jika ada)
        try {
            const trades = JSON.parse(item.trade_log || '[]');
            if (Array.isArray(trades) && trades.length > 0) {
                let logHtml = '<h4 class="font-semibold mt-4 mb-2">Log Trade</h4><div class="text-xs font-mono border rounded p-3 bg-gray-50 max-h-40 overflow-y-auto">';
                trades.forEach(trade => {
                    const profitClass = trade.profit_pips > 0 ? 'text-green-600' : 'text-red-600';
                    logHtml += `<p>Entry: ${trade.entry.toFixed(4)} | Exit: ${trade.exit.toFixed(4)} | Profit: <span class="${profitClass}">${trade.profit_pips.toFixed(2)} pips</span> | Reason: ${trade.reason}</p>`;
                });
                logHtml += '</div>';
                detailLog.innerHTML = logHtml;
            } else {
                detailLog.innerHTML = '<h4 class="font-semibold mt-4 mb-2">Log Trade</h4><p class="text-gray-500">Tidak ada log trade untuk ditampilkan.</p>';
            }
        } catch (e) {
            console.error("Gagal memproses log trade:", e);
            detailLog.innerHTML = '<h4 class="font-semibold mt-4 mb-2">Log Trade</h4><p class="text-red-500">Gagal memuat log trade.</p>';
        }

        // Tampilkan grafik kurva ekuitas (jika ada data)
        try {
            const equityData = JSON.parse(item.equity_curve || '[]');
            if (Array.isArray(equityData) && equityData.length > 0) {
                displayDetailEquityChart(equityData);
            } else {
                // Jika tidak ada data, hancurkan chart yang mungkin ada sebelumnya
                if (detailEquityChart) {
                    detailEquityChart.destroy();
                    detailEquityChart = null;
                }
                // Opsional: Tampilkan pesan bahwa tidak ada data chart
                // const chartCtx = document.getElementById('detail-equity-chart').getContext('2d');
                // chartCtx.clearRect(0, 0, chartCtx.canvas.width, chartCtx.canvas.height);
                // Atau biarkan canvas kosong
            }
        } catch (e) {
            console.error("Gagal memproses data kurva ekuitas:", e);
            if (detailEquityChart) {
                detailEquityChart.destroy();
                detailEquityChart = null;
            }
        }
    }

    // Tampilkan grafik kurva ekuitas di detail view
    function displayDetailEquityChart(equityData) {
        const ctx = document.getElementById('detail-equity-chart').getContext('2d');
        if (detailEquityChart) {
            detailEquityChart.destroy(); // Hancurkan grafik lama
        }
        detailEquityChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: Array.from({ length: equityData.length }, (_, i) => i + 1),
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

    // Inisialisasi
    loadHistoryList();
});