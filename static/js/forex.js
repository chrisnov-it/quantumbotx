
document.addEventListener('DOMContentLoaded', function() {
    fetchForexData();
    // Refresh data setiap 10 detik untuk konsistensi dengan halaman Saham
    setInterval(fetchForexData, 10000); 
});

async function fetchForexData() {
    const tableBody = document.getElementById('forex-table-body');

    // Tampilkan pesan loading jika tabel masih kosong
    if (!tableBody.querySelector('tr')) {
        tableBody.innerHTML = '<tr><td colspan="5" class="p-4 text-center text-gray-500">Memuat data forex...</td></tr>';
    }

    try {
        const response = await fetch('/api/forex-data');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const forexPairs = await response.json(); // API sekarang mengembalikan array

        if (!forexPairs || forexPairs.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" class="p-4 text-center text-gray-500">Tidak ada data forex dari MT5.</td></tr>';
            return;
        }

        const rowsHtml = forexPairs.map(pair => {
            // Spread dihitung berdasarkan poin, bukan pips. Untuk konversi ke pips:
            // Jika digits 5 (misal EURUSD 1.23456), 1 pip = 10 poin.
            // Jika digits 3 (misal USDJPY 123.456), 1 pip = 10 poin.
            // Jika digits 2 atau 4, 1 pip = 1 poin.            
            // Karena data spread sudah dalam poin, dan 1 pip umumnya 10 poin untuk 5/3 digit,
            // atau 1 poin untuk 2/4 digit, kita bisa langsung bagi dengan 10 untuk konversi umum.
            // Ini adalah penyederhanaan karena kita tidak memiliki akses ke mt5.symbol_info di frontend.
            return `
                <tr class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap"><div class="font-medium text-gray-900">${pair.name}</div></td>
                    <td class="px-6 py-4 whitespace-nowrap font-medium">${pair.bid.toFixed(pair.digits)}</td>
                    <td class="px-6 py-4 whitespace-nowrap font-medium">${pair.ask.toFixed(pair.digits)}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${(pair.spread / 10).toFixed(1)} pips</td>
                    <td class="px-6 py-4 whitespace-nowrap text-right">
                        <button class="bg-blue-600 text-white py-1 px-3 rounded-md text-sm font-medium hover:bg-blue-700">Trade</button>
                        <button class="bg-gray-600 text-white py-1 px-3 rounded-md text-sm font-medium hover:bg-gray-700 details-btn" data-symbol="${pair.name}">Details</button>
                    </td>
                </tr>
            `;
        }).join('');

        tableBody.innerHTML = rowsHtml;
    } catch (error) {
        console.error('Error fetching forex data:', error);
        if (tableBody) {
            tableBody.innerHTML = '<tr><td colspan="5" class="p-4 text-center text-red-500">Gagal memuat data.</td></tr>';
        }
    }
}

document.addEventListener('click', function(e) {
    if (e.target.classList.contains('details-btn')) {
        const symbol = e.target.dataset.symbol;
        fetchSymbolProfile(symbol);
    }
});

document.getElementById('close-modal').addEventListener('click', function() {
    document.getElementById('stock-modal').classList.add('hidden'); // Menggunakan modal yang sama dengan stocks
});

async function fetchSymbolProfile(symbol) {
    const modal = document.getElementById('stock-modal'); // Menggunakan modal yang sama dengan stocks
    const modalTitle = document.getElementById('modal-title');
    const modalContent = document.getElementById('modal-content');

    modalTitle.textContent = 'Loading...';
    modalContent.textContent = '';
    modal.classList.remove('hidden');

    try {
        const response = await fetch(`/api/forex/${symbol}/profile`);
        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.error || 'Failed to fetch symbol profile.');
        }
        const profile = await response.json();

        modalTitle.textContent = profile.name;
        modalContent.innerHTML = `
            <div class="space-y-2 text-left">
                <p><strong>Symbol:</strong> ${profile.symbol}</p>
                <p><strong>Base Currency:</strong> ${profile.currency_base}</p>
                <p><strong>Profit Currency:</strong> ${profile.currency_profit}</p>
                <p><strong>Digits:</strong> ${profile.digits}</p>
                <p><strong>Spread:</strong> ${profile.spread} points</p>
                <p><strong>Contract Size:</strong> ${profile.trade_contract_size}</p>
                <p><strong>Min Volume:</strong> ${profile.volume_min}</p>
                <p><strong>Max Volume:</strong> ${profile.volume_max}</p>
                <p><strong>Volume Step:</strong> ${profile.volume_step}</p>
            </div>
        `;

    } catch (error) {
        modalTitle.textContent = 'Error';
        modalContent.textContent = error.message;
    }
}
