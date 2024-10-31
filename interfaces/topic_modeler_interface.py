from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple

import numpy as np
import pandas as pd


class ITopicModeler(ABC):
    @abstractmethod
    def fit_transform(self, documents: List[str]) -> Tuple[List[int], np.ndarray, np.ndarray]:
        pass

    @abstractmethod
    def get_topic_info(self) -> Optional[pd.DataFrame]:
        pass

    @abstractmethod
    def get_topics(self) -> Optional[Dict[int, List[tuple]]]:
        pass
