"""
Testing
"""
import os
import datetime

import unittest

from AWSSignV4.client import Client, get_host


class ClientTest(unittest.TestCase):

    def setUp(self) -> None:
        """Setup all initiale data"""
        self.client = Client(
            aws_region='<AWS Region>',
            aws_service='iotdevicegateway',
            aws_access_key=os.environ.get("aws_access_key"),
            aws_secret_key=os.environ.get("aws_secret_key"),
            date_time=datetime.datetime.now().utcnow()
        )
        self.endpoint = "<Your AWS IoT Core Endpoint>"
        self.client.build_canonical(canonical_uri="/topics/hello", canonical_querystring="qos=1")

    def test_post(self) -> None:
        payload = {"iot": "core"}
        res = self.client.post(self.endpoint, data=payload)
        self.assertEqual(res.status_code, 200)

    def test_get_host(self):
        res = get_host(self.endpoint)
        self.assertEqual(res, "a2qacovkwccbxk-ats.iot.us-east-1.amazonaws.com")
