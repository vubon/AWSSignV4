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
        """Initializes the SignV4 class with AWS credentials and service information.
        :param aws_access_key: str: The AWS access key ID.
        :param aws_secret_key: str: The AWS secret access key.
        :param aws_region: str: The AWS region for the service (e.g., 'us-east-1').
        :param aws_service: str: The AWS service name (e.g., 's3', 'execute-api').
        :param date_time: datetime: A datetime object representing the current time,
                                    used for generating timestamps in the signature. Must be UTC.
        """
        self._signed_headers = 'content-type;host;x-amz-date'
        self._aws_access_key = aws_access_key
        self._aws_secret_key = aws_secret_key
        self.aws_region = aws_region
        self.aws_service = aws_service
        self.date_stamp = date_time.strftime('%Y%m%d')
        self.amz_date = date_time.strftime('%Y%m%dT%H%M%SZ')

    @staticmethod
    def hash_sha256(message: str) -> str:
        """Computes the SHA256 hash of a given string.
        :param message: str: The string to hash.
        :return: str: The hex-encoded SHA256 hash of the message.
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
        """Derives the AWS Signature Version 4 signing key.
        The key is derived from the AWS secret access key and scoped to the date,
        region, and service. This key is used to sign the 'string to sign'.
        :return: bytes: The derived signing key.
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
        """Constructs the canonical headers string.
        Only 'content-type', 'host', and 'x-amz-date' headers are included.
        Headers are lowercased, and their values are trimmed.
        :param headers: dict: A dictionary containing request headers. Expected keys
                              are "host" and optionally "content-type".
        :return: list: A list of strings, where each string is a canonical header
                       entry in the format 'header_name:header_value\n'.
                       Example: ['content-type:application/json\n', 'host:example.com\n', ...]
        """
        content_type = headers.get("content-type", _DEFAULT_CONTENT_TYPE)
        host = headers.get("host")
        return [
            f'content-type:{content_type}\n',
            f'host:{host}\n',
            f'x-amz-date:{self.amz_date}\n'
        ]

    def get_canonical_request(self, **kwargs: dict) -> str:
        """Creates the canonical request string as per AWS Signature Version 4.
        The canonical request is a standardized representation of the request
        components, which is then hashed and included in the 'string to sign'.
        :param kwargs: dict: Keyword arguments containing the components of the request:
            - "method": str: The HTTP method (e.g., "POST", "GET").
            - "canonical_uri": str: The URI-encoded version of the absolute path component of the URI.
            - "canonical_querystring": str: The URL-encoded query string parameters.
            - "headers": dict: Request headers, must include "host" and optionally "content-type".
            - "payload": str: The payload of the request body. For GET, this is an empty string.
        :return: str: The canonical request string.
        """
        headers = kwargs.pop("headers")
        payload = kwargs.pop("payload")

        method = kwargs["method"]
        uri = kwargs["canonical_uri"]
        qs = kwargs["canonical_querystring"]

        # canonical_headers_string is 'h1:v1\nh2:v2\n...\n'
        canonical_headers_string = "".join(self.get_canonical_headers(headers))

        signed_headers_str = self._signed_headers
        payload_hash_str = self.hash_sha256(payload)

        return f"{method}\n{uri}\n{qs}\n{canonical_headers_string}{signed_headers_str}\n{payload_hash_str}"

    def get_credential_scope(self) -> str:
        """Generates the credential scope string.
        The credential scope limits the validity of the signature to a specific date,
        region, and service.
        Format: YYYYMMDD/region/service/aws4_request
        :return: str: The credential scope string.
        """
        return f"{self.date_stamp}/{self.aws_region}/{self.aws_service}/{_AWS_REQUEST}"

    def string_to_sign(self, **kwargs) -> str:
        """Creates the 'string to sign' for AWS Signature Version 4.
        This string includes the algorithm, request timestamp, credential scope,
        and a hash of the canonical request.
        :param kwargs: dict: Arguments passed to `get_canonical_request` to generate
                             the canonical request hash.
        :return: str: The complete string to be signed.
        """
        credential_scope = self.get_credential_scope()
        canonical_request = self.get_canonical_request(**kwargs)
        return f"{_AWS_ALGORITHM}\n{self.amz_date}\n{credential_scope}\n{self.hash_sha256(canonical_request)}"

    def signature(self, **kwargs):
        """Computes the AWS Signature Version 4.
        The signature is calculated by signing the 'string to sign' with the derived
        signing key using HMAC-SHA256.
        :param kwargs: dict: Arguments passed to `string_to_sign`.
        :return: str: The hex-encoded signature.
        """
        return hmac.new(self.get_signature_key(), self.string_to_sign(**kwargs).encode('utf-8'),
                        hashlib.sha256).hexdigest()

    def authorization_header(self, **kwargs) -> dict:
        """Constructs the HTTP Authorization header string for AWS Signature Version 4.
        This header contains the access key, credential scope, signed headers, and the signature.
        :param kwargs: dict: Arguments passed to `signature` to compute the signature.
        :return: dict: A dictionary containing the 'Content-Type', 'X-Amz-Date',
                       and 'Authorization' headers.
        """
        credential_scope = self.get_credential_scope()
        credential_part = f"{self._aws_access_key}/{credential_scope}"
        authorization_string = (
            f"{_AWS_ALGORITHM} Credential={credential_part}, "
            f"SignedHeaders={self._signed_headers}, "
            f"Signature={self.signature(**kwargs)}"
        )
        return {
            'Content-Type': _DEFAULT_CONTENT_TYPE,
            'X-Amz-Date': self.amz_date,
            'Authorization': authorization_string,
        }
