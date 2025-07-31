
document.addEventListener('DOMContentLoaded', function() {
    fetchForexData();

    // Optional: Refresh data every 30 seconds
    // setInterval(fetchForexData, 30000); 
});

function fetchForexData() {
    const tableBody = document.getElementById('forex-table-body');

    fetch('/api/forex-data')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (!tableBody) {
                console.error('Container element #forex-table-body not found.');
                return;
            }

            const symbols = Object.keys(data);

            if (symbols.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="5" class="p-4 text-center text-gray-500">Tidak ada data forex dari MT5.</td></tr>';
                return;
            }

            const rowsHtml = symbols.map(symbolKey => {
                const pair = data[symbolKey];
                const spreadInPips = pair.spread / (pair.digits > 3 ? 10 : 1);
                return `
                    <tr>
                        <td class="px-6 py-4 whitespace-nowrap"><div class="font-medium text-gray-900">${pair.name}</div></td>
                        <td class="px-6 py-4 whitespace-nowrap font-medium">${pair.bid.toFixed(pair.digits)}</td>
                        <td class="px-6 py-4 whitespace-nowrap font-medium">${pair.ask.toFixed(pair.digits)}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${spreadInPips.toFixed(1)} pips</td>
                        <td class="px-6 py-4 whitespace-nowrap text-right">
                            <button class="bg-blue-600 text-white py-1 px-3 rounded-md text-sm font-medium hover:bg-blue-700">Trade</button>
                            <button class="bg-gray-600 text-white py-1 px-3 rounded-md text-sm font-medium hover:bg-gray-700 details-btn" data-symbol="${symbolKey}">Details</button>
                        </td>
                    </tr>
                `;
            }).join('');

            tableBody.innerHTML = rowsHtml;
        })
        .catch(error => {
            console.error('Error fetching forex data:', error);
            if (tableBody) {
                tableBody.innerHTML = '<tr><td colspan="5" class="p-4 text-center text-red-500">Gagal memuat data.</td></tr>';
            }
        });
}

document.addEventListener('click', function(e) {
    if (e.target.classList.contains('details-btn')) {
        const symbol = e.target.dataset.symbol;
        fetchSymbolProfile(symbol);
    }
});

document.getElementById('close-modal').addEventListener('click', function() {
    document.getElementById('forex-modal').classList.add('hidden');
});

async function fetchSymbolProfile(symbol) {
    const modal = document.getElementById('forex-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalContent = document.getElementById('modal-content');

    modalTitle.textContent = 'Loading...';
    modalContent.textContent = '';
    modal.classList.remove('hidden');

    try {
        const response = await fetch(`/api/forex/${symbol}/profile`);
        if (!response.ok) {
            throw new Error('Failed to fetch symbol profile.');
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
