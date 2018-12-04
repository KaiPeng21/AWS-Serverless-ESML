"""
A module that parses environment variables
"""
import os

ES_HOST = os.getenv("ES_HOST", "localhost")
ES_PORT = int(os.getenv("ES_PORT", 9200))

ES_INDEX = os.getenv("ES_INDEX", "filesearch")
ES_BATCH_SIZE = os.getenv("ES_BATCH_SIZE", 5242800)

AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
