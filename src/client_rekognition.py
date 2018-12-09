"""
A module that interfaces with Amazon Rekognition Service
"""
import boto3

rekognition = boto3.client("rekognition")

def detect_labels(s3_tuple : tuple, max_labels : int = 20, min_confidence : float = 0.9) -> list:
    """ Detect image labels given an image file from s3
    
    Arguments:
        s3_tuple {tuple} -- tuple in the form (s3 bucket, s3 object key, file size)
    
    Keyword Arguments:
        max_labels {int} -- maximum number of labels (default: {20})
        min_confidence {float} -- minimum confidence (default: {0.9})
    
    Returns:
        list -- list of labels in the form
        [
            "label 1",
            "label 2",
            "label 3",
            ...
        ]
    """

    response = rekognition.detect_labels(
        Image={
            "S3Object" : {
                "Bucket" : s3_tuple[0],
                "Name" : s3_tuple[1]
            }
        },
        MaxLabels=max_labels,
        MinConfidence=min_confidence
    )
    labels = [label["Name"] for label in response["Labels"]]
    return labels

def detect_text(s3_tuple : tuple, min_confidence : float = 0.9) -> list:
    """ Detect text in images given an image file from s3
    
    Arguments:
        s3_tuple {tuple} -- tuple in the form (s3 bucket, s3 object key, file size)
    
    Keyword Arguments:
        min_confidence {float} -- minimum confidence (default: {0.9})
    
    Returns:
        list -- list of text in the form
        [
            "text1",
            "text2",
            "text3",
            ...
        ]
    """

    response = rekognition.detect_text(
        Image={
            "S3Object" : {
                "Bucket" : s3_tuple[0],
                "Name" : s3_tuple[1]
            }
        }
    )
    text_list = [text["DetectedText"] for text in response["TextDetections"] if text["Confidence"] >= min_confidence]
    return text_list

def recognize_celebrities(s3_tuple : tuple, min_confidence : float = 0.9) -> list:
    """ Recognize celebrities in the image
    
    Arguments:
        s3_tuple {tuple} -- tuple in the form (s3 bucket, s3 object key, file size)
    
    Keyword Arguments:
        min_confidence {float} -- minimum confidence (default: {0.9})
    
    Returns:
        list -- list of celebrity names in the form
        [
            "celebrity name",
            "celebrity name",
            "celebrity name",
            ...
        ]
    """

    response = rekognition.recognize_celebrities(
        Image={
            "S3Object" : {
                "Bucket" : s3_tuple[0],
                "Name" : s3_tuple[1]
            }
        }
    )
    celebrities = [celebrity["Name"] for celebrity in response["CelebrityFaces"] if celebrity["MatchConfidence"] >= min_confidence]
    return celebrities
