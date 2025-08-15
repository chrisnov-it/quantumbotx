// static/js/main.js

document.addEventListener('DOMContentLoaded', function() {
    // --- Logika untuk Sidebar Toggle ---
    const sidebarToggle = document.getElementById('sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.getElementById('sidebar').classList.toggle('collapsed');
        });
    }

    // --- Logika untuk Notifikasi Real-time dengan Toast ---
    const notificationDot = document.getElementById('notification-dot');

    // Fungsi untuk menampilkan notifikasi menggunakan Toastify
    function showToast(message, type = 'info') {
        // Disesuaikan dengan jenis notifikasi jika ada
        let backgroundColor = "linear-gradient(to right, #00b09b, #96c93d)"; // Default (info/success)

        Toastify({
            text: `🔔 ${message}`,
            duration: 6000, // 6 detik
            close: true,
            gravity: "top",
            position: "right",
            stopOnFocus: true,
            style: {
                background: backgroundColor,
                borderRadius: "8px",
                boxShadow: "0 3px 6px -1px rgba(0, 0, 0, 0.12), 0 10px 36px -4px rgba(77, 96, 232, 0.3)"
            },
            onClick: function(){
                window.location.href = "/notifications"; // Arahkan ke halaman notifikasi jika di-klik
            }
        }).showToast();
    }

    // Fungsi untuk mengambil notifikasi baru dan menandainya sebagai sudah ditampilkan
    async function fetchAndShowNotifications() {
        try {
            // 1. Ambil notifikasi yang belum dibaca
            const response = await fetch('/api/notifications/unread');
            if (!response.ok) return; // Gagal secara diam-diam jika ada error server

            const notifications = await response.json();

            if (notifications && notifications.length > 0) {
                if (notificationDot) notificationDot.classList.remove('hidden');

                const notificationIds = [];
                notifications.forEach(notif => {
                    // 2. Tampilkan setiap notifikasi sebagai toast
                    showToast(notif.details);
                    notificationIds.push(notif.id);
                });

                // 3. Tandai notifikasi ini sebagai sudah dibaca
                await fetch('/api/notifications/mark-as-read', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ ids: notificationIds }),
                });
            }
        } catch (error) {
            console.error('Gagal mengambil notifikasi toast:', error);
        }
    }
    
    // Fungsi untuk memeriksa status titik notifikasi (bahkan jika toast tidak muncul)
    async function checkNotificationStatus() {
         if (!notificationDot) return;
         try {
            const response = await fetch('/api/notifications/unread-count');
            const data = await response.json();
            if (data.unread_count > 0) {
                notificationDot.classList.remove('hidden');
            } else {
                notificationDot.classList.add('hidden');
            }
        } catch (error) {
            console.error('Gagal memeriksa status notifikasi:', error);
        }
    }

    // Jalankan saat halaman dimuat, lalu periksa setiap 10 detik
    setTimeout(() => {
        fetchAndShowNotifications();
        checkNotificationStatus();
    }, 1000); // Beri jeda 1 detik saat awal load
    
    setInterval(fetchAndShowNotifications, 10000); // Ambil notif baru & tampilkan toast
    setInterval(checkNotificationStatus, 10000); // Pastikan status dot selalu sinkron
});
