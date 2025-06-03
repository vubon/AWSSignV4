"""AWS Signature Version 4 Client.
This class provides a client interface to make signed HTTP requests to AWS services
using the AWS Signature Version 4 signing process. It extends the SignV4 class
to handle the specifics of request construction and authorization.
"""
import json
from urllib.parse import urlparse

import requests
from AWSSignV4.signv4 import SignV4


def get_host(url: str) -> str:
    """Extracts the hostname from a given URL.
    :param url: str: The URL from which to extract the hostname.
    :return: str: The hostname (e.g., 'www.example.com').
    """
    parse = urlparse(url)
    return parse.hostname


class Client(SignV4):
    """AWS Signature Version 4 Client.
    This class provides a client interface to make signed HTTP requests to AWS services
    using the AWS Signature Version 4 signing process. It extends the SignV4 class
    to handle the specifics of request construction and authorization.
    """

    def __init__(self, aws_access_key: str, aws_secret_key: str, aws_region: str, aws_service: str, date_time):
        """Initializes the Client with AWS credentials and service information.
        :param aws_access_key: str: The AWS access key ID.
        :param aws_secret_key: str: The AWS secret access key.
        :param aws_region: str: The AWS region for the service (e.g., 'us-east-1').
        :param aws_service: str: The AWS service name (e.g., 's3', 'execute-api').
        :param date_time: datetime: A datetime object representing the current time,
                                    used for generating the signature. Must be UTC.
        """
        super(Client, self).__init__(aws_access_key, aws_secret_key, aws_region, aws_service, date_time)
        self.canonical_uri = None
        self.canonical_querystring = None

    def build_canonical(self, canonical_uri: str, canonical_querystring: str):
        """Sets the canonical URI and query string for subsequent requests.
        These components are part of the AWS Signature Version 4 canonical request.
        Example:
          canonical_uri = "/topics/hello"
          canonical_querystring = "qos=1"
        :param canonical_uri: str: The URI path component of the request.
        :param canonical_querystring: str: The query string component of the request.
                                           Should not include the leading '?'.
        """

        self.canonical_querystring = canonical_querystring
        self.canonical_uri = canonical_uri

    def post(self, url: str, data):
        """Sends a POST request with an AWS Signature Version 4.
        The request body is JSON serialized. The method constructs the necessary
        canonical request components and authorization header.
        :param url: str: The base URL for the request (without canonical URI or query string).
        :param data: dict: The payload to be sent as JSON in the request body.
        :return: requests.Response: The response object from the requests library.
        """
        payload = json.dumps(data)
        request_url = url + self.canonical_uri
        if self.canonical_querystring:
            request_url += "?" + self.canonical_querystring

        canonical = {
            "method": "POST",
            "payload": payload,
            "canonical_uri": self.canonical_uri,
            "canonical_querystring": self.canonical_querystring if self.canonical_querystring else "",
            "headers": {
                "host": get_host(request_url)
            }
        }
        return requests.post(request_url, data=payload, headers=self.authorization_header(**canonical))
