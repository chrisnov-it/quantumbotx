// static/js/backtest_history.js

document.addEventListener('DOMContentLoaded', () => {
    const historyListContainer = document.getElementById('history-list-container');
    
    const detailView = document.getElementById('detail-view');
    const detailPlaceholder = document.getElementById('detail-placeholder');
    const detailId = document.getElementById('detail-id');
    const detailTimestamp = document.getElementById('detail-timestamp');
    const detailSummary = document.getElementById('detail-summary');
    const detailParams = document.getElementById('detail-params');
    const detailLog = document.getElementById('detail-log');

    let equityChart = null;

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

    async function loadHistoryList() {
        try {
            console.log('Memulai proses load history list...');
            const response = await fetch('/api/backtest/history');
            if (!response.ok) {
                throw new Error(`Gagal memuat riwayat backtest. Status: ${response.status}`);
            }
            const history = await response.json();
            console.log('Data history diterima:', history);

            historyListContainer.innerHTML = '';

            if (history.length === 0) {
                historyListContainer.innerHTML = '<p class="text-gray-500 text-center py-4">Tidak ada riwayat backtest.</p>';
                return;
            }

            // Pastikan data yang diperlukan ada sebelum di-sort
            history.forEach(item => {
                if (!item.timestamp) {
                    console.warn('Item tanpa timestamp ditemukan:', item);
                    return;
                }
            });

            // Urutkan berdasarkan timestamp terbaru
            history.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

            history.forEach(item => {
                const marketName = extractMarketName(item.data_filename);
                const itemElement = document.createElement('div');
                itemElement.className = 'p-3 mb-2 bg-gray-50 rounded cursor-pointer hover:bg-gray-100 border border-gray-200';
                
                // Ambil nilai profit dari kunci yang benar
                const totalProfit = item.total_profit_usd || 0;
                
                itemElement.innerHTML = `
                    <p class="font-medium text-gray-800">${item.strategy_name || 'Tidak Diketahui'} (${marketName})</p>
                    <p class="text-xs text-gray-500">${formatTimestamp(item.timestamp)}</p>
                    <p class="text-sm mt-1"><span class="font-semibold">Profit:</span> ${typeof totalProfit === 'number' ? totalProfit.toLocaleString('en-US', { style: 'currency', currency: 'USD' }) : '$0.00'}</p>
                `;
                
                itemElement.addEventListener('click', () => showDetail(item));
                historyListContainer.appendChild(itemElement);
            });

        } catch (error) {
            console.error('Error loading history list:', error);
            historyListContainer.innerHTML = `
                <p class="text-red-500 text-center py-4">Gagal memuat riwayat: ${error.message}</p>
                <p class="text-gray-500 text-center mt-2">Pastikan API backtest history berjalan dengan benar.</p>
            `;
        }
    }

    function showDetail(item) {
        try {
            console.log('Menampilkan detail backtest:', item);
            
            // Sembunyikan placeholder, tampilkan detail view
            detailPlaceholder.classList.add('hidden');
            detailView.classList.remove('hidden');

            const marketName = extractMarketName(item.data_filename);
            
            // Pastikan nilai-nilai yang diperlukan ada
            const totalProfit = item.total_profit_usd || 0;
            const maxDrawdown = item.max_drawdown_percent || 0;
            const winRate = item.win_rate_percent || 0;
            const totalTrades = item.total_trades || 0;
            const wins = item.wins || 0;
            const losses = item.losses || 0;

            // Isi data dasar
            detailId.textContent = item.id || 'N/A';
            detailTimestamp.textContent = formatTimestamp(item.timestamp);

            // Isi ringkasan dengan enhanced engine data
            const spreadCosts = item.parameters?.spread_costs || 0;
            const engineType = item.parameters?.engine_type || 'legacy';
            const maxRisk = item.parameters?.max_risk_percent || 'N/A';
            const maxLot = item.parameters?.max_lot_size || 'N/A';
            const spreadPips = item.parameters?.typical_spread_pips || 'N/A';
            
            detailSummary.innerHTML = `
                <div class="p-3 bg-gray-50 rounded"><p class="text-xs text-gray-500">Strategi</p><p class="font-bold">${item.strategy_name || 'N/A'}</p></div>
                <div class="p-3 bg-gray-50 rounded"><p class="text-xs text-gray-500">Pasar</p><p class="font-bold">${marketName}</p></div>
                <div class="p-3 bg-gray-50 rounded"><p class="text-xs text-gray-500">Engine</p><p class="font-bold text-${engineType === 'enhanced' ? 'green' : 'yellow'}-600">${engineType === 'enhanced' ? '🚀 Enhanced' : '⚠️ Legacy'}</p></div>
                <div class="p-3 bg-gray-50 rounded"><p class="text-xs text-gray-500">Gross Profit</p><p class="font-bold">${totalProfit.toLocaleString('en-US', { style: 'currency', currency: 'USD' })}</p></div>
                <div class="p-3 bg-gray-50 rounded"><p class="text-xs text-gray-500">Spread Costs</p><p class="font-bold text-red-600">-${spreadCosts.toLocaleString('en-US', { style: 'currency', currency: 'USD' })}</p></div>
                <div class="p-3 bg-gray-50 rounded"><p class="text-xs text-gray-500">Net Profit</p><p class="font-bold ${totalProfit - spreadCosts >= 0 ? 'text-green-600' : 'text-red-600'}">${(totalProfit - spreadCosts).toLocaleString('en-US', { style: 'currency', currency: 'USD' })}</p></div>
                <div class="p-3 bg-gray-50 rounded"><p class="text-xs text-gray-500">Max Drawdown</p><p class="font-bold">${maxDrawdown}%</p></div>
                <div class="p-3 bg-gray-50 rounded"><p class="text-xs text-gray-500">Win Rate</p><p class="font-bold">${winRate}%</p></div>
                <div class="p-3 bg-gray-50 rounded"><p class="text-xs text-gray-500">Total Trades</p><p class="font-bold">${totalTrades}</p></div>
                <div class="p-3 bg-gray-50 rounded"><p class="text-xs text-gray-500">Wins</p><p class="font-bold">${wins}</p></div>
                <div class="p-3 bg-gray-50 rounded"><p class="text-xs text-gray-500">Losses</p><p class="font-bold">${losses}</p></div>
                <div class="p-3 bg-gray-50 rounded"><p class="text-xs text-gray-500">Max Risk</p><p class="font-bold">${maxRisk}%</p></div>
                <div class="p-3 bg-gray-50 rounded"><p class="text-xs text-gray-500">Max Lot</p><p class="font-bold">${maxLot}</p></div>
            `;

            // Tampilkan equity chart
            displayEquityChart(item.equity_curve);

            // Tampilkan parameter
            displayParameters(item.parameters);

            // Tampilkan log trade
            displayTradeLog(item.trade_log);

        } catch (error) {
            console.error('Error showing detail:', error);
            detailView.innerHTML = '<p class="text-red-500 text-center py-4">Error menampilkan detail: ' + error.message + '</p>';
        }
    }

    function displayEquityChart(equityData) {
        try {
            // Destroy existing chart
            if (equityChart) {
                equityChart.destroy();
                equityChart = null;
            }

            const canvas = document.getElementById('detail-equity-chart');
            if (!canvas) {
                console.error('Canvas element not found');
                return;
            }

            let parsedEquityData = [];
            
            if (typeof equityData === 'string') {
                try {
                    parsedEquityData = JSON.parse(equityData);
                } catch (e) {
                    console.error('Error parsing equity data:', e);
                    return;
                }
            } else if (Array.isArray(equityData)) {
                parsedEquityData = equityData;
            } else {
                console.error('Invalid equity data format');
                return;
            }

            if (!parsedEquityData || parsedEquityData.length === 0) {
                canvas.parentElement.innerHTML = '<p class="text-gray-500 text-center py-4">Tidak ada data equity curve.</p>';
                return;
            }

            const ctx = canvas.getContext('2d');
            equityChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: Array.from({ length: parsedEquityData.length }, (_, i) => i + 1),
                    datasets: [{
                        label: 'Equity Curve',
                        data: parsedEquityData,
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
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        title: { display: true, text: 'Pertumbuhan Modal (Equity Curve)' }
                    },
                    scales: {
                        y: { beginAtZero: false }
                    }
                }
            });
        } catch (error) {
            console.error('Error displaying equity chart:', error);
        }
    }

    function displayParameters(parameters) {
        try {
            let parsedParams = {};
            
            if (typeof parameters === 'string') {
                try {
                    parsedParams = JSON.parse(parameters);
                } catch (e) {
                    console.error('Error parsing parameters:', e);
                    parsedParams = {};
                }
            } else if (typeof parameters === 'object' && parameters !== null) {
                parsedParams = parameters;
            }

            if (Object.keys(parsedParams).length === 0) {
                detailParams.innerHTML = '<h4 class="text-lg font-semibold mt-6 mb-2">Parameter</h4><p class="text-gray-500">Tidak ada parameter yang disimpan.</p>';
                return;
            }

            let paramsHtml = '<h4 class="text-lg font-semibold mt-6 mb-2">Parameter</h4>';
            paramsHtml += '<div class="grid grid-cols-2 md:grid-cols-3 gap-3">';
            
            for (const [key, value] of Object.entries(parsedParams)) {
                paramsHtml += `
                    <div class="p-2 bg-gray-50 rounded">
                        <p class="text-xs text-gray-500">${key}</p>
                        <p class="font-medium">${value}</p>
                    </div>
                `;
            }
            
            paramsHtml += '</div>';
            detailParams.innerHTML = paramsHtml;
        } catch (error) {
            console.error('Error displaying parameters:', error);
            detailParams.innerHTML = '<h4 class="text-lg font-semibold mt-6 mb-2">Parameter</h4><p class="text-red-500">Error menampilkan parameter.</p>';
        }
    }

    function displayTradeLog(tradeLog) {
        try {
            let parsedTrades = [];
            
            if (typeof tradeLog === 'string') {
                try {
                    parsedTrades = JSON.parse(tradeLog);
                } catch (e) {
                    console.error('Error parsing trade log:', e);
                    parsedTrades = [];
                }
            } else if (Array.isArray(tradeLog)) {
                parsedTrades = tradeLog;
            }

            if (!parsedTrades || parsedTrades.length === 0) {
                detailLog.innerHTML = '<h4 class="text-lg font-semibold mt-6 mb-2">Trade Log</h4><p class="text-gray-500">Tidak ada trade yang tercatat.</p>';
                return;
            }

            let logHtml = '<h4 class="text-lg font-semibold mt-6 mb-2">Trade Log (Terakhir ' + Math.min(20, parsedTrades.length) + ' Trades)</h4>';
            logHtml += '<div class="text-xs font-mono border rounded p-2 bg-gray-50 max-h-64 overflow-y-auto">';
            
            // Show last 20 trades
            const trades = parsedTrades.slice(-20);
            
            trades.forEach(trade => {
                const profit = trade.profit || 0;
                const profitClass = profit > 0 ? 'text-green-600' : 'text-red-600';
                const entry = trade.entry || trade.entry_price || 0;
                const exit = trade.exit || trade.exit_price || 0;
                const reason = trade.reason || 'N/A';
                const positionType = trade.position_type || 'N/A';
                
                logHtml += `
                    <p class="mb-1">
                        <span class="font-bold">${positionType}</span> | 
                        Entry: ${parseFloat(entry).toFixed(4)} | 
                        Exit: ${parseFloat(exit).toFixed(4)} | 
                        Profit: <span class="${profitClass}">${parseFloat(profit).toFixed(2)}</span> | 
                        Reason: ${reason}
                    </p>
                `;
            });
            
            logHtml += '</div>';
            detailLog.innerHTML = logHtml;
        } catch (error) {
            console.error('Error displaying trade log:', error);
            detailLog.innerHTML = '<h4 class="text-lg font-semibold mt-6 mb-2">Trade Log</h4><p class="text-red-500">Error menampilkan trade log.</p>';
        }
    }

    // Inisialisasi
    loadHistoryList();
});
