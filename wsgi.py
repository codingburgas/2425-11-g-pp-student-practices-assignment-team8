import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from src import create_app
from src.config import Config

app = create_app(Config)
