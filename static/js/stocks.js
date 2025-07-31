
document.addEventListener('DOMContentLoaded', function() {
    fetchStockData();
});

function fetchStockData() {
    const tableBody = document.getElementById('stocks-table-body');

    fetch('/api/stocks')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(stocks => {
            if (!tableBody) {
                console.error('Element with ID "stocks-table-body" not found.');
                return;
            }

            if (!stocks || stocks.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="5" class="text-center">Tidak ada data saham yang tersedia atau gagal dimuat dari MT5.</td></tr>';
                return;
            }

            const rowsHtml = stocks.map(stock => {
                const changeClass = stock.change >= 0 ? 'text-green-600' : 'text-red-600';
                const changeIcon = stock.change >= 0 ? '▲' : '▼';

                return `
                    <tr>
                        <td class="px-6 py-4 whitespace-nowrap">
                            <div class="flex items-center">
                                <div class="font-medium text-gray-900">${stock.symbol}</div>
                            </div>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap font-medium">${stock.last_price.toFixed(2)}</td>
                        <td class="px-6 py-4 whitespace-nowrap font-medium ${changeClass}">${changeIcon} ${Math.abs(stock.change)}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${stock.time}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-right">
                            <button class="bg-blue-600 text-white py-1 px-3 rounded-md text-sm font-medium hover:bg-blue-700">Trade</button>
                            <button class="bg-gray-600 text-white py-1 px-3 rounded-md text-sm font-medium hover:bg-gray-700 details-btn" data-symbol="${stock.symbol}">Details</button>
                        </td>
                    </tr>
                `;
            }).join('');

            tableBody.innerHTML = rowsHtml;
        })
        .catch(error => {
            console.error('Error fetching stock data:', error);
            if (tableBody) {
                tableBody.innerHTML = '<tr><td colspan="5" class="p-4 text-center text-red-500">Gagal memuat data.</td></tr>';
            }
        });
}

document.addEventListener('click', function(e) {
    if (e.target.classList.contains('details-btn')) {
        const symbol = e.target.dataset.symbol;
        fetchCompanyProfile(symbol);
    }
});

document.getElementById('close-modal').addEventListener('click', function() {
    document.getElementById('stock-modal').classList.add('hidden');
});

async function fetchCompanyProfile(symbol) {
    const modal = document.getElementById('stock-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalContent = document.getElementById('modal-content');

    modalTitle.textContent = 'Loading...';
    modalContent.textContent = '';
    modal.classList.remove('hidden');

    try {
        const response = await fetch(`/api/stocks/${symbol}/profile`);
        if (!response.ok) {
            throw new Error('Failed to fetch company profile.');
        }
        const profile = await response.json();

        modalTitle.textContent = profile.name;
        modalContent.innerHTML = `
            <p><strong>Symbol:</strong> ${profile.symbol}</p>
            <p><strong>Base Currency:</strong> ${profile.currency_base}</p>
            <p><strong>Profit Currency:</strong> ${profile.currency_profit}</p>
            <p><strong>Digits:</strong> ${profile.digits}</p>
            <p><strong>Spread:</strong> ${profile.spread}</p>
            <p><strong>Contract Size:</strong> ${profile.trade_contract_size}</p>
            <p><strong>Min Volume:</strong> ${profile.volume_min}</p>
            <p><strong>Max Volume:</strong> ${profile.volume_max}</p>
            <p><strong>Volume Step:</strong> ${profile.volume_step}</p>
            <p><strong>Initial Margin:</strong> ${profile.margin_initial}</p>
            <p><strong>Maintenance Margin:</strong> ${profile.margin_maintenance}</p>
        `;

    } catch (error) {
        modalTitle.textContent = 'Error';
        modalContent.textContent = error.message;
    }
}
