from fileprocess import *

def test_get_pdf_text_from_path(logger, testfiles_filepath):
    expected_text = "This is a dummy PDF"
    text = get_pdf_text_from_path(testfiles_filepath + "test_pdf.pdf")
    assert text == expected_text

# def test_get_docx_text_from_path(logger, testfiles_filepath):
#     expected_text = "This is a dummy word document."
#     text = get_docx_text_from_path(testfiles_filepath + "test_docx.docx")
#     assert text == expected_text

def test_get_txt_text_from_path(logger, testfiles_filepath):
    expected_text = "This is a dummy txt file."
    text = get_txt_text_from_path(testfiles_filepath + "test_txt.txt")
    assert text == expected_text  

def test_get_file_text_from_path(logger, testfiles_filepath):
    expected_text = "This is a dummy PDF"
    text = get_file_text_from_path(testfiles_filepath + "test_pdf.pdf")
    assert text == expected_text 
    
    # expected_text = "This is a dummy word document."
    # text = get_file_text_from_path(testfiles_filepath + "test_docx.docx")
    # assert text == expected_text 
    
    expected_text = "This is a dummy txt file."
    text = get_file_text_from_path(testfiles_filepath + "test_txt.txt")
    assert text == expected_text

def test_get_pdf_text_binary_data(logger, pdf_binary_data):
    expected_text = "This is a dummy PDF"
    text = get_pdf_text_from_binary_data(pdf_binary_data)
    assert text == expected_text  

# def test_get_docx_text_binary_data(logger, docx_binary_data):
#     expected_text = "This is a dummy word document."
#     text = get_docx_text_from_binary_data(docx_binary_data)
#     assert text == expected_text  

def test_get_txt_text_binary_data(logger, txt_binary_data):
    expected_text = "This is a dummy txt file."
    text = get_txt_text_from_binary_data(txt_binary_data)
    assert text == expected_text  