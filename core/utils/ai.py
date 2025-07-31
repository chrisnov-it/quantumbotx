# core/utils/ai.py - VERSI PERBAIKAN

import ollama
import logging
# Hapus impor ini dari bagian atas file untuk memutus lingkaran
# from core.bots.controller import get_bot_analysis_data, get_bot_instance_by_id

logger = logging.getLogger(__name__)

# Fungsi lain di file ini... (jika ada)

def get_ai_analysis(bot_id, market_data):
    """
    Menganalisis data pasar menggunakan model AI dari Ollama dan memberikan keputusan.
    """
    # Lakukan impor di dalam fungsi (impor lokal)
    from core.bots.controller import get_bot_instance_by_id

    try:
        bot = get_bot_instance_by_id(bot_id)
        if not bot:
            return {
                "ai_decision": "ERROR",
                "ai_explanation": "Bot instance not found in controller.",
                "ai_suggested_strategy": "N/A"
            }

        # ... (sisa kode fungsi Anda tetap sama) ...
        
        # Contoh sisa kode:
        prompt = f"Analyze the following market data for {bot.market} and decide whether to BUY, SELL, or HOLD..."
        
        response = ollama.chat(
            model='llama3',
            messages=[{'role': 'user', 'content': prompt}]
        )
        
        # Logika untuk mem-parsing response AI
        decision = "HOLD" # Default
        explanation = response['message']['content']
        
        if "BUY" in explanation.upper():
            decision = "BUY"
        elif "SELL" in explanation.upper():
            decision = "SELL"
            
        return {
            "ai_decision": decision,
            "ai_explanation": explanation,
            "ai_suggested_strategy": "Based on analysis"
        }

    except Exception as e:
        logger.error(f"Error during AI analysis for bot {bot_id}: {e}", exc_info=True)
        return {
            "ai_decision": "ERROR",
            "ai_explanation": str(e),
            "ai_suggested_strategy": "N/A"
        }