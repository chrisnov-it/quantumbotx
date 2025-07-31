// static/js/bot_detail.js - VERSI PERBAIKAN FINAL

document.addEventListener('DOMContentLoaded', function() {
    // --- Elemen Global ---
    const botNameHeader = document.getElementById('bot-name-header');
    const botMarketHeader = document.getElementById('bot-market-header');
    const botStatusBadge = document.getElementById('bot-status-badge');
    const paramsContainer = document.getElementById('bot-parameters-container');
    const analysisContainer = document.getElementById('bot-analysis-container');
    const analysisSignal = document.getElementById('analysis-signal');
    const historyContainer = document.getElementById('history-log-container');

    // --- State & Helper ---
    const pathParts = window.location.pathname.split('/');
    const botId = pathParts[pathParts.length - 1];
    let botData = null; 

    const formatTimestamp = (iso) =>
        new Date(iso).toLocaleString('id-ID', {
            day: '2-digit', month: 'short', year: 'numeric',
            hour: '2-digit', minute: '2-digit', second: '2-digit'
        });

    // --- Fungsi Pengambil Data ---

    async function fetchBotDetails() {
        try {
            const res = await fetch(`/api/bots/${botId}`);
            if (!res.ok) throw new Error('Gagal memuat detail bot dari server.');
            botData = await res.json();
            if (botData.error) throw new Error(botData.error);

            // Render detail bot
            botNameHeader.textContent = botData.name;
            botMarketHeader.textContent = `Pasar: ${botData.market} | Timeframe: ${botData.timeframe}`;
            botStatusBadge.textContent = botData.status;

            // Render Parameter Standar
            let paramsHTML = `
                <div class="grid grid-cols-2 gap-4">
                    <div><p class="text-gray-500">Lot Size</p><p class="font-semibold text-gray-800">${botData.lot_size}</p></div>
                    <div><p class="text-gray-500">Stop Loss</p><p class="font-semibold text-gray-800">${botData.sl_pips} pips</p></div>
                    <div><p class="text-gray-500">Take Profit</p><p class="font-semibold text-gray-800">${botData.tp_pips} pips</p></div>
                    <div><p class="text-gray-500">Interval</p><p class="font-semibold text-gray-800">${botData.check_interval_seconds}s</p></div>
                </div>
            `;

            // Render Parameter Strategi Kustom jika ada
            const customParams = botData.strategy_params || {}; // Backend sudah mengubahnya menjadi objek
            const customParamKeys = Object.keys(customParams);

            if (customParamKeys.length > 0) {
                paramsHTML += '<div class="border-t mt-4 pt-3"><h4 class="text-sm font-semibold text-gray-700 mb-2">Parameter Strategi</h4><div class="grid grid-cols-2 gap-4">';
                customParamKeys.forEach(key => {
                    const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                    paramsHTML += `<div><p class="text-gray-500">${label}</p><p class="font-semibold text-gray-800">${customParams[key]}</p></div>`;
                });
                paramsHTML += '</div></div>';
            }
            paramsContainer.innerHTML = paramsHTML;
            
        } catch (e) {
            console.error('Error fetching bot details:', e);
            botNameHeader.textContent = 'Gagal Memuat';
            paramsContainer.innerHTML = '<p class="text-center text-red-500">Gagal memuat parameter.</p>';
        }
    }

    async function fetchBotHistory() {
        try {
            const res = await fetch(`/api/bots/${botId}/history`);
            const history = await res.json();
            historyContainer.innerHTML = '';

            if (history.length === 0) {
                historyContainer.innerHTML = '<p class="text-gray-500 p-4 text-center">Belum ada aktivitas.</p>';
                return;
            }

            history.forEach(log => {
                let icon = 'fa-info-circle text-blue-500';
                if (log.action.includes('BELI')) icon = 'fa-arrow-up text-green-500';
                if (log.action.includes('JUAL')) icon = 'fa-arrow-down text-red-500';

                historyContainer.innerHTML += `
                    <div class="flex items-start p-3 border-b border-gray-100">
                        <i class="fas ${icon} mt-1 mr-3"></i>
                        <div class="flex-1">
                            <p class="text-sm text-gray-800">${log.details}</p>
                            <p class="text-xs text-gray-400 mt-1">${formatTimestamp(log.timestamp)}</p>
                        </div>
                    </div>`;
            });
        } catch (e) {
            console.error('Error fetching history:', e);
            historyContainer.innerHTML = '<p class="text-center text-red-500">Gagal memuat riwayat.</p>';
        }
    }

async function fetchAndDisplayAnalysis() {
    if (!botData) { 
        console.log("Menunggu detail bot...");
        return;
    }
    try {
        console.log(`Fetching analysis for bot ID: ${botId}`);
        const res = await fetch(`/api/bots/${botId}/analysis`);
        console.log('Response:', res);
        const analysis = await res.json();
        console.log('Analysis data:', analysis);
        if (!res.ok) throw new Error('Gagal memuat data analisis MT5.');

        // Tampilkan sinyal utama
        const signal = analysis.signal || "TAHAN";
        analysisSignal.textContent = signal;
        let color = 'bg-gray-200 text-gray-800';
        if (signal.includes('BUY')) color = 'bg-green-100 text-green-800';
        if (signal.includes('SELL')) color = 'bg-red-100 text-red-800';
        analysisSignal.className = `mt-4 text-center font-bold text-lg p-2 rounded-md ${color}`;

        // --- PERBAIKAN: Tampilkan semua detail analisis secara dinamis ---
        analysisContainer.innerHTML = ""; // Kosongkan kontainer
        const specialKeys = ['signal', 'explanation']; // Kunci yang tidak perlu ditampilkan di sini

        Object.entries(analysis).forEach(([key, value]) => {
            if (!specialKeys.includes(key) && value !== null && value !== undefined) {
                let formattedValue = value;
                // Format angka menjadi 2-5 desimal, boolean menjadi Ya/Tidak
                if (typeof value === 'number') {
                    formattedValue = value.toFixed(key === 'RSI' ? 2 : 5);
                } else if (typeof value === 'boolean') {
                    formattedValue = value ? 'Ya' : 'Tidak';
                }
                analysisContainer.innerHTML += `<div class="flex justify-between py-1"><span class="text-gray-500">${key.replace(/_/g, ' ')}</span><span class="font-semibold text-gray-800">${formattedValue}</span></div>`;
            }
        });

    } catch (e) {
        console.error('Error fetching analysis:', e);
        analysisSignal.textContent = 'Error';
        analysisContainer.innerHTML = `<p class="text-center text-red-500">${e.message}</p>`;
    }
}

    // --- Pusat Kontrol ---
    // Panggil semua fungsi sekali saat halaman dimuat untuk data awal
    fetchBotDetails();      // Ambil parameter bot (hanya sekali)
    fetchBotHistory();      // Ambil riwayat awal
    fetchAndDisplayAnalysis(); // Ambil analisis awal
    
    // Atur interval refresh untuk data yang dinamis
    setInterval(fetchAndDisplayAnalysis, 5000); // Refresh analisis setiap 5 detik
    setInterval(fetchBotHistory, 10000);      // Refresh riwayat setiap 10 detik
});
