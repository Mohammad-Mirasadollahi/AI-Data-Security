# interfaces/summarizer_interface.py
from abc import ABC, abstractmethod
from typing import List


class ISummarizer(ABC):
    @abstractmethod
    def summarize(self, texts: List[str]) -> List[str]:
        pass
