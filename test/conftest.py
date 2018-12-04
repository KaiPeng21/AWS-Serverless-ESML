
import pytest
import sys
import os

import io
import logging
import json

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(TEST_DIR, os.path.join(os.pardir, "src")))
sys.path.insert(0, PROJECT_DIR)

@pytest.fixture
def logger():
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(__name__)

@pytest.fixture
def testfiles_filepath():
    return os.path.dirname(os.path.abspath(__file__)) + "/testfiles/"

@pytest.fixture
def pdf_binary_data():
    filepath = os.path.dirname(os.path.abspath(__file__)) + "/testfiles/test_pdf.pdf"
    with open(filepath, 'rb') as f:
        binary_data = io.BytesIO(f.read())
    return binary_data

@pytest.fixture
def docx_binary_data():
    filepath = os.path.dirname(os.path.abspath(__file__)) + "/testfiles/test_docx.docx"
    with open(filepath, 'rb') as f:
        binary_data = io.BytesIO(f.read())
    return binary_data

@pytest.fixture
def txt_binary_data():
    filepath = os.path.dirname(os.path.abspath(__file__)) + "/testfiles/test_txt.txt"
    with open(filepath, 'rb') as f:
        binary_data = io.BytesIO(f.read())
    return binary_data

@pytest.fixture
def s3_put_event():
    testfiles_filepath = os.path.dirname(os.path.abspath(__file__)) + "/events/"
    with open(testfiles_filepath + "s3_event.json") as f:
        put_event = json.loads(f.read())
    return put_event

@pytest.fixture
def sqs_event():
    testfiles_filepath = os.path.dirname(os.path.abspath(__file__)) + "/events/"
    with open(testfiles_filepath + "sqs_event.json") as f:
        put_event = json.loads(f.read())
    return put_event
