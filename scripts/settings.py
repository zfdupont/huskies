import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

DATABASE_URI = os.environ.get("DATABASE_URI")
HUSKIES_HOME = os.environ.get("HUSKIES_HOME")