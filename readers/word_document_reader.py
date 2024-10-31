# readers/word_document_reader.py
import logging
import os
from typing import List

from docx import Document

from interfaces.document_reader_interface import IDocumentReader

# interfaces/document_reader_interface.py

logger = logging.getLogger(__name__)


class WordDocumentReader(IDocumentReader):

    def read_documents(self, folder_path: str) -> List[str]:

        logger.info(f"شروع خواندن فایل‌های Word از فولدر: {folder_path}")
        documents = []
        try:
            for filename in os.listdir(folder_path):
                if filename.lower().endswith('.docx'):
                    file_path = os.path.join(folder_path, filename)
                    logger.info(f"خواندن فایل: {file_path}")
                    try:
                        doc = Document(file_path)
                        text = ''
                        for paragraph in doc.paragraphs:
                            text += paragraph.text + ' '
                        if text.strip():
                            documents.append(text.strip())
                            logger.info(f"متن فایل '{filename}' با موفقیت استخراج شد.")
                        else:
                            logger.warning(f"هیچ متنی از فایل '{filename}' استخراج نشد.")
                    except Exception as e:
                        logger.error(f"خطا در خواندن فایل '{filename}': {str(e)}")
            logger.info("تمامی فایل‌های Word با موفقیت خوانده شدند.")
        except Exception as e:
            logger.error(f"خطا در خواندن فایل‌های Word: {str(e)}")
            raise
        return documents
