# core/strategies/base_strategy.py

from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    """
    Kelas dasar abstrak untuk semua strategi trading.
    Setiap strategi harus mewarisi kelas ini dan mengimplementasikan metode `analyze`.
    """
    def __init__(self, bot_instance, params: dict = {}):
        self.bot = bot_instance
        self.params = params

    @abstractmethod
    def analyze(self, df):
        """
        Metode inti yang harus di-override oleh setiap strategi turunan.
        Metode ini harus mengembalikan sebuah dictionary yang berisi hasil analisis.
        Menerima DataFrame sebagai input.
        """
        raise NotImplementedError("Setiap strategi harus mengimplementasikan metode `analyze(df)`.")

    @classmethod
    def get_definable_params(cls):
        """
        Metode kelas yang mengembalikan daftar parameter yang bisa diatur oleh pengguna.
        Setiap strategi turunan harus meng-override ini jika memiliki parameter.
        """
        return []