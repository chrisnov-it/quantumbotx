# core/strategies/base_strategy.py

class BaseStrategy:
    """
    Kelas dasar abstrak untuk semua strategi trading.
    Setiap strategi harus mewarisi kelas ini dan mengimplementasikan metode `analyze`.
    """
    def __init__(self, bot_instance, params: dict = {}):
        """
        Inisialisasi strategi dengan instance dari bot yang menjalankannya.

        Args:
            bot_instance (TradingBot): Instance dari bot yang aktif.
            params (dict): Dictionary berisi parameter kustom untuk strategi.
        """
        self.bot = bot_instance
        self.params = params

    def analyze(self):
        """
        Metode inti yang harus di-override oleh setiap strategi turunan.
        Metode ini harus mengembalikan sebuah dictionary yang berisi hasil analisis.
        """
        raise NotImplementedError("Setiap strategi harus mengimplementasikan metode `analyze()`.")

    @classmethod
    def get_definable_params(cls):
        """
        Metode kelas yang mengembalikan daftar parameter yang bisa diatur oleh pengguna.
        Setiap strategi turunan harus meng-override ini jika memiliki parameter.
        """
        return []