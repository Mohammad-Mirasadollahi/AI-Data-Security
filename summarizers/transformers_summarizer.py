# summarizers/transformers_summarizer.py
import logging
from typing import List

from transformers import pipeline

from config import Config
from interfaces.summarizer_interface import ISummarizer

logger = logging.getLogger(__name__)


class TransformersSummarizer(ISummarizer):


    def __init__(self, model_name: str = Config.SUMMARIZER_MODEL):

        try:
            logger.info(f"بارگذاری مدل خلاصه‌سازی: {model_name}")
            self.summarizer = pipeline("summarization", model=model_name)
            logger.info("مدل خلاصه‌سازی با موفقیت بارگذاری شد.")
        except Exception as e:
            logger.error(f"خطا در بارگذاری مدل خلاصه‌سازی: {str(e)}")
            raise

    def summarize(self, texts: List[str]) -> List[str]:

        logger.info("شروع خلاصه‌سازی متون.")
        summaries = []
        try:
            for text in texts:
                # توجه: برخی مدل‌ها محدودیت طول ورودی دارند. ممکن است نیاز به تقسیم متن به بخش‌های کوچکتر باشد.
                summary = self.summarizer(text, max_length=130, min_length=30, do_sample=False)
                summaries.append(summary[0]['summary_text'])
                logger.debug(f"خلاصه متن: {summary[0]['summary_text']}")
            logger.info("خلاصه‌سازی متون با موفقیت انجام شد.")
            return summaries
        except Exception as e:
            logger.error(f"خطا در خلاصه‌سازی متون: {str(e)}")
            raise
