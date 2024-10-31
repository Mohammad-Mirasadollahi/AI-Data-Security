import logging
from models.topic_modeler import TopicModeler
from models.categorizer import Categorizer
from readers.pdf_document_reader import WordDocumentReader
from summarizers.transformers_summarizer import TransformersSummarizer
from processors.integrated_processor import IntegratedProcessor
from logger import logger
from config import Config

def main():
    pdf_folder_path = './notebooks/word_files/'
    predefined_topics = [
        {'label': 'فناوری'},
        {'label': 'سلامت و سبک زندگی'},
        {'label': 'هنر و سرگرمی'},
        {'label': 'سفر و مکان‌ها'},
        {'label': 'آموزش'}
    ]

    try:
        logger.info("شروع اجرای برنامه مدل‌سازی موضوعات.")
        document_reader = WordDocumentReader()
        logger.info("اجرای تشخیص خودکار موضوعات...")
        topic_modeler_auto = TopicModeler()
        categorizer_auto = Categorizer(topic_modeler_auto)
        auto_processor = IntegratedProcessor(
            topic_modeler=topic_modeler_auto,
            categorizer=categorizer_auto,
            document_reader=document_reader,
            #summarizer=summarizer,
            folder_path=pdf_folder_path
        )
        auto_results = auto_processor.run()
        print(auto_results)
        logger.info("اجرای با موضوعات از پیش تعریف شده...")
        topic_modeler_manual = TopicModeler(predefined_topics=predefined_topics)
        categorizer_manual = Categorizer(topic_modeler_manual)
        manual_processor = IntegratedProcessor(
            topic_modeler=topic_modeler_manual,
            categorizer=categorizer_manual,
            document_reader=document_reader,
            #summarizer=summarizer,
            folder_path=pdf_folder_path,
            predefined_topics=predefined_topics
        )
        manual_results = manual_processor.run()
        logger.info("اجرای با طبقه‌بندی صفر-شات برای برچسب‌گذاری...")
        topic_modeler_zero_shot = TopicModeler()
        categorizer_zero_shot = Categorizer(topic_modeler_zero_shot)
        zero_shot_processor = IntegratedProcessor(
            topic_modeler=topic_modeler_zero_shot,
            categorizer=categorizer_zero_shot,
            document_reader=document_reader,
            #summarizer=summarizer,
            folder_path=pdf_folder_path
        )
        zero_shot_results = zero_shot_processor.run(use_zero_shot=True)

        logger.info("تمامی فرآیندهای مدل‌سازی موضوعات با موفقیت انجام شد.")

    except Exception as e:
        logger.error(f"خطایی در اجرای اصلی رخ داده است: {str(e)}")
        print(f"خطایی رخ داده است. لطفاً فایل لاگ را بررسی کنید: {Config.LOG_DIR}")

if __name__ == "__main__":
    main()
