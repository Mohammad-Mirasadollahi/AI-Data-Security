from abc import ABC, abstractmethod
from typing import List, Dict, Tuple

import numpy as np


class ICategorizer(ABC):
    @abstractmethod
    def assign_automatic_labels(self):
        pass

    @abstractmethod
    def assign_predefined_labels(self, embeddings: np.ndarray, predefined_topics: List[Dict]) -> Tuple[
        List[str], List[float]]:
        pass
