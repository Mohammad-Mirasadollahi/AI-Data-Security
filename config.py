# config.py
import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    MODEL_NAME: str = os.getenv('MODEL_NAME', './models/saved_models')
    LOG_DIR: str = os.getenv('LOG_DIR', 'logs')
    RESULTS_DIR: str = os.getenv('RESULTS_DIR', 'results')
    ZERO_SHOT_MODEL: str = os.getenv('ZERO_SHOT_MODEL', './models/mnli_model')
    SUMMARIZER_MODEL:str=os.getenv('SUMMARIZER_MODEL','')
