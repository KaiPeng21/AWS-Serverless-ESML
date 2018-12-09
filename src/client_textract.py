# TODO: replace fileprocess module with Amazon Textract once the service become available
# Getting really excited about the new features in Reinvent 2018!!!

# import boto3
# import io

# textract = boto3.client('textract')
# s3 = boto3.client('s3')

# def get_file_stream_in_s3(bucket : str, key : str) -> io.BytesIO:
#     """Extract binary data from file in an S3 bucket
    
#     Arguments:
#         bucket {str} -- S3 Bucket Name
#         key {str} -- File Key
    
#     Returns:
#         io.BytesIO -- file stream
#     """

#     try:
#         response = s3.get_object(Bucket=bucket, Key=key)
#         s3_file_content = response['Body'].read()
#         return io.BytesIO(s3_file_content)
#     except Exception as e:
#         print(f"Unable to read from bucket and {bucket} key {key}")
#         print(e)
#         raise e

# def test(bucket : str, document : str):
#     response = textract.detect_document_text(
#         Document={'S3Object' : {'Bucket' : bucket, 'Name' : document}}
#     )

#     print('response')
#     print(response)
#     print()

#     blocks = response["Blocks"]


# if __name__ == "__main__":
#     pass


