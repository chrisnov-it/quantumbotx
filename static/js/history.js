// static/js/history.js

document.addEventListener('DOMContentLoaded', function() {
    const historyTableBody = document.getElementById('history-table-body');
    let historyData = [];
    let currentSort = { column: null, direction: 'asc' };

    const formatTimestamp = (timestampInSeconds) => {
        const date = new Date(timestampInSeconds * 1000);
        return date.toLocaleString('id-ID', {
            day: '2-digit', month: 'short', year: 'numeric',
            hour: '2-digit', minute: '2-digit'
        });
    };

    const renderTable = (data) => {
        historyTableBody.innerHTML = '';

        if (data.length === 0) {
            historyTableBody.innerHTML = '<tr><td colspan="6" class="p-4 text-center text-gray-500">Tidak ada riwayat transaksi ditemukan.</td></tr>';
            return;
        }

        data.forEach(deal => {
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
    };

    const sortTable = (column) => {
        if (currentSort.column === column) {
            currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
        } else {
            currentSort.column = column;
            currentSort.direction = 'asc';
        }

        // Update sort icons
        document.getElementById('profit-sort-icon').innerHTML = column === 'profit' ? (currentSort.direction === 'asc' ? '▲' : '▼') : '';
        document.getElementById('time-sort-icon').innerHTML = column === 'time' ? (currentSort.direction === 'asc' ? '▲' : '▼') : '';

        const sortedData = [...historyData].sort((a, b) => {
            let aValue = a[column];
            let bValue = b[column];

            if (column === 'profit' || column === 'time') {
                aValue = parseFloat(aValue);
                bValue = parseFloat(bValue);
            } else if (column === 'volume' || column === 'magic') {
                aValue = parseFloat(aValue);
                bValue = parseFloat(bValue);
            }

            if (aValue < bValue) return currentSort.direction === 'asc' ? -1 : 1;
            if (aValue > bValue) return currentSort.direction === 'asc' ? 1 : -1;
            return 0;
        });

        renderTable(sortedData);
    };

    window.sortTable = sortTable;

    async function fetchGlobalHistory() {
        try {
            const response = await fetch('/api/history');
            if (!response.ok) throw new Error('Gagal memuat data riwayat');
            historyData = await response.json();
            renderTable(historyData);
        } catch (error) {
            console.error('Error fetching global history:', error);
            historyTableBody.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-red-500">Gagal memuat riwayat: ${error.message}</td></tr>`;
        }
    }

    fetchGlobalHistory();
});
