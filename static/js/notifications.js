document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('notifications-container');

    const formatTimestamp = (isoString) => {
        const date = new Date(isoString);
        return date.toLocaleString('id-ID', {
            day: '2-digit', month: 'short', year: 'numeric',
            hour: '2-digit', minute: '2-digit'
        });
    };

    const getNotificationAppearance = (action) => {
        const lowerAction = action.toLowerCase();
        if (lowerAction.includes('buy')) return { icon: 'fa-arrow-up', color: 'green' };
        if (lowerAction.includes('sell')) return { icon: 'fa-arrow-down', color: 'red' };
        if (lowerAction.includes('start')) return { icon: 'fa-play-circle', color: 'blue' };
        if (lowerAction.includes('stop')) return { icon: 'fa-pause-circle', color: 'yellow' };
        if (lowerAction.includes('error')) return { icon: 'fa-exclamation-triangle', color: 'red' };
        return { icon: 'fa-info-circle', color: 'gray' };
    };

    async function fetchNotifications() {
        try {
            const response = await fetch('/api/notifications');
            if (!response.ok) throw new Error('Gagal memuat notifikasi');
            const notifications = await response.json();

            if (notifications.length === 0) {
                container.innerHTML = '<p class="p-6 text-center text-gray-500">Tidak ada notifikasi.</p>';
                return;
            }

            const notificationsHtml = notifications.map(notif => {
                const appearance = getNotificationAppearance(notif.action);
                const message = `<strong>[${notif.bot_name}]</strong> ${notif.details}`;
                return `
                    <div class="p-4 flex items-start hover:bg-gray-50 cursor-pointer">
                        <div class="w-10 h-10 rounded-full bg-${appearance.color}-100 flex items-center justify-center text-${appearance.color}-600 mr-4 flex-shrink-0"><i class="fas ${appearance.icon}"></i></div>
                        <div>
                            <p class="text-sm text-gray-800">${message}</p>
                            <p class="text-xs text-gray-500 mt-1">${formatTimestamp(notif.timestamp)}</p>
                        </div>
                    </div>`;
            }).join('');

            container.innerHTML = notificationsHtml;

        } catch (error) {
            console.error("Error fetching notifications:", error);
            container.innerHTML = `<p class="p-6 text-center text-red-500">Gagal memuat notifikasi: ${error.message}</p>`;
        }
    }

    fetchNotifications();

    // Setelah memuat notifikasi, tandai semua sebagai sudah dibaca
    fetch('/api/notifications/mark-as-read', {
        method: 'POST'
    }).then(response => response.json())
      .then(data => console.log(data.message))
      .catch(error => console.error('Gagal menandai notifikasi:', error));

});