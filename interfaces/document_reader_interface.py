from abc import ABC, abstractmethod
from typing import List


class IDocumentReader(ABC):

    @abstractmethod
    def read_documents(self, folder_path: str) -> List[str]:
        pass
