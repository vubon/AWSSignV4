"""
Testing
"""
import os
import datetime
import unittest
from unittest.mock import patch, MagicMock

from AWSSignV4.client import Client, get_host
from AWSSignV4.signv4 import SignV4, _DEFAULT_CONTENT_TYPE


class ClientTest(unittest.TestCase):

    def setUp(self) -> None:
        """Setup all initiale data"""
        # Using dummy values for credentials and endpoint for most unit tests
        self.dummy_access_key = "test_access_key"
        self.dummy_secret_key = "test_secret_key"
        self.dummy_region = "us-east-1"
        self.dummy_service = "test_service"
        self.dt_now = datetime.datetime(2024, 7, 15, 12, 0, 0, tzinfo=datetime.timezone.utc) # Use a fixed datetime

        self.client = Client(
            aws_access_key=self.dummy_access_key,
            aws_secret_key=self.dummy_secret_key,
            aws_region=self.dummy_region,
            aws_service=self.dummy_service,
            date_time=self.dt_now
        )
        # A generic endpoint for testing URL construction
        self.base_endpoint = "https://example.com"
        # self.client.build_canonical(canonical_uri="/topics/hello", canonical_querystring="qos=1")

    # Commenting out the original test_post as it makes a real network call.
    # def test_post(self) -> None:
    #     payload = {"iot": "core"}
    #     # This test requires actual credentials and endpoint configured.
    #     # For CI/CD or local testing without live AWS, this will fail or needs to be skipped.
    #     # Consider using environment variables to enable/disable this test.
    #     if os.environ.get("RUN_INTEGRATION_TESTS"):
    #         self.client_live = Client(
    #             aws_region=os.environ.get("AWS_REGION_LIVE", '<AWS Region>'),
    #             aws_service=os.environ.get("AWS_SERVICE_LIVE", 'iotdevicegateway'),
    #             aws_access_key=os.environ.get("aws_access_key"),
    #             aws_secret_key=os.environ.get("aws_secret_key"),
    #             date_time=datetime.datetime.now(datetime.timezone.utc)
    #         )
    #         live_endpoint = os.environ.get("AWS_ENDPOINT_LIVE", "<Your AWS IoT Core Endpoint>")
    #         self.client_live.build_canonical(canonical_uri="/topics/hello", canonical_querystring="qos=1")
    #         res = self.client_live.post(live_endpoint, data=payload)
    #         self.assertEqual(res.status_code, 200)
    #     else:
    #         self.skipTest("Skipping integration test_post as RUN_INTEGRATION_TESTS is not set.")


    def test_get_host(self):
        # Original test used a specific endpoint, let's make it more generic
        # or test with various URL formats if necessary.
        res = get_host("https://a2qacovkwccbxk-ats.iot.us-east-1.amazonaws.com/some/path")
        self.assertEqual(res, "a2qacovkwccbxk-ats.iot.us-east-1.amazonaws.com")
        res_no_path = get_host("http://example.com")
        self.assertEqual(res_no_path, "example.com")

    @patch('requests.post')
    @patch.object(SignV4, 'authorization_header', return_value={"Authorization": "dummy_auth_header"})
    def test_post_url_construction_with_querystring(self, mock_auth_header, mock_requests_post):
        self.client.build_canonical(canonical_uri="/test/path", canonical_querystring="key=value")
        self.client.post(self.base_endpoint, data={"test": "data"})

        mock_requests_post.assert_called_once()
        args, kwargs = mock_requests_post.call_args
        self.assertEqual(args[0], "https://example.com/test/path?key=value")

        # Check what's passed to authorization_header
        mock_auth_header.assert_called_once()
        auth_args, auth_kwargs = mock_auth_header.call_args_list[0] # call_args is a tuple (args, kwargs)
        self.assertEqual(auth_kwargs['canonical_querystring'], "key=value")


    @patch('requests.post')
    @patch.object(SignV4, 'authorization_header', return_value={"Authorization": "dummy_auth_header"})
    def test_post_url_construction_empty_querystring(self, mock_auth_header, mock_requests_post):
        self.client.build_canonical(canonical_uri="/test/path", canonical_querystring="")
        self.client.post(self.base_endpoint, data={"test": "data"})

        mock_requests_post.assert_called_once()
        args, kwargs = mock_requests_post.call_args
        self.assertEqual(args[0], "https://example.com/test/path")

        mock_auth_header.assert_called_once()
        auth_args, auth_kwargs = mock_auth_header.call_args_list[0]
        self.assertEqual(auth_kwargs['canonical_querystring'], "")

    @patch('requests.post')
    @patch.object(SignV4, 'authorization_header', return_value={"Authorization": "dummy_auth_header"})
    def test_post_url_construction_none_querystring(self, mock_auth_header, mock_requests_post):
        self.client.build_canonical(canonical_uri="/test/path", canonical_querystring=None)
        self.client.post(self.base_endpoint, data={"test": "data"})

        mock_requests_post.assert_called_once()
        args, kwargs = mock_requests_post.call_args
        self.assertEqual(args[0], "https://example.com/test/path")

        mock_auth_header.assert_called_once()
        auth_args, auth_kwargs = mock_auth_header.call_args_list[0]
        # Ensure canonical_querystring passed to SignV4 is "" if original was None
        self.assertEqual(auth_kwargs['canonical_querystring'], "")


class SignV4Test(unittest.TestCase):
    def setUp(self):
        self.dt = datetime.datetime(2024, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
        self.signer = SignV4("test_akid", "test_secret", "us-east-1", "test_service", self.dt)

    def test_get_canonical_request_post_with_qs(self):
        kwargs = {
            "method": "POST",
            "canonical_uri": "/test/path",
            "canonical_querystring": "param1=val1&param2=val2",
            "headers": {"host": "example.com", "content-type": "application/json"},
            "payload": "{'key':'value'}"
        }

        # Mock get_canonical_headers for predictable output within this test unit
        # This ensures the test for get_canonical_request focuses on its own logic
        expected_amz_date = self.dt.strftime('%Y%m%dT%H%M%SZ')
        self.signer.get_canonical_headers = MagicMock(return_value=[
            f"content-type:application/json\n",
            f"host:example.com\n",
            f"x-amz-date:{expected_amz_date}\n"
        ])

        expected_payload_hash = self.signer.hash_sha256("{'key':'value'}")
        # Note: get_canonical_headers returns a list, which is then "".join()ed by get_canonical_request
        # So, canonical_headers_string will have each header followed by \n
        expected_canonical_headers_str = (
            "content-type:application/json\n"
            "host:example.com\n"
            f"x-amz-date:{expected_amz_date}\n"
        )

        expected_request = (
            "POST\n"
            "/test/path\n"
            "param1=val1&param2=val2\n"
            f"{expected_canonical_headers_str}" # This string already includes the trailing newline from the last header.
            "content-type;host;x-amz-date\n"
            f"{expected_payload_hash}"
        )
        self.assertEqual(self.signer.get_canonical_request(**kwargs), expected_request)

    def test_get_canonical_request_get_no_qs(self):
        kwargs = {
            "method": "GET",
            "canonical_uri": "/another/path",
            "canonical_querystring": "", # Empty query string
            "headers": {"host": "myhost.com"}, # No content-type, should use default
            "payload": "" # Empty payload for GET
        }

        expected_amz_date = self.dt.strftime('%Y%m%dT%H%M%SZ')
        # Simulate get_canonical_headers, note _DEFAULT_CONTENT_TYPE should be used
        self.signer.get_canonical_headers = MagicMock(return_value=[
            f"content-type:{_DEFAULT_CONTENT_TYPE}\n",
            f"host:myhost.com\n",
            f"x-amz-date:{expected_amz_date}\n"
        ])

        expected_payload_hash = self.signer.hash_sha256("")
        expected_canonical_headers_str = (
            f"content-type:{_DEFAULT_CONTENT_TYPE}\n"
            "host:myhost.com\n"
            f"x-amz-date:{expected_amz_date}\n"
        )
        expected_request = (
            "GET\n"
            "/another/path\n"
            "\n" # Empty query string
            f"{expected_canonical_headers_str}"
            "content-type;host;x-amz-date\n"
            f"{expected_payload_hash}"
        )
        self.assertEqual(self.signer.get_canonical_request(**kwargs), expected_request)

    def test_authorization_header_content_type(self):
        # Mock methods called by authorization_header to isolate its logic
        self.signer.get_credential_scope = MagicMock(return_value="scope_string")
        self.signer.signature = MagicMock(return_value="test_signature")

        headers = self.signer.authorization_header(
            method="POST", # Dummy kwargs for signature and underlying calls
            canonical_uri="/",
            canonical_querystring="",
            headers={"host":"example.com"},
            payload="{}"
        )
        self.assertIn('Content-Type', headers)
        self.assertEqual(headers['Content-Type'], _DEFAULT_CONTENT_TYPE)

if __name__ == '__main__':
    unittest.main()
