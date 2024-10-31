 #readers/pdf_document_reader.py
import logging
import os
from typing import List

import pdfplumber

from interfaces.document_reader_interface import IDocumentReader

logger = logging.getLogger(__name__)


class PDFDocumentReader(IDocumentReader):

    def read_documents(self, folder_path: str) -> List[str]:

        logger.info(f"شروع خواندن فایل‌های PDF از فولدر: {folder_path}")
        documents = []
        try:
            for filename in os.listdir(folder_path):
                if filename.lower().endswith('.pdf'):
                    file_path = os.path.join(folder_path, filename)
                    logger.info(f"خواندن فایل: {file_path}")
                    with pdfplumber.open(file_path) as pdf:
                        text = ''
                        for page in pdf.pages:
                            extracted_text = page.extract_text()
                            if extracted_text:
                                text += extracted_text + ' '
                        if text.strip():
                            documents.append(text.strip())
                            logger.info(f"متن فایل '{filename}' با موفقیت استخراج شد.")
                        else:
                            logger.warning(f"هیچ متنی از فایل '{filename}' استخراج نشد.")
            logger.info("تمامی فایل‌های PDF با موفقیت خوانده شدند.")
        except Exception as e:
            logger.error(f"خطا در خواندن فایل‌های PDF: {str(e)}")
            raise
        return documents
