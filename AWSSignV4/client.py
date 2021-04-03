"""AWS Signature Version 4 Cleint"""
import json
from urllib.parse import urlparse

import requests
from AWSSignV4.signv4 import SignV4


def get_host(url: str) -> str:
    """
    :param url:
    :return:
    """
    parse = urlparse(url)
    return parse.hostname


class Client(SignV4):
    """
    Cleint layer
    """

    def __init__(self, aws_access_key: str, aws_secret_key: str, aws_region: str, aws_service: str, date_time):
        super(Client, self).__init__(aws_access_key, aws_secret_key, aws_region, aws_service, date_time)
        self.canonical_uri = None
        self.canonical_querystring = None

    def build_canonical(self, canonical_uri: str, canonical_querystring: str):
        """
         # "canonical_uri": "/topics/hello",
        # "canonical_querystring": "qos=1"
        :return:
        """

        self.canonical_querystring = canonical_querystring
        self.canonical_uri = canonical_uri

    def post(self, url: str, data):
        """
        :return:
        """
        payload = json.dumps(data)
        url += self.canonical_uri + ("?" + self.canonical_querystring) if self.canonical_querystring else None
        canonical = {
            "headers": {
                "host": get_host(url)
            },
            "method": "POST",
            "payload": payload,
        }
        canonical.update(
            {"canonical_uri": self.canonical_uri, "canonical_querystring": self.canonical_querystring})
        return requests.post(url, data=payload, headers=self.authorization_header(**canonical))
