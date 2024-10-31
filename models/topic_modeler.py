# models/topic_modeler.py
import logging
from typing import List, Dict, Optional, Tuple

import numpy as np
import pandas as pd
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer

from config import Config
from interfaces.topic_modeler_interface import ITopicModeler

logger = logging.getLogger(__name__)


class TopicModeler(ITopicModeler):

    def __init__(self, predefined_topics: Optional[List[Dict]] = None):

        try:
            logger.info("شروع به بارگذاری مدل تعبیه‌سازی جملات.")
            self.embedding_model = SentenceTransformer(Config.MODEL_NAME)
            logger.info(f"مدل تعبیه‌سازی '{Config.MODEL_NAME}' با موفقیت بارگذاری شد.")

            self.predefined_topics = predefined_topics

            persian_stop_words = [
                'و', 'در', 'به', 'از', 'که', 'با', 'برای', 'این', 'را', 'آن', 'ها', 'یک', 'می', 'تا', 'بر', 'یا', 'اما',
                'دیگر', 'هم', 'کرده', 'کرد', 'بود', 'بودن', 'باشه', 'نیز', 'از', 'باشد'
            ]

            vectorizer = CountVectorizer(
                stop_words=persian_stop_words,
                ngram_range=(1, 3),
                max_features=5000
            )

            self.topic_model = BERTopic(
                embedding_model=self.embedding_model,
                vectorizer_model=vectorizer,
                calculate_probabilities=True,
                verbose=False,
                min_topic_size=2,
                top_n_words=10,
                nr_topics=10
            )

            logger.info(f"BERTopic با مدل '{Config.MODEL_NAME}' مقداردهی اولیه شد.")
            mode = 'موضوعات از پیش تعریف شده' if predefined_topics else 'تشخیص خودکار موضوعات'
            logger.info(f"حالت مدل‌سازی: {mode}")

        except Exception as e:
            logger.error(f"خطا در مقداردهی اولیه TopicModeler: {str(e)}")
            raise

    def fit_transform(self, documents: List[str]) -> Tuple[List[int], np.ndarray, np.ndarray]:

        try:
            logger.info("شروع فرآیند مدل‌سازی موضوعات.")
            valid_docs = [str(doc).strip() for doc in documents if str(doc).strip()]
            if not valid_docs:
                raise ValueError("هیچ سند معتبر برای پردازش ارائه نشده است.")

            logger.info(f"{len(valid_docs)} سند برای پردازش موجود است.")
            embeddings = self.embedding_model.encode(valid_docs, show_progress_bar=True)
            logger.info("تعبیه‌سازی اسناد تکمیل شد.")

            topics, probs = self.topic_model.fit_transform(valid_docs, embeddings)
            logger.info("مدل‌سازی موضوعات با BERTopic انجام شد.")
            return topics, probs, embeddings
        except Exception as e:
            logger.error(f"خطا در fit_transform: {str(e)}")
            raise

    def get_topic_info(self) -> Optional[pd.DataFrame]:
        try:
            topic_info = self.topic_model.get_topic_info()
            logger.info("دریافت اطلاعات موضوعات موفقیت‌آمیز بود.")
            return topic_info
        except Exception as e:
            logger.error(f"خطا در دریافت اطلاعات موضوعات: {str(e)}")
            return None

    def get_topics(self) -> Optional[Dict[int, List[tuple]]]:
        try:
            topics = self.topic_model.get_topics()
            logger.info("دریافت کلمات کلیدی موضوعات موفقیت‌آمیز بود.")
            return topics
        except Exception as e:
            logger.error(f"خطا در دریافت موضوعات: {str(e)}")
            return None
