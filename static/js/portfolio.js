// static/js/portfolio.js

document.addEventListener('DOMContentLoaded', function() {
    // --- Elemen DOM & Variabel Global ---
    const portfolioTableBody = document.getElementById('portfolio-table-body');
    const portfolioSummary = document.getElementById('portfolio-summary');
    const pnlCanvas = document.getElementById('pnlChart');
    const assetCanvas = document.getElementById('assetAllocationChart');
    
    let pnlChart = null;
    let assetAllocationChart = null;
    let previousTotalProfit = 0;
    const MAX_CHART_POINTS = 60; // Tampilkan 60 data point terakhir

    // --- Fungsi Pembantu ---
    const formatCurrency = (value) => {
        const sign = value >= 0 ? '+' : '-';
        return `${sign}${Math.abs(value).toFixed(2)}`;
    };

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
            const positions = await response.json();
            
            let totalProfit = 0;
            portfolioTableBody.innerHTML = ''; // Kosongkan tabel sebelum diisi

            if (positions.length === 0) {
                portfolioTableBody.innerHTML = '<tr><td colspan="6" class="p-4 text-center text-gray-500">Tidak ada posisi terbuka.</td></tr>';
            } else {
                positions.forEach(pos => {
                    totalProfit += pos.profit;
                    const profitClass = pos.profit >= 0 ? 'text-green-600' : 'text-red-600';
                    const typeClass = pos.type === 0 ? 'text-blue-600' : 'text-orange-600';
                    const dealType = pos.type === 0 ? 'BUY' : 'SELL';

                    const row = `
                        <tr class="hover:bg-gray-50">
                            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${pos.symbol}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm font-semibold ${typeClass}">${dealType}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${pos.volume}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${pos.price_open.toFixed(5)}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm font-semibold ${profitClass}">${formatCurrency(pos.profit)}</td>
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
                <p class="text-sm text-gray-500">Total P/L Terbuka</p>
                <p class="text-2xl font-bold ${totalProfitClass}">${formatCurrency(totalProfit)} <span class="ml-2 text-lg">${trendIcon}</span></p>`;
            previousTotalProfit = totalProfit;

            // Update Grafik P/L
            if (pnlChart) {
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
            portfolioTableBody.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-red-500">Gagal memuat data: ${error.message}</td></tr>`;
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