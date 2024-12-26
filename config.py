# config.py

import os

import yaml
from dotenv import load_dotenv


class Config:
    def __init__(self, config_file: str = 'config.yaml', env_file: str = '.env'):
        # Load environment variables from .env file
        load_dotenv(env_file)

        # Load configurations from config.yaml
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            self.predefined_topics = config.get('predefined_topics', [])
            self.input_folder = config.get('input_folder', 'input_docs')
            self.output_folder = config.get('output_folder', 'output_docs')
            self.log_folder = config.get('log_folder', 'logs')
            self.qdrant_host = config.get('qdrant_host', '127.0.0.1')
            self.qdrant_port = int(config.get('qdrant_port', 6333))

        # Optional: Load Qdrant API key from environment variables
        self.qdrant_api_key = os.getenv('QDRANT_API_KEY', None)
        self.embedding_model = os.getenv('EMBEDDING_MODEL',
                                         'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

    def __repr__(self):
        return (f"Config(qdrant_host={self.qdrant_host}, qdrant_port={self.qdrant_port}, "
                f"embedding_model={self.embedding_model}, predefined_topics={self.predefined_topics}, "
                f"input_folder={self.input_folder}, output_folder={self.output_folder}, "
                f"log_folder={self.log_folder})")
