// static/js/portfolio.js

document.addEventListener('DOMContentLoaded', function() {
    // --- Elemen DOM & Variabel Global ---
    const portfolioTableBody = document.getElementById('portfolio-table-body');
    const portfolioSummary = document.getElementById('portfolio-summary');
    const pnlCanvas = document.getElementById('pnlChart');
    const assetCanvas = document.getElementById('assetAllocationChart');
    const descriptionEl = document.querySelector('[data-i18n="portfolio.description"]');
    
    let pnlChart = null;
    let assetAllocationChart = null;
    let previousTotalProfit = 0;
    let currentBrokerType = 'MT5';
    const MAX_CHART_POINTS = 60; // Tampilkan 60 data point terakhir

    // --- Fungsi Pembantu ---
    const formatCurrency = (value) => {
        const sign = value >= 0 ? '+' : '-';
        return `${sign}${Math.abs(value).toFixed(2)}`;
    };

    const formatAdaptive = (value) => {
        const abs = Math.abs(Number(value || 0));
        if (abs > 0 && abs < 1e-8) return Number(value).toExponential(2);
        if (abs >= 1000) return Number(value).toFixed(2);
        if (abs >= 1) return Number(value).toFixed(4);
        if (abs >= 0.001) return Number(value).toFixed(6);
        return Number(value).toFixed(8);
    };

    function updatePortfolioSourceLabel(brokerType) {
        currentBrokerType = brokerType || currentBrokerType;
        if (!descriptionEl) return;
        const sourceLabel = currentBrokerType === 'CCXT' ? 'Binance (CCXT)' : 'MetaTrader 5';
        descriptionEl.textContent = `Posisi trading yang sedang terbuka di akun ${sourceLabel}.`;
    }

    // --- Inisialisasi Chart ---
    function initPnlChart() {
        if (!pnlCanvas) return;
        pnlChart = new Chart(pnlCanvas, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Total P/L ($)',
                    data: [],
                    borderColor: 'rgba(59, 130, 246, 1)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true, tension: 0.4, pointRadius: 0
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                scales: { x: { type: 'time', time: { unit: 'second', displayFormats: { second: 'HH:mm:ss' } } } },
                plugins: { legend: { display: false }, tooltip: { mode: 'index', intersect: false } }
            }
        });
    }

    async function updateAssetAllocationChart() {
        if (!assetCanvas) return;
        try {
            const response = await fetch('/api/portfolio/allocation');
            if (!response.ok) throw new Error('Gagal mengambil data alokasi');
            const data = await response.json();
            updatePortfolioSourceLabel(data.broker_type);

            if (assetAllocationChart) {
                assetAllocationChart.data.labels = data.labels;
                assetAllocationChart.data.datasets[0].data = data.values;
                assetAllocationChart.update();
            } else {
                assetAllocationChart = new Chart(assetCanvas, {
                    type: 'doughnut',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: 'Alokasi Aset',
                            data: data.values,
                            backgroundColor: ['#36A2EB', '#FFCD56', '#4BC0C0', '#FF6384', '#9966FF', '#FF9F40'],
                            hoverOffset: 4
                        }]
                    },
                    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'top' } } }
                });
            }
        } catch (error) {
            console.error("Gagal mengupdate chart alokasi:", error);
            // Opsi: Tampilkan pesan error di canvas
        }
    }

    // --- Fungsi Utama Pembaruan Data ---
    async function updatePortfolioData() {
        try {
            const response = await fetch('/api/portfolio/open-positions');
            if (!response.ok) throw new Error('Gagal memuat posisi terbuka');
            const payload = await response.json();
            if (!payload.success) throw new Error(payload.error || 'Gagal memuat posisi terbuka');
            const positions = payload.positions || [];
            updatePortfolioSourceLabel(payload.broker_type);
            
            let totalProfit = 0;
            portfolioTableBody.innerHTML = ''; // Kosongkan tabel sebelum diisi

            if (positions.length === 0) {
                portfolioTableBody.innerHTML = `<tr><td colspan="7" class="p-4 text-center text-gray-500">${window.QuantumBotXI18n.t('portfolio.no_open_positions')}</td></tr>`;
            } else {
                positions.forEach(pos => {
                    const pnlMain = Number(pos.profit_usdt ?? pos.profit ?? 0);
                    totalProfit += pnlMain;
                    const profitClass = pnlMain >= 0 ? 'text-green-600' : 'text-red-600';
                    const isBuy = pos.type === 0 || String(pos.type).toUpperCase() === 'BUY' || String(pos.type).toUpperCase() === 'SPOT';
                    const typeClass = isBuy ? 'text-blue-600' : 'text-orange-600';
                    const dealType = pos.type === 0 ? 'BUY' : (String(pos.type || 'N/A').toUpperCase());
                    const openPrice = Number(pos.price_open || 0);
                    const currentPrice = Number(pos.price_current || 0);
                    const openPriceDisplay = currentBrokerType === 'CCXT' ? formatAdaptive(openPrice) : openPrice.toFixed(5);
                    const currentPriceDisplay = currentBrokerType === 'CCXT' ? formatAdaptive(currentPrice) : currentPrice.toFixed(5);
                    const quoteAsset = String(pos.quote_asset || '').toUpperCase();
                    const quotePnl = Number(pos.profit_quote || 0);
                    const quotePnlDisplay = quoteAsset ? `${quotePnl >= 0 ? '+' : '-'}${formatAdaptive(Math.abs(quotePnl))} ${quoteAsset}` : '';
                    const mainPnlLabel = currentBrokerType === 'CCXT' ? `${pnlMain >= 0 ? '+' : '-'}${formatAdaptive(Math.abs(pnlMain))} USDT` : formatCurrency(pnlMain);
                    const secondaryPnl = (currentBrokerType === 'CCXT' && quotePnlDisplay)
                        ? `<div class="text-xs text-gray-500">${quotePnlDisplay}</div>`
                        : '';

                    const row = `
                        <tr class="hover:bg-gray-50">
                            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${pos.symbol}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm font-semibold ${typeClass}">${dealType}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${formatAdaptive(pos.volume)}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${openPriceDisplay}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${currentPriceDisplay}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm font-semibold ${profitClass}">${mainPnlLabel}${secondaryPnl}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${pos.magic}</td>
                        </tr>`;
                    portfolioTableBody.innerHTML += row;
                });
            }

            // Update Summary
            const totalProfitClass = totalProfit >= 0 ? 'text-green-600' : 'text-red-600';
            let trendIcon = '<i class="fas fa-minus text-gray-400"></i>';
            if (totalProfit > previousTotalProfit) trendIcon = '<i class="fas fa-arrow-up text-green-500"></i>';
            else if (totalProfit < previousTotalProfit) trendIcon = '<i class="fas fa-arrow-down text-red-500"></i>';

            portfolioSummary.innerHTML = `
                <p class="text-sm text-gray-500">${window.QuantumBotXI18n.t('portfolio.open_pnl_total')}</p>
                <p class="text-2xl font-bold ${totalProfitClass}">${currentBrokerType === 'CCXT' ? `${totalProfit >= 0 ? '+' : '-'}${formatAdaptive(Math.abs(totalProfit))} USDT` : formatCurrency(totalProfit)} <span class="ml-2 text-lg">${trendIcon}</span></p>
                <p class="text-xs text-gray-500 mt-1">Last Update: ${new Date().toLocaleTimeString('id-ID')}</p>`;
            previousTotalProfit = totalProfit;

            // Update Grafik P/L
            if (pnlChart) {
                pnlChart.data.datasets[0].label = currentBrokerType === 'CCXT' ? 'Total P/L (USDT)' : 'Total P/L ($)';
                const now = new Date();
                pnlChart.data.labels.push(now);
                pnlChart.data.datasets[0].data.push(totalProfit);
                if (pnlChart.data.labels.length > MAX_CHART_POINTS) {
                    pnlChart.data.labels.shift();
                    pnlChart.data.datasets[0].data.shift();
                }
                pnlChart.update('none');
            }

        } catch (error) {
            console.error("Gagal mengambil data portfolio:", error);
            portfolioTableBody.innerHTML = `<tr><td colspan="7" class="p-4 text-center text-red-500">Gagal memuat data: ${error.message}</td></tr>`;
        }
    }

    // --- Inisialisasi dan Eksekusi ---
    async function initializePage() {
        initPnlChart(); // Inisialisasi chart P/L kosong
        await updatePortfolioData(); // Panggil data portfolio pertama kali (termasuk update P/L)
        await updateAssetAllocationChart(); // Panggil data alokasi pertama kali
        
        // Set interval untuk pembaruan data
        setInterval(async () => {
            await updatePortfolioData();
            await updateAssetAllocationChart(); // Alokasi juga di-refresh
        }, 5000);
    }

    initializePage();
});
