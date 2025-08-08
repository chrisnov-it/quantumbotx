// static/js/history.js

document.addEventListener('DOMContentLoaded', function() {
    const historyTableBody = document.getElementById('history-table-body');

    const formatTimestamp = (timestampInSeconds) => {
        const date = new Date(timestampInSeconds * 1000);
        return date.toLocaleString('id-ID', {
            day: '2-digit', month: 'short', year: 'numeric',
            hour: '2-digit', minute: '2-digit'
        });
    };

    async function fetchGlobalHistory() {
        try {
            const response = await fetch('/api/history');
            if (!response.ok) throw new Error('Gagal memuat data riwayat');
            const history = await response.json();

            historyTableBody.innerHTML = ''; // Kosongkan pesan "Memuat..."

            if (history.length === 0) {
                historyTableBody.innerHTML = '<tr><td colspan="6" class="p-4 text-center text-gray-500">Tidak ada riwayat transaksi ditemukan.</td></tr>';
                return;
            }

            history.forEach(deal => {
                const profitClass = deal.profit >= 0 ? 'text-green-600' : 'text-red-600';
                const dealType = deal.type === 0 ? 'BUY' : 'SELL'; // 0: BUY, 1: SELL

                const row = `
                    <tr class="hover:bg-gray-50">
                        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${deal.symbol}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${dealType}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${deal.volume}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm font-semibold ${profitClass}">$${deal.profit.toFixed(2)}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${formatTimestamp(deal.time)}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${deal.magic}</td>
                    </tr>
                `;
                historyTableBody.innerHTML += row;
            });

        } catch (error) {
            console.error('Error fetching global history:', error);
            historyTableBody.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-red-500">Gagal memuat riwayat: ${error.message}</td></tr>`;
        }
    }

    fetchGlobalHistory();
});
