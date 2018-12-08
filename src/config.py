"""
A module that parses environment variables
"""
import os

ES_HOST = os.getenv("ES_HOST", "http://localhost")
ES_PORT = int(os.getenv("ES_PORT", 9200))

ES_INDEX = os.getenv("ES_INDEX", "filesearch")

AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
