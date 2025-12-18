import google.generativeai as genai
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        # Configure Gemini
        # In a real app, this API key should come from settings.GEMINI_API_KEY
        # For this PoC, we expect it in env vars or settings
        try:
            if hasattr(settings, 'GOOGLE_API_KEY') and settings.GOOGLE_API_KEY:
                genai.configure(api_key=settings.GOOGLE_API_KEY)
                # Updated to 2.5-flash as 1.5 is not available in current environment
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                self.enabled = True
            else:
                logger.warning("GOOGLE_API_KEY not found in settings. AI features disabled.")
                self.enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize AI Service: {e}")
            self.enabled = False

    async def generate_daily_brief(self, context_data: dict) -> str:
        """
        Generate a daily briefing based on statistical prediction data.
        """
        if not self.enabled:
            return "AI Hizmeti devredışı (API Key eksik)."
            
        try:
            prompt = f"""
            Sen bir restoran yöneticisi asistanısın. Aşağıdaki verilere göre işletme sahibine günlük, motive edici ve operasyonel tavsiyeler içeren kısa bir brifing ver.
            
            Veriler:
            - Tarih: {context_data.get('date')} ({context_data.get('day_name')})
            - Lokasyon: {context_data.get('city', 'Belirtilmemiş')}
            - Hava Durumu: {context_data.get('weather_forecast')}
            - Beklenen Ciro: {context_data.get('prediction', {}).get('revenue')} TL
            - Beklenen Müşteri: {context_data.get('prediction', {}).get('covers')} kişi
            - Hazırlık Tavsiyesi: {context_data.get('prep_advice', {}).get('cig_kofte_kg')} kg çiğ köfte, {context_data.get('prep_advice', {}).get('lavash_packs')} paket lavaş.
            
            Lütfen şu formatta yanıt ver:
            1. Genel Durum Özeti (kısa)
            2. Operasyonel Tavsiye (özellikle hava durumu ve yoğunluğa göre personel/kurye uyarısı)
            3. Hazırlık Notu (mutfak için net rakamlar)
            4. Günün Mottosu (eğlenceli)
            
            Samimi ve profesyonel bir dil kullan. Türkçe yanıt ver.
            """
            
            response = await self.model.generate_content_async(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"AI Generation failed: {e}")
            return "AI Analizi şu an yapılamıyor, lütfen daha sonra deneyin."
