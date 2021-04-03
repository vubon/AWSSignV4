"""
AWS Request Signater Version 4
@auther: Vubon Roy
"""
import hashlib
import hmac

_AWS_REQUEST = "aws4_request"
_AWS4 = "AWS4"
_AWS_ALGORITHM = "AWS4-HMAC-SHA256"
_DEFAULT_CONTENT_TYPE = "application/x-amz-json-1.0"


class SignV4:
    """
    AWS Request Signature Version 4
    """

    def __init__(self, aws_access_key: str, aws_secret_key: str, aws_region: str, aws_service: str, date_time):
        self._signed_headers = 'content-type;host;x-amz-date'
        self._aws_access_key = aws_access_key
        self._aws_secret_key = aws_secret_key
        self.aws_region = aws_region
        self.aws_service = aws_service
        self.date_stamp = date_time.strftime('%Y%m%d')
        self.amz_date = date_time.strftime('%Y%m%dT%H%M%SZ')

    @staticmethod
    def hash_sha256(message: str) -> str:
        """
        :param message:
        :return:
        """
        return hashlib.sha256(message.encode('utf-8')).hexdigest()

    @staticmethod
    def sign(key: bytes, message: str) -> bytes:
        """
        Signing message with key
        :param key: bytes: Key as bytes
        :param message: str: Client message
        :return: return as bytes
        :rtype: bytes
        """
        return hmac.new(key=key, msg=message.encode('utf-8'), digestmod=hashlib.sha256).digest()

    def get_signature_key(self) -> bytes:
        """
        :return:
        """
        return self.sign(
            key=self.sign(
                key=self.sign(
                    key=self.sign(
                        key=(_AWS4 + self._aws_secret_key).encode('utf-8'), message=self.date_stamp
                    ),
                    message=self.aws_region
                ),
                message=self.aws_service
            ),
            message=_AWS_REQUEST
        )

    def get_canonical_headers(self, headers: dict) -> list:
        """
        :param headers:
        :return:
        """
        content_type = headers.get("content-type", _DEFAULT_CONTENT_TYPE)
        host = headers.get("host")
        return ['content-type:' + content_type + '\n' + 'host:' + host + '\n' + 'x-amz-date:' + self.amz_date + '\n']

    def get_canonical_request(self, **kwargs: dict) -> str:
        """
        :param kwargs:
         canonical = {
            "headers": {
                "content-type": "application/json",
                "host": "hello.com",
                "date": "datetime object UTC format"
            },
            "method": "POST",
            "payload": {"content": "hello world"},
            "canonical_uri": "hello/test",
            "canonical_querystring": "qos=1"
        }
        :return:
        """
        headers = kwargs.pop("headers")
        payload = kwargs.pop("payload")
        payload_hash = [self.hash_sha256(payload)]
        canonical_headers = self.get_canonical_headers(headers)

        _request = []
        for key, value in kwargs.items():
            _request.append(value)

        canonical_request = _request + canonical_headers + [self._signed_headers] + payload_hash
        return "\n".join([str(item) for item in canonical_request])

    def get_credential_scope(self) -> str:
        """
        :return:
        """
        return self.date_stamp + "/" + self.aws_region + "/" + self.aws_service + "/" + _AWS_REQUEST

    def string_to_sign(self, **kwargs) -> str:
        """
        :param kwargs:
        :return:
        """
        credential_scope = self.get_credential_scope()
        canonical_request = self.get_canonical_request(**kwargs)
        return _AWS_ALGORITHM + "\n" + self.amz_date + "\n" + credential_scope + "\n" + self.hash_sha256(
            canonical_request)

    def signature(self, **kwargs):
        """
        :return:
        """
        return hmac.new(self.get_signature_key(), self.string_to_sign(**kwargs).encode('utf-8'),
                        hashlib.sha256).hexdigest()

    def authorization_header(self, **kwargs) -> dict:
        """
        :return:
        """
        credential_scope = self.get_credential_scope()
        first_part = _AWS_ALGORITHM + " " + "Credential=" + self._aws_access_key + "/" + credential_scope
        second_part = ', SignedHeaders=' + self._signed_headers + ", " + 'Signature=' + self.signature(**kwargs)
        return {
            'Content-Type': "application/x-amz-json-1.0",
            'X-Amz-Date': self.amz_date,
            'Authorization': first_part + second_part,
        }
