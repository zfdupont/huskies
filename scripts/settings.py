import os
from os.path import join, dirname

DATABASE_URI = os.environ.get("DATABASE_URI")
HUSKIES_HOME = os.environ.get("HUSKIES_HOME")
TOTAL_PLANS = int(os.environ.get("TOTAL_PLANS"))
RECOM_STEPS = int(os.environ.get("RECOM_STEPS"))