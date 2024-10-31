# tests/test_transformers_summarizer.py
import unittest

from summarizers.transformers_summarizer import TransformersSummarizer


class TestTransformersSummarizer(unittest.TestCase):

    def setUp(self):
        # استفاده از یک مدل خلاصه‌سازی کوچک برای تست
        self.summarizer = TransformersSummarizer(model_name="facebook/bart-large-cnn")
        self.texts = [
            "این یک متن طولانی برای تست خلاصه‌سازی است. هدف ما اطمینان از صحت عملکرد خلاصه‌ساز است.",
            "پایتون یک زبان برنامه‌نویسی قدرتمند و منعطف است که در زمینه‌های مختلفی مورد استفاده قرار می‌گیرد."
        ]

    def test_summarize(self):
        summaries = self.summarizer.summarize(self.texts)
        self.assertEqual(len(summaries), len(self.texts))
        for summary, original in zip(summaries, self.texts):
            self.assertTrue(len(summary) < len(original))
            self.assertIsInstance(summary, str)

    def test_summarize_empty_text(self):
        summaries = self.summarizer.summarize([""])
        self.assertEqual(len(summaries), 1)
        self.assertEqual(summaries[0], "")


if __name__ == '__main__':
    unittest.main()
