# core/strategies/base_strategy.py

class BaseStrategy:
    """
    Kelas dasar abstrak untuk semua strategi trading.
    Setiap strategi harus mewarisi kelas ini dan mengimplementasikan metode `analyze`.
    """
    def __init__(self, bot_instance):
        """
        Inisialisasi strategi dengan instance dari bot yang menjalankannya.

        Args:
            bot_instance (TradingBot): Instance dari bot yang aktif.
        """
        self.bot = bot_instance

    def analyze(self):
        """
        Metode inti yang harus di-override oleh setiap strategi turunan.
        Metode ini harus mengembalikan sebuah dictionary yang berisi hasil analisis.
        """
        raise NotImplementedError("Setiap strategi harus mengimplementasikan metode `analyze()`.")