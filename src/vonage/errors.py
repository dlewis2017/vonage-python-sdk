from requests import Response


class VonageError(Exception):
    """Base Error Class for all Vonage SDK errors."""


class ServerError(VonageError):
    """Indicates an error was reported from a Vonage server."""


class ClientError(VonageError):
    """Indicates an error was recieved as part of the response from a Vonage SDK request."""

    def __init__(self, response: Response, content_type: str, host: str):
        if content_type == 'application/json':
            self.body = response.json()
        else:
            self.body = response.text
        if self.body:
            super().__init__(
                f'{response.status_code} response from {host}. \nError Message:\n{self.body}'
            )
        else:
            super().__init__(f'{response.status_code} response from {host}.')


class AuthenticationError(VonageError):
    pass


class CallbackRequiredError(VonageError):
    """Indicates a callback is required but was not present."""


class MessagesError(VonageError):
    """
    Indicates an error related to the Messages class which calls the Vonage Messages API.
    """


class SmsError(VonageError):
    """
    Indicates an error related to the Sms class which calls the Vonage SMS API.
    """


class PartialFailureError(VonageError):
    """
    Indicates that one or more parts of the message was not sent successfully.
    """


class PricingTypeError(VonageError):
    """A pricing type was specified that is not allowed."""


class InvalidAuthenticationTypeError(VonageError):
    """An authentication method was specified that is not allowed."""


class InvalidRoleError(VonageError):
    """The specified role was invalid."""


class TokenExpiryError(VonageError):
    """The specified token expiry time was invalid."""


class InvalidOptionsError(VonageError):
    """The option(s) that were specified are invalid."""

    """An authentication method was specified that is not allowed."""


class VerifyError(VonageError):
    """Error related to the Verify API."""


class BlockedNumberError(VonageError):
    """The number you are trying to verify is blocked for verification."""


class NumberInsightError(VonageError):
    """Error related to the Number Insight API."""


class SipError(VonageError):
    """Error related to usage of SIP calls."""


class InvalidInputError(VonageError):
    """The input that was provided was invalid."""


class InvalidAuthenticationTypeError(VonageError):
    """An authentication method was specified that is not allowed."""


class MeetingsError(VonageError):
    """An error related to the Meetings class which calls the Vonage Meetings API."""


class Verify2Error(VonageError):
    """An error relating to the Verify (V2) API."""


class SubaccountsError(VonageError):
    """An error relating to the Subaccounts API."""


class ProactiveConnectError(VonageError):
    """An error relating to the Proactive Connect API."""


class UsersError(VonageError):
    """An error relating to the Users API."""
