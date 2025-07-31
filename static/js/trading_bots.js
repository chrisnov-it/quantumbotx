// static/js/trading_bots.js - VERSI PERBAIKAN

document.addEventListener('DOMContentLoaded', function() {
    // --- Elemen DOM ---
    const tableBody = document.getElementById('bots-table-body');
    const modal = document.getElementById('create-bot-modal');
    const form = document.getElementById('create-bot-form');
    const modalTitle = document.getElementById('modal-title');
    const createBotBtn = document.getElementById('create-bot-btn');
    const cancelBtn = document.getElementById('cancel-create');
    const strategySelect = document.getElementById('strategy');
    let currentBotId = null; // Variabel untuk melacak bot yang sedang diedit

    // --- Fungsi ---

    // Fungsi untuk memuat daftar strategi ke dalam form
    async function loadStrategies() {
        try {
            const response = await fetch('/api/strategies');
            if (!response.ok) throw new Error('Gagal memuat strategi.');
            const strategies = await response.json();
            
            if (strategySelect) {
                strategySelect.innerHTML = '<option value="" disabled selected>Pilih sebuah strategi</option>';
                strategies.forEach(strategy => {
                    const option = document.createElement('option');
                    option.value = strategy.id;
                    option.textContent = strategy.name;
                    strategySelect.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error loading strategies:', error);
            if (strategySelect) {
                strategySelect.innerHTML = '<option value="">Gagal memuat strategi</option>';
            }
        }
    }

    // Fungsi untuk mengambil dan menampilkan semua bot
    async function fetchBots() {
        try {
            const response = await fetch('/api/bots');
            const bots = await response.json();
            tableBody.innerHTML = ''; // Kosongkan tabel sebelum mengisi

            if (bots.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="5" class="text-center p-6 text-gray-500">Belum ada bot yang dibuat.</td></tr>';
                return;
            }

            bots.forEach(bot => {
                const statusClass = bot.status === 'Aktif' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800';
                const startStopButton = bot.status === 'Aktif'
                    ? `<button data-action="stop" data-id="${bot.id}" class="text-yellow-600 hover:text-yellow-900" title="Hentikan Bot"><i class="fas fa-pause-circle fa-lg"></i></button>`
                    : `<button data-action="start" data-id="${bot.id}" class="text-green-600 hover:text-green-900" title="Jalankan Bot"><i class="fas fa-play-circle fa-lg"></i></button>`;

                const row = `
                    <tr class="hover:bg-gray-50">
                        <td class="px-4 py-4">
                            <div class="font-medium text-gray-900">${bot.name}</div>
                            <div class="text-sm text-gray-500">${bot.market}</div>
                        </td>
                        <td class="px-4 py-4 text-sm text-gray-500">
                            <div>Lot: ${bot.lot_size}</div>
                            <div>SL: ${bot.sl_pips} pips | TP: ${bot.tp_pips} pips</div>
                        </td>
                        <td class="px-4 py-4 text-sm text-gray-500">
                            <div>Strategi: ${bot.strategy_name}</div>
                            <div>TF: ${bot.timeframe} | Interval: ${bot.check_interval_seconds}s</div>
                        </td>
                        <td class="px-4 py-4">
                            <span class="px-2 py-1 rounded-full text-xs font-semibold ${statusClass}">${bot.status}</span>
                        </td>
                        <td class="px-4 py-4 text-center">
                            <div class="flex justify-center items-center gap-4">
                                ${startStopButton}
                                <a href="/bots/${bot.id}" class="text-blue-600 hover:text-blue-900" title="Lihat Detail & Analisis"><i class="fas fa-chart-line"></i></a>
                                <button data-action="edit" data-id="${bot.id}" class="text-gray-600 hover:text-gray-900" title="Edit Bot"><i class="fas fa-pencil-alt"></i></button>
                                <button data-action="delete" data-id="${bot.id}" class="text-red-600 hover:text-red-900" title="Hapus Bot"><i class="fas fa-trash"></i></button>
                            </div>
                        </td>
                    </tr>
                `;
                tableBody.innerHTML += row;
            });
        } catch (err) {
            console.error("Gagal memuat bot:", err);
            tableBody.innerHTML = '<tr><td colspan="5" class="text-center p-6 text-red-500">Gagal memuat data bot.</td></tr>';
        }
    }

    // --- Event Listeners ---

    // Buka modal untuk membuat bot baru
    createBotBtn.addEventListener("click", () => {
        currentBotId = null;
        form.reset();
        modalTitle.textContent = '🚀 Buat Bot Baru';
        // Set nilai default
        form.elements.lot_size.value = 0.01;
        form.elements.timeframe.value = 'H1';
        form.elements.sl_pips.value = 100;
        form.elements.tp_pips.value = 200;
        form.elements.check_interval_seconds.value = 60;
        modal.classList.remove('hidden');
    });

    // Tutup modal
    cancelBtn.addEventListener("click", () => {
        modal.classList.add('hidden');
    });

    // Submit form (untuk membuat atau mengedit bot)
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const formData = new FormData(form);
        const data = {};
        formData.forEach((value, key) => {
            if (['lot_size', 'sl_pips', 'tp_pips', 'check_interval_seconds'].includes(key)) {
                data[key] = parseFloat(value);
            } else {
                data[key] = value;
            }
        });

        const url = currentBotId ? `/api/bots/${currentBotId}` : '/api/bots';
        const method = currentBotId ? 'PUT' : 'POST';

        try {
            const res = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await res.json();

            if (res.ok) {
                alert(`✅ ${result.message || 'Operasi berhasil'}`);
                modal.classList.add('hidden');
                fetchBots(); // Refresh tabel setelah berhasil
            } else {
                alert(`❌ Gagal: ${result.error || 'Terjadi kesalahan tidak diketahui'}`);
            }
        } catch (err) {
            console.error(err);
            alert("❌ Gagal terhubung ke server.");
        }
    });

    // Event listener untuk tombol aksi di tabel (start, stop, edit, delete)
    tableBody.addEventListener('click', async (e) => {
        const button = e.target.closest('button[data-action]');
        if (!button) return;

        const action = button.dataset.action;
        const botId = button.dataset.id;

        if (action === 'edit') {
            try {
                const res = await fetch(`/api/bots/${botId}`);
                const bot = await res.json();
                if (res.ok) {
                    currentBotId = botId;
                    modalTitle.textContent = '✏️ Edit Bot';
                    // Isi form dengan data bot yang ada
                    for (const key in bot) {
                        if (form.elements[key]) {
                            form.elements[key].value = bot[key];
                        }
                    }
                    modal.classList.remove('hidden');
                } else {
                    alert(`❌ Gagal memuat data bot: ${bot.error}`);
                }
            } catch (err) {
                console.error(err);
                alert('❌ Gagal terhubung ke server untuk mengedit.');
            }
            return;
        }

        if (action === 'delete') {
            if (!confirm('Apakah Anda yakin ingin menghapus bot ini?')) {
                return;
            }
        }
        
        let endpoint = `/api/bots/${botId}`;
        let method = 'POST';
        
        if (action === 'delete') {
            method = 'DELETE';
        } else if (action === 'start' || action === 'stop') {
            endpoint = `/api/bots/${botId}/${action}`;
        }

        try {
            const res = await fetch(endpoint, { method });
            const result = await res.json();
            
            if (res.ok && !result.error) {
                alert(`✅ ${result.message || 'Operasi berhasil'}`);
                fetchBots(); // Refresh tabel
            } else {
                alert(`❌ ${result.error || 'Operasi gagal'}`);
            }
        } catch (err) {
            console.error(err);
            alert("❌ Gagal terhubung ke server untuk melakukan aksi.");
        }
    });


    // --- Panggilan Awal ---
    loadStrategies(); // Muat strategi saat halaman pertama kali dibuka
    fetchBots(); // Ambil data bot saat halaman pertama kali dibuka
    setInterval(fetchBots, 10000); // Refresh data bot setiap 10 detik
});