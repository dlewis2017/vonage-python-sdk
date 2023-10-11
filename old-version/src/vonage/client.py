import vonage
from vonage_jwt.jwt import JwtClient

from .account import Account
from .application import Application
from .errors import *
from .meetings import Meetings
from .messages import Messages
from .number_insight import NumberInsight
from .number_management import Numbers
from .proactive_connect import ProactiveConnect
from .short_codes import ShortCodes
from .sms import Sms
from .subaccounts import Subaccounts
from .users import Users
from .ussd import Ussd
from .video import Video
from .voice import Voice
from .verify import Verify
from .verify2 import Verify2

import logging
from platform import python_version

import base64
import hashlib
import hmac
import time

from requests import Response
from requests.adapters import HTTPAdapter
from requests.sessions import Session

string_types = (str, bytes)

try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

logger = logging.getLogger("vonage")


class Client:
    """
    Create a Client object to start making calls to Vonage/Nexmo APIs.

    The credentials you provide when instantiating a Client determine which
    methods can be called. Consult the `Vonage API docs <https://developer.vonage.com/concepts/guides/authentication/>`
    for details of the authentication used by the APIs you wish to use, and instantiate your
    client with the appropriate credentials.

    :param str key: Your Vonage API key
    :param str secret: Your Vonage API secret.
    :param str signature_secret: Your Vonage API signature secret.
        You may need to have this enabled by Vonage support. It is only used for SMS authentication.
    :param str signature_method:
        The encryption method used for signature encryption. This must match the method
        configured in the Vonage Dashboard. We recommend `sha256` or `sha512`.
        This should be one of `md5`, `sha1`, `sha256`, or `sha512` if using HMAC digests.
        If you want to use a simple MD5 hash, leave this as `None`.
    :param str application_id: Your application ID if calling methods which use JWT authentication.
    :param str private_key: Your private key, for calling methods which use JWT authentication.
        This should either be a str containing the key in its PEM form, or a path to a private key file.
    :param str app_name: This optional value is added to the user-agent header
        provided by this library and can be used to track your app statistics.
    :param str app_version: This optional value is added to the user-agent header
        provided by this library and can be used to track your app statistics.
    :param timeout: (optional) How many seconds to wait for the server to send data
        before giving up, as a float, or a (connect timeout, read
        timeout) tuple. If set this timeout is used for every call to the Vonage enpoints
    :type timeout: float or tuple
    """

    def __init__(
        self,
        key=None,
        secret=None,
        signature_secret=None,
        signature_method=None,
        application_id=None,
        private_key=None,
        app_name=None,
        app_version=None,
        timeout=None,
        pool_connections=10,
        pool_maxsize=10,
        max_retries=3,
    ):
        self.api_key = key
        self.api_secret = secret

        self.signature_secret = signature_secret
        self.signature_method = signature_method

        self.application_id = application_id

        if self.signature_method in {
            "md5",
            "sha1",
            "sha256",
            "sha512",
        }:
            self.signature_method = getattr(hashlib, signature_method)

        if private_key is not None and application_id is not None:
            self._jwt_client = JwtClient(application_id, private_key)

        self._jwt_claims = {}
        self._host = "rest.nexmo.com"
        self._api_host = "api.nexmo.com"
        self._video_host = "video.api.vonage.com"
        self._meetings_api_host = "api-eu.vonage.com/v1/meetings"
        self._proactive_connect_host = "api-eu.vonage.com"

        user_agent = f"vonage-python/{vonage.__version__} python/{python_version()}"

        if app_name and app_version:
            user_agent += f" {app_name}/{app_version}"

        self.headers = {
            "User-Agent": user_agent,
            "Accept": "application/json",
        }

        self.account = Account(self)
        self.application = Application(self)
        self.meetings = Meetings(self)
        self.messages = Messages(self)
        self.number_insight = NumberInsight(self)
        self.numbers = Numbers(self)
        self.proactive_connect = ProactiveConnect(self)
        self.short_codes = ShortCodes(self)
        self.sms = Sms(self)
        self.subaccounts = Subaccounts(self)
        self.users = Users(self)
        self.ussd = Ussd(self)
        self.video = Video(self)
        self.verify = Verify(self)
        self.verify2 = Verify2(self)
        self.voice = Voice(self)

        self.timeout = timeout
        self.session = Session()
        self.adapter = HTTPAdapter(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=max_retries,
        )
        self.session.mount("https://", self.adapter)

    # Gets and sets _host attribute
    def host(self, value=None):
        if value is None:
            return self._host
        else:
            self._host = value

    # Gets and sets _api_host attribute
    def api_host(self, value=None):
        if value is None:
            return self._api_host
        else:
            self._api_host = value

    def video_host(self, value=None):
        if value is None:
            return self._video_host
        else:
            self._video_host = value

    # Gets and sets _meetings_api_host attribute
    def meetings_api_host(self, value=None):
        if value is None:
            return self._meetings_api_host
        else:
            self._meetings_api_host = value

    def proactive_connect_host(self, value=None):
        if value is None:
            return self._proactive_connect_host
        else:
            self._proactive_connect_host = value

    def auth(self, params=None, **kwargs):
        self._jwt_claims = params or kwargs

    def check_signature(self, params):
        params = dict(params)
        signature = params.pop("sig", "").lower()
        return hmac.compare_digest(signature, self.signature(params))

    def signature(self, params):
        if self.signature_method:
            hasher = hmac.new(
                self.signature_secret.encode(),
                digestmod=self.signature_method,
            )
        else:
            hasher = hashlib.md5()

        # Add timestamp if not already present
        if not params.get("timestamp"):
            params["timestamp"] = int(time.time())

        for key in sorted(params):
            value = params[key]

            if isinstance(value, str):
                value = value.replace("&", "_").replace("=", "_")

            hasher.update(f"&{key}={value}".encode("utf-8"))

        if self.signature_method is None:
            hasher.update(self.signature_secret.encode())

        return hasher.hexdigest()

    def get(self, host, request_uri, params={}, auth_type=None, sent_data_type='json'):
        return self.send_request('GET', host, request_uri, params, auth_type, sent_data_type)

    def post(
        self,
        host,
        request_uri,
        params=None,
        auth_type=None,
        sent_data_type='json',
        supports_signature_auth=False,
    ):
        return self.send_request(
            'POST', host, request_uri, params, auth_type, sent_data_type, supports_signature_auth
        )

    def put(self, host, request_uri, params, auth_type=None):
        return self.send_request('PUT', host, request_uri, params, auth_type)

    def patch(self, host, request_uri, params, auth_type=None):
        return self.send_request('PATCH', host, request_uri, params, auth_type)

    def delete(self, host, request_uri, params=None, auth_type=None):
        return self.send_request('DELETE', host, request_uri, params, auth_type)

    def send_request(
        self,
        request_type: str,
        host: str,
        request_uri: str,
        params: dict = {},
        auth_type=None,
        sent_data_type='json',
        supports_signature_auth=False,
    ):
        """
        Low-level method to make a request to an API server.
        The supports_signature_auth parameter lets you preferentially use signature authentication if a
        signature_secret was provided when initializing this client (only for the SMS API).
        """

        uri = f"https://{host}{request_uri}"
        self._request_headers = self.headers

        if auth_type == 'jwt':
            self._request_headers['Authorization'] = self._create_jwt_auth_string()
        elif auth_type == 'params':
            if supports_signature_auth and self.signature_secret:
                params["api_key"] = self.api_key
                params["sig"] = self.signature(params)
            else:
                params = dict(
                    params,
                    api_key=self.api_key,
                    api_secret=self.api_secret,
                )
        elif auth_type == 'header':
            self._request_headers['Authorization'] = self._create_header_auth_string()
        else:
            raise InvalidAuthenticationTypeError(
                f'Invalid authentication type. Must be one of "jwt", "header" or "params".'
            )

        logger.debug(
            f'{request_type} to {repr(uri)} with params {repr(params)}, headers {repr(self._request_headers)}'
        )
        if sent_data_type == 'json':
            return self.parse(
                host,
                self.session.request(
                    request_type,
                    uri,
                    json=params,
                    headers=self._request_headers,
                    timeout=self.timeout,
                ),
            )
        elif sent_data_type == 'data':
            return self.parse(
                host,
                self.session.request(
                    request_type,
                    uri,
                    data=params,
                    headers=self._request_headers,
                    timeout=self.timeout,
                ),
            )
        else:
            return self.parse(
                host,
                self.session.request(
                    request_type,
                    uri,
                    params=params,
                    headers=self._request_headers,
                    timeout=self.timeout,
                ),
            )

    def parse(self, host: str, response: Response):
        logger.debug(f'Response headers {repr(response.headers)}')

        if response.status_code == 401:
            raise AuthenticationError('Authentication failed.')
        if response.status_code == 204:
            return None

        try:
            content_type = response.headers['Content-Type'].split(';', 1)[0]
        except KeyError:
            raise ClientError(response, None, host)

        if 200 <= response.status_code < 300:
            if content_type == "application/json":
                try:
                    return response.json()
                except JSONDecodeError:  # Get this when we get a 202 with no content
                    return None
            else:
                return response.text

        if 400 <= response.status_code < 500:
            logger.warning(f'Client error: {response.status_code} {repr(response.content)}')
            raise ClientError(response, content_type, host)

        if 500 <= response.status_code < 600:
            logger.warning(f"Server error: {response.status_code} {repr(response.content)}")
            message = f"{response.status_code} response from {host}"
            raise ServerError(message)

    def _create_jwt_auth_string(self):
        return b"Bearer " + self.generate_application_jwt()

    def generate_application_jwt(self):
        try:
            return self._jwt_client.generate_application_jwt(self._jwt_claims)
        except AttributeError as err:
            if '_jwt_client' in str(err):
                raise VonageError(
                    'JWT generation failed. Check that you passed in valid values for "application_id" and "private_key".'
                )
            else:
                raise err

    def _create_header_auth_string(self):
        hash = base64.b64encode(f"{self.api_key}:{self.api_secret}".encode("utf-8")).decode("ascii")
        return f"Basic {hash}"
