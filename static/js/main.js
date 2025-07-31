// static/js/main.js


document.addEventListener('DOMContentLoaded', function() {
    // --- Logika untuk Sidebar Toggle ---
    const sidebarToggle = document.getElementById('sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.getElementById('sidebar').classList.toggle('collapsed');
        });
    }

    // --- Logika untuk Notifikasi Real-time ---
    const notificationDot = document.getElementById('notification-dot');

    async function checkUnreadNotifications() {
        if (!notificationDot) return; // Jangan jalankan jika elemen tidak ada
        try {
            const response = await fetch('/api/notifications/unread-count');
            const data = await response.json();
            if (data.unread_count > 0) {
                notificationDot.classList.remove('hidden');
            } else {
                notificationDot.classList.add('hidden');
            }
        } catch (error) {
            console.error('Gagal memeriksa notifikasi:', error);
        }
    }

    // Periksa saat halaman dimuat, lalu periksa setiap 15 detik
    checkUnreadNotifications();
    setInterval(checkUnreadNotifications, 15000);
});