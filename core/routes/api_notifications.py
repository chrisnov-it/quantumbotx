# core/routes/api_notifications.py

from core.db import queries
from flask import Blueprint, jsonify, request

api_notifications = Blueprint('api_notifications', __name__)

@api_notifications.route('/api/notifications', methods=['GET'])
def get_notifications_route():
    """Mengembalikan daftar notifikasi penting."""
    try:
        # Saat pengguna mengunjungi halaman notifikasi, tandai semua sebagai sudah dibaca
        queries.mark_notifications_as_read()
        notifications = queries.get_notifications()
        return jsonify(notifications)
    except Exception as e:
        return jsonify({"error": f"Gagal mengambil notifikasi: {e}"}), 500

@api_notifications.route('/api/notifications/unread-count')
def get_unread_notifications_count_route():
    """Mengembalikan jumlah notifikasi yang belum dibaca."""
    try:
        count = queries.get_unread_notifications_count()
        return jsonify(count)
    except Exception as e:
        return jsonify({"error": f"Gagal menghitung notifikasi: {e}"}), 500

@api_notifications.route('/api/notifications/unread', methods=['GET'])
def get_unread_notifications_route():
    """Mengembalikan notifikasi yang belum dibaca untuk toast."""
    try:
        notifications = queries.get_unread_notifications()
        return jsonify(notifications)
    except Exception as e:
        return jsonify({"error": f"Gagal mengambil notifikasi belum dibaca: {e}"}), 500

@api_notifications.route('/api/notifications/mark-as-read', methods=['POST'])
def mark_notifications_as_read_route():
    """Menandai notifikasi spesifik sebagai sudah dibaca."""
    try:
        data = request.get_json()
        if not data or 'ids' not in data:
            return jsonify({"error": "Request body harus menyertakan 'ids'"}), 400
        
        notification_ids = data['ids']
        if not isinstance(notification_ids, list):
            return jsonify({"error": "'ids' harus berupa array/list"}), 400

        queries.mark_notifications_as_read(notification_ids)
        return jsonify({'message': f'{len(notification_ids)} notifikasi ditandai sudah dibaca.'})
    except Exception as e:
        return jsonify({"error": f"Gagal menandai notifikasi: {e}"}), 500
