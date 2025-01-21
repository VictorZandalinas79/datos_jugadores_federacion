import os
from dotenv import load_dotenv

def load_config():
    """Load configuration from .env file"""
    load_dotenv()
    return {
        'delay': int(os.getenv('DELAY_BETWEEN_REQUESTS', 1)),
        'output_dir': os.getenv('OUTPUT_DIRECTORY', 'data')
    }

def ensure_output_directory(directory):
    """Ensure the output directory exists"""
    if not os.path.exists(directory):
        os.makedirs(directory)