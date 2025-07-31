document.getElementById('sidebar-toggle').addEventListener('click', function() {
    document.getElementById('sidebar').classList.toggle('collapsed');
});

async function fetchCryptoData() {
    const tableBody = document.querySelector('tbody');

    try {
        const response = await fetch('/api/crypto');
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }
        const cryptos = await response.json();

        if (!cryptos || cryptos.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" class="p-4 text-center text-gray-500">Tidak ada data cryptocurrency yang tersedia.</td></tr>';
            return;
        }

        const rowsHtml = cryptos.map(crypto => {
            const changeClass = crypto.change.startsWith('+') ? 'text-green-600' : 'text-red-600';
            return `
                <tr>
                    <td class="px-6 py-4 whitespace-nowrap"><div class="flex items-center"><div class="font-medium text-gray-900">${crypto.name}</div><div class="text-sm text-gray-500 ml-2">${crypto.symbol}</div></div></td>
                    <td class="px-6 py-4 whitespace-nowrap font-medium">${crypto.price}</td>
                    <td class="px-6 py-4 whitespace-nowrap ${changeClass} font-medium">${crypto.change}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${crypto.market_cap}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-right"><button class="bg-blue-600 text-white py-1 px-3 rounded-md text-sm font-medium hover:bg-blue-700">Trade</button></td>
                </tr>
            `;
        }).join('');

        tableBody.innerHTML = rowsHtml;
    } catch (error) {
        console.error('Gagal mengambil data crypto:', error);
        tableBody.innerHTML = '<tr><td colspan="5" class="p-4 text-center text-red-500">Gagal memuat data.</td></tr>';
    }
}

document.addEventListener('DOMContentLoaded', fetchCryptoData);
setInterval(fetchCryptoData, 15000);
