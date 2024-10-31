# models/categorizer.py
import logging
from typing import List, Dict, Tuple

import numpy as np
from transformers import pipeline

from config import Config
from interfaces.categorizer_interface import ICategorizer

logger = logging.getLogger(__name__)


class Categorizer(ICategorizer):

    def __init__(self, topic_modeler: 'ITopicModeler'):

        self.topic_modeler = topic_modeler
        self.topic_labels = {}
        self.zero_shot_classifier = None
        self.load_zero_shot_classifier()

    def load_zero_shot_classifier(self):
        try:
            logger.info("بارگذاری مدل طبقه‌بندی صفر-شات.")
            self.zero_shot_classifier = pipeline(
                "zero-shot-classification",
                model=Config.ZERO_SHOT_MODEL,
            )
            logger.info("مدل طبقه‌بندی صفر-شات با موفقیت بارگذاری شد.")
        except Exception as e:
            logger.error(f"خطا در بارگذاری مدل طبقه‌بندی صفر-شات: {str(e)}")
            raise

    def assign_automatic_labels(self):
        try:
            logger.info("شروع تخصیص خودکار برچسب‌ها.")
            topic_info = self.topic_modeler.get_topic_info()
            if topic_info is None:
                raise ValueError("عدم توانایی در دریافت اطلاعات موضوعات.")

            for _, row in topic_info.iterrows():
                topic_id = row['Topic']

                if topic_id == -1:
                    self.topic_labels[topic_id] = 'خارج از دسته‌بندی'
                    continue

                topic_words = [word for word, _ in self.topic_modeler.get_topics()[topic_id]][:10]

                labels = topic_words

                topic_desc = " ".join(topic_words)

                classification = self.zero_shot_classifier(
                    sequences=topic_desc,
                    candidate_labels=labels,
                    multi_label=True
                )
                if classification['labels']:
                    best_label = classification['labels'][0]
                else:
                    best_label = f"موضوع {topic_id}"

                self.topic_labels[topic_id] = best_label

                logger.debug(f"موضوع {topic_id} با برچسب '{best_label}' تخصیص داده شد.")

            logger.info("تخصیص خودکار برچسب‌ها با موفقیت انجام شد.")
        except Exception as e:
            logger.error(f"خطا در تخصیص خودکار برچسب‌ها: {str(e)}")
            raise

    def assign_predefined_labels(self, embeddings: np.ndarray, predefined_topics: List[Dict]) -> Tuple[
        List[str], List[float]]:
        try:
            logger.info("شروع تخصیص برچسب‌های از پیش تعریف شده.")
            if not predefined_topics:
                raise ValueError("موضوعات از پیش تعریف شده‌ای ارائه نشده است.")

            topic_labels = [topic['label'] for topic in predefined_topics]
            topic_label_embeddings = self.topic_modeler.embedding_model.encode(
                topic_labels, show_progress_bar=False
            )
            logger.debug(f"تعبیه‌سازی برچسب‌های موضوعات از پیش تعریف شده انجام شد.")

            embeddings_norm = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
            topic_label_embeddings_norm = topic_label_embeddings / np.linalg.norm(topic_label_embeddings, axis=1,
                                                                                  keepdims=True)

            similarities = np.dot(embeddings_norm, topic_label_embeddings_norm.T)
            logger.debug("محاسبه شباهت کسینوسی بین اسناد و برچسب‌ها انجام شد.")

            assigned_labels = []
            confidences = []
            for sim in similarities:
                idx = np.argmax(sim)
                assigned_labels.append(topic_labels[idx])
                confidences.append(sim[idx])

            logger.info("تخصیص برچسب‌های از پیش تعریف شده با موفقیت انجام شد.")
            return assigned_labels, confidences

        except Exception as e:
            logger.error(f"خطا در تخصیص برچسب‌های از پیش تعریف شده: {str(e)}")
            raise
