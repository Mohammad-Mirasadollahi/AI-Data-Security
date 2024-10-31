# processors/integrated_processor.py
import datetime
import logging
import os
from typing import List, Optional, Dict

import pandas as pd

from config import Config
from interfaces.categorizer_interface import ICategorizer
from interfaces.document_reader_interface import IDocumentReader
# from interfaces.summarizer_interface import ISummarizer
from interfaces.topic_modeler_interface import ITopicModeler

logger = logging.getLogger(__name__)


class IntegratedProcessor:

    def __init__(
            self,
            topic_modeler: ITopicModeler,
            categorizer: ICategorizer,
            document_reader: IDocumentReader,
            # summarizer: Optional[ISummarizer],
            folder_path: str,
            predefined_topics: Optional[List[Dict]] = None
    ):

        self.folder_path = folder_path
        self.predefined_topics = predefined_topics
        self.topic_modeler = topic_modeler
        self.categorizer = categorizer
        self.document_reader = document_reader
        # self.summarizer = summarizer
        self.documents = self.document_reader.read_documents(self.folder_path)

        # if self.summarizer:
        #     logger.info("شروع خلاصه‌سازی اسناد.")
        #     self.documents = self.summarizer.summarize(self.documents)

    def run(self, use_zero_shot: bool = False) -> pd.DataFrame:

        try:
            logger.info("شروع فرآیند یکپارچه مدل‌سازی موضوعات و دسته‌بندی.")
            if not self.documents:
                logger.warning("هیچ سندی برای پردازش یافت نشد.")
                return pd.DataFrame()

            topics, probabilities, embeddings = self.topic_modeler.fit_transform(self.documents)

            if use_zero_shot:
                logger.info("استفاده از طبقه‌بندی صفر-شات برای تخصیص برچسب‌ها.")
                self.categorizer.assign_automatic_labels()
                labeled_topics = [self.categorizer.topic_labels.get(topic, f"موضوع {topic}") for topic in topics]
                assigned_topic_probs = [
                    probabilities[i][topic] if topic in probabilities[i] else 0
                    for i, topic in enumerate(topics)
                ]
                df = pd.DataFrame({
                    'Document': self.documents,
                    'Topic': topics,
                    'Assigned Label': labeled_topics,
                    'Confidence': assigned_topic_probs
                })
            elif self.predefined_topics:
                logger.info("استفاده از برچسب‌های از پیش تعریف شده برای تخصیص برچسب‌ها.")
                assigned_labels, confidences = self.categorizer.assign_predefined_labels(embeddings,
                                                                                         self.predefined_topics)
                df = pd.DataFrame({
                    'Document': self.documents,
                    'Assigned Label': assigned_labels,
                    'Confidence': confidences
                })
            else:
                logger.info("استفاده از تخصیص برچسب خودکار بدون طبقه‌بندی صفر-شات.")
                self.categorizer.assign_automatic_labels()
                labeled_topics = [self.categorizer.topic_labels.get(topic, f"موضوع {topic}") for topic in topics]
                assigned_topic_probs = [
                    probabilities[i][topic] if topic in probabilities[i] else 0
                    for i, topic in enumerate(topics)
                ]
                df = pd.DataFrame({
                    'Document': self.documents,
                    'Topic': topics,
                    'Topic Label': labeled_topics,
                    'Confidence': assigned_topic_probs
                })

            # مرتب‌سازی و ذخیره نتایج
            df = df.sort_values('Confidence', ascending=False).reset_index(drop=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs(Config.RESULTS_DIR, exist_ok=True)
            output_file = os.path.join(Config.RESULTS_DIR, f'topic_results_{timestamp}.csv')
            df.to_csv(output_file, index=False)
            logger.info(f"نتایج در فایل '{output_file}' ذخیره شد.")

            # گروه‌بندی و نمایش اسناد بر اساس دسته‌ها
            label_column = 'Assigned Label' if 'Assigned Label' in df.columns else 'Topic Label'
            grouped = df.groupby(label_column)
            print("\nنتایج دسته‌بندی اسناد بر اساس دسته‌ها:")
            print("=" * 80)
            for label, group in grouped:
                print(f"\nدسته: {label}")
                print("-" * 40)
                for doc in group['Document']:
                    print(f"- {doc}")

            logger.info("فرآیند یکپارچه با موفقیت پایان یافت.")
            return df

        except Exception as e:
            logger.error(f"خطا در پردازش اسناد: {str(e)}")
            raise
