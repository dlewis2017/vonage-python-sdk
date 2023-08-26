class Ussd:
    defaults = {'auth_type': 'params', 'sent_data_type': 'data'}

    def __init__(self, client):
        self._client = client

    def send_ussd_push_message(self, params=None, **kwargs):
        return self._client.post(
            self._client.host(), "/ussd/json", params or kwargs, **Ussd.defaults
        )

    def send_ussd_prompt_message(self, params=None, **kwargs):
        return self._client.post(
            self._client.host(), "/ussd-prompt/json", params or kwargs, **Ussd.defaults
        )
