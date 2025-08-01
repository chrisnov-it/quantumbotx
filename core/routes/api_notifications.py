# core/routes/api_notifications.py

from core.db import queries
from flask import Blueprint, jsonify

api_notifications = Blueprint('api_notifications', __name__)

@api_notifications.route('/api/notifications', methods=['GET'])
def get_notifications_route():
    """Mengembalikan daftar notifikasi penting."""
    try:
        notifications = queries.get_notifications()
        return jsonify(notifications)
    except Exception as e:
        return jsonify({"error": f"Gagal mengambil notifikasi: {e}"}), 500

@api_notifications.route('/api/notifications/unread-count')
def get_unread_notifications_count():
    """Mengembalikan jumlah notifikasi yang belum dibaca."""
    try:
        count = queries.get_unread_notifications_count()
        return jsonify(count)
    except Exception as e:
        return jsonify({"error": f"Gagal menghitung notifikasi: {e}"}), 500

@api_notifications.route('/api/notifications/mark-as-read', methods=['POST'])
def mark_notifications_as_read():
    """Menandai semua notifikasi sebagai sudah dibaca."""
    try:
        queries.mark_notifications_as_read()
        return jsonify({'message': 'Semua notifikasi ditandai sudah dibaca.'})
    except Exception as e:
        return jsonify({"error": f"Gagal menandai notifikasi: {e}"}), 500
