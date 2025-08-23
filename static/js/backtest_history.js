// static/js/backtest_history.js

document.addEventListener('DOMContentLoaded', () => {
    const historyListContainer = document.getElementById('history-list-container');
    
    const detailView = document.getElementById('detail-view');
    const detailPlaceholder = document.getElementById('detail-placeholder');
    const detailId = document.getElementById('detail-id');
    const detailTimestamp = document.getElementById('detail-timestamp');
    const detailSummary = document.getElementById('detail-summary');

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
                
                // Tambahkan error handling untuk nilai profit
                const totalProfit = item.total_profit || item.total_profit_pips || 0;
                
                itemElement.innerHTML = `
                    <p class="font-medium text-gray-800">${item.strategy_name || 'Tidak Diketahui'} (${marketName})</p>
                    <p class="text-xs text-gray-500">${formatTimestamp(item.timestamp)}</p>
                    <p class="text-sm mt-1"><span class="font-semibold">Profit:</span> ${typeof totalProfit === 'number' ? totalProfit.toLocaleString('id-ID', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '0.00'}</p>
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
            const totalProfit = item.total_profit || item.total_profit_pips || 0;
            const maxDrawdown = item.max_drawdown_percent || 0;
            const winRate = item.win_rate_percent || 0;
            const totalTrades = item.total_trades || 0;
            const wins = item.wins || 0;
            const losses = item.losses || 0;

            // Isi data dasar
            detailId.textContent = item.id || 'N/A';
            detailTimestamp.textContent = formatTimestamp(item.timestamp);

            // Isi ringkasan
            detailSummary.innerHTML = `
                <div class="p-3 bg-gray-50 rounded"><p class="text-xs text-gray-500">Strategi</p><p class="font-bold">${item.strategy_name || 'N/A'}</p></div>
                <div class="p-3 bg-gray-50 rounded"><p class="text-xs text-gray-500">Pasar</p><p class="font-bold">${marketName}</p></div>
                <div class="p-3 bg-gray-50 rounded"><p class="text-xs text-gray-500">Total Profit</p><p class="font-bold">Rp ${totalProfit.toLocaleString('id-ID', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} %</p></div>
                <div class="p-3 bg-gray-50 rounded"><p class="text-xs text-gray-500">Max Drawdown</p><p class="font-bold">${maxDrawdown}%</p></div>
                <div class="p-3 bg-gray-50 rounded"><p class="text-xs text-gray-500">Win Rate</p><p class="font-bold">${winRate}%</p></div>
                <div class="p-3 bg-gray-50 rounded"><p class="text-xs text-gray-500">Total Trades</p><p class="font-bold">${totalTrades}</p></div>
                <div class="p-3 bg-gray-50 rounded"><p class="text-xs text-gray-500">Wins</p><p class="font-bold">${wins}</p></div>
                <div class="p-3 bg-gray-50 rounded"><p class="text-xs text-gray-500">Losses</p><p class="font-bold">${losses}</p></div>
            `;
            // ... (isi parameter dan log seperti sebelumnya)
        } catch (error) {
            console.error('Error showing detail:', error);
            // Handle error display if needed
        }
    }

    // Tampilkan grafik kurva ekuitas (jika ada data)

    // Inisialisasi
    loadHistoryList();
});
