// static/js/trading_bots.js - VERSI PERBAIKAN

document.addEventListener('DOMContentLoaded', function() {
    // --- Elemen DOM ---
    const tableBody = document.getElementById('bots-table-body');
    const modal = document.getElementById('create-bot-modal');
    const form = document.getElementById('create-bot-form');
    const modalTitle = document.getElementById('modal-title');
    const submitBtn = document.getElementById('submit-bot-btn'); // <-- 1. Ambil elemen tombol
    const createBotBtn = document.getElementById('create-bot-btn');
    const startAllBtn = document.getElementById('start-all-btn');
    const stopAllBtn = document.getElementById('stop-all-btn');
    const cancelBtn = document.getElementById('cancel-create');
    const cancelBtnFooter = document.getElementById('cancel-create-footer'); // Tombol Batal di footer
    const paramsContainer = document.getElementById('strategy-params-container');
    const strategySelect = document.getElementById('strategy');
    let currentBotId = null; // Variabel untuk melacak bot yang sedang diedit

    // --- Fungsi ---

    // Fungsi untuk mengisi nilai parameter strategi saat mengedit bot
    function fillStrategyParams(params) {
        if (!params) return;
        Object.entries(params).forEach(([key, value]) => {
            const inputElement = document.getElementById(key);
            if (inputElement) {
                inputElement.value = value;
            }
        });
    }
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
        paramsContainer.innerHTML = ''; // Kosongkan parameter
        form.reset();
        submitBtn.textContent = 'Buat Bot'; // <-- 2. Set teks untuk mode 'Create'
        modalTitle.textContent = '🚀 Buat Bot Baru';
        // Set nilai default
        form.elements.lot_size.value = 0.01;
        form.elements.timeframe.value = 'H1';
        form.elements.sl_pips.value = 100;
        form.elements.tp_pips.value = 200;
        form.elements.check_interval_seconds.value = 60;
        modal.classList.remove('hidden');
    });

    // Event listener untuk tombol Start All dengan UX Improvement
    startAllBtn.addEventListener('click', async () => {
        if (!confirm('Apakah Anda yakin ingin menjalankan semua bot yang sedang dijeda?')) return;

        const originalHtml = startAllBtn.innerHTML;
        startAllBtn.disabled = true;
        startAllBtn.innerHTML = `<i class="fas fa-spinner fa-spin mr-2"></i> Memulai...`;

        try {
            const res = await fetch('/api/bots/start_all', { method: 'POST' });
            const result = await res.json();
            if (res.ok) {
                alert(`✅ ${result.message}`);
                fetchBots(); // Refresh tabel
            } else {
                alert(`❌ ${result.error}`);
            }
        } catch (err) {
            console.error('Error starting all bots:', err);
            alert('❌ Gagal terhubung ke server.');
        } finally {
            startAllBtn.disabled = false;
            startAllBtn.innerHTML = originalHtml;
        }
    });

    // Event listener untuk tombol Stop All dengan UX Improvement
    stopAllBtn.addEventListener('click', async () => {
        if (!confirm('Apakah Anda yakin ingin menghentikan semua bot yang sedang berjalan?')) return;

        const originalHtml = stopAllBtn.innerHTML;
        stopAllBtn.disabled = true;
        stopAllBtn.innerHTML = `<i class="fas fa-spinner fa-spin mr-2"></i> Menghentikan...`;

        try {
            const res = await fetch('/api/bots/stop_all', { method: 'POST' });
            const result = await res.json();
            if (res.ok) {
                alert(`✅ ${result.message}`);
                fetchBots(); // Refresh tabel
            } else {
                alert(`❌ ${result.error}`);
            }
        } catch (err) {
            console.error('Error stopping all bots:', err);
            alert('❌ Gagal terhubung ke server.');
        } finally {
            stopAllBtn.disabled = false;
            stopAllBtn.innerHTML = originalHtml;
        }
    });

    // Tutup modal
    function closeModal() {
        modal.classList.add('hidden');
    }

    cancelBtn.addEventListener("click", closeModal);
    cancelBtnFooter.addEventListener("click", closeModal);

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

        // Kumpulkan parameter strategi dinamis
        const params = {};
        const paramInputs = paramsContainer.querySelectorAll('input');
        paramInputs.forEach(input => {
            params[input.name] = parseFloat(input.value) || input.value;
        });
        data.params = params;

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
            console.error('Error submitting bot form:', err);
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
        // 1. Tampilkan modal & loading overlay segera untuk respons instan
        modalTitle.textContent = '✏️ Memuat Data Bot...';
        submitBtn.textContent = 'Ubah Bot';
        form.reset();
        paramsContainer.innerHTML = '';
        modal.classList.remove('hidden');
        const loadingOverlay = document.getElementById('modal-loading-overlay');
        if(loadingOverlay) loadingOverlay.classList.remove('hidden');

        try {
            const res = await fetch(`/api/bots/${botId}`);
            const bot = await res.json();

            if (res.ok) {
                modalTitle.textContent = '✏️ Edit Bot'; // Perbarui judul setelah data dimuat
                currentBotId = botId;
                
                // 2. Isi form dengan data yang sudah diambil
                for (const key in bot) {
                    if (form.elements[key]) {
                        form.elements[key].value = bot[key];
                    }
                }
                
                // 3. Trigger event untuk memuat parameter strategi
                strategySelect.dispatchEvent(new Event('change', { 'bubbles': true }));
                
                // 4. Tunggu sebentar lalu isi parameter strategi
                await new Promise(resolve => setTimeout(() => {
                    if (bot.strategy_params) {
                        fillStrategyParams(bot.strategy_params);
                    }
                    resolve();
                }, 250));

            } else {
                alert(`❌ Gagal memuat data bot: ${bot.error}`);
                modal.classList.add('hidden'); // Sembunyikan modal jika gagal
            }
        } catch (err) {
            console.error(`Error fetching bot ${botId} for edit:`, err);
            alert('❌ Gagal terhubung ke server untuk mengedit.');
            modal.classList.add('hidden'); // Sembunyikan modal jika gagal
        } finally {
            // 5. Sembunyikan loading overlay setelah semua selesai
            if(loadingOverlay) loadingOverlay.classList.add('hidden');
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
            console.error(`Error performing action '${action}' on bot ${botId}:`, err);
            alert("❌ Gagal terhubung ke server untuk melakukan aksi.");
        }
    });

    // Event listener untuk dropdown strategi
    strategySelect.addEventListener('change', async (e) => {
        const strategyId = e.target.value;
        paramsContainer.innerHTML = '<p class="text-sm text-gray-500">Memuat parameter...</p>';
        if (!strategyId) {
            paramsContainer.innerHTML = '';
            return;
        }

        try {
            const res = await fetch(`/api/strategies/${strategyId}/params`);
            const params = await res.json();
            paramsContainer.innerHTML = ''; // Kosongkan lagi

            if (params.length > 0) {
                params.forEach(param => {
                    const paramField = `
                        <div class="col-span-1">
                            <label for="${param.name}" class="block text-sm font-medium text-gray-700">${param.label}</label>
                            <input type="${param.type || 'number'}" name="${param.name}" id="${param.name}" value="${param.default}" step="${param.step || 'any'}"
                                   class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
                        </div>
                    `;
                    paramsContainer.innerHTML += paramField;
                });
            } else {
                paramsContainer.innerHTML = '<p class="text-sm text-gray-500 col-span-2">Strategi ini tidak memiliki parameter kustom.</p>';
            }
        } catch (err) {
            console.error('Gagal memuat parameter strategi:', err);
            paramsContainer.innerHTML = '<p class="text-sm text-red-500 col-span-2">Gagal memuat parameter.</p>';
        }
    });

    // --- Panggilan Awal ---
    loadStrategies(); // Muat strategi saat halaman pertama kali dibuka
    fetchBots(); // Ambil data bot saat halaman pertama kali dibuka
    setInterval(fetchBots, 10000); // Refresh data bot setiap 10 detik
});