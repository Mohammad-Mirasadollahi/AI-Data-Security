import datetime
import os

import pandas as pd
import streamlit as st

from config import Config
from logger import logger
from models.categorizer import Categorizer
from models.topic_modeler import TopicModeler
from processors.integrated_processor import IntegratedProcessor
from readers.word_document_reader import WordDocumentReader


def process_documents(folder_path, predefined_topics):
    try:
        logger.info("شروع اجرای برنامه مدل‌سازی موضوعات.")
        document_reader = WordDocumentReader()

        logger.info("اجرای با موضوعات از پیش تعریف شده...")
        topic_modeler_manual = TopicModeler(predefined_topics=predefined_topics)
        categorizer_manual = Categorizer(topic_modeler_manual)
        manual_processor = IntegratedProcessor(
            topic_modeler=topic_modeler_manual,
            categorizer=categorizer_manual,
            document_reader=document_reader,
            folder_path=folder_path,
            predefined_topics=predefined_topics
        )
        manual_results = manual_processor.run()

        logger.info("تمامی فرآیندهای مدل‌سازی موضوعات با موفقیت انجام شد.")

        # Combine results
        combined_df = pd.concat([manual_results], ignore_index=True)

        if 'Topic Label' in combined_df.columns and 'Assigned Label' not in combined_df.columns:
            combined_df.rename(columns={'Topic Label': 'Assigned Label'}, inplace=True)

        combined_df = combined_df.sort_values('Confidence', ascending=False).reset_index(drop=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs(Config.RESULTS_DIR, exist_ok=True)
        output_file = os.path.join(Config.RESULTS_DIR, f'topic_results_{timestamp}.csv')
        combined_df.to_csv(output_file, index=False)
        logger.info(f"نتایج در فایل '{output_file}' ذخیره شد.")

        label_column = 'Assigned Label' if 'Assigned Label' in combined_df.columns else 'Topic Label'
        grouped = combined_df.groupby(label_column)
        grouped_data = {label: group['Document'].tolist() for label, group in grouped}

        results = {

            "manual": manual_results,

            "combined_df": combined_df,
            "output_file": output_file,
            "grouped_data": grouped_data
        }

        return results

    except Exception as e:
        logger.error(f"خطایی در اجرای اصلی رخ داده است: {str(e)}")
        st.error(f"خطایی رخ داده است. لطفاً فایل لاگ را بررسی کنید: {Config.LOG_DIR}")
        return None


def main():
    st.set_page_config(page_title="سیستم مدل‌سازی موضوعات", layout="wide")
    st.title("سیستم مدل‌سازی موضوعات برای فایل‌های PDF و Word")

    st.subheader("تعریف موضوعات از پیش تعریف شده")
    st.write("هر موضوع را در یک خط جداگانه وارد کنید.")
    predefined_topics_input = st.text_area(
        "موضوعات از پیش تعریف شده (هر خط یک موضوع)",
        value="فناوری\nسلامت و سبک زندگی\nهنر و سرگرمی\nسفر و مکان‌ها\nآموزش"
    )
    predefined_topics = [{'label': topic.strip()} for topic in predefined_topics_input.split('\n') if topic.strip()]
    folder_path = './notebooks/word_files/'
    if st.button("پردازش فایل‌ها"):
        if os.path.exists(folder_path):
            with st.spinner("در حال پردازش فایل‌ها..."):
                results = process_documents(folder_path, predefined_topics)
            if results:
                st.success("مدل‌سازی موضوعات با موفقیت انجام شد.")

                st.subheader("نتایج مدل‌سازی موضوعات")
                st.dataframe(results['combined_df'])

                with open(results['output_file'], "rb") as file:
                    btn = st.download_button(
                        label="دانلود نتایج به صورت CSV",
                        data=file,
                        file_name=os.path.basename(results['output_file']),
                        mime="text/csv"
                    )

                st.subheader("نتایج دسته‌بندی اسناد بر اساس دسته‌ها")
                for label, documents in results['grouped_data'].items():
                    with st.expander(f"دسته: {label}"):
                        for doc in documents:
                            st.write(f"- {doc}")
            else:
                st.error("خطایی در پردازش فایل‌ها رخ داده است.")
        else:
            st.error("مسیر پوشه مشخص شده وجود ندارد. لطفاً مسیر معتبر وارد کنید.")


if __name__ == "__main__":
    main()
