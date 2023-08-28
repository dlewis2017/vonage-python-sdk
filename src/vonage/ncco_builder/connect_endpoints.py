from pydantic import BaseModel, HttpUrl, AnyUrl, constr
from typing import Dict, Literal


class ConnectEndpoints:
    class Endpoint(BaseModel):
        type: str = None

    class PhoneEndpoint(Endpoint):
        number: constr(pattern=r'^[1-9]\d{6,14}$')
        dtmfAnswer: constr(pattern='^[0-9*#p]+$') = None
        onAnswer: Dict[str, HttpUrl] = None
        type: Literal['phone'] = 'phone'

    class AppEndpoint(Endpoint):
        user: str
        type: Literal['app'] = 'app'

    class WebsocketEndpoint(Endpoint):
        uri: AnyUrl
        contentType: Literal['audio/l16;rate=16000', 'audio/l16;rate=8000']
        headers: dict = None
        type: Literal['websocket'] = 'websocket'

    class SipEndpoint(Endpoint):
        uri: str
        headers: dict = None
        type: Literal['sip'] = 'sip'

    class VbcEndpoint(Endpoint):
        extension: str
        type: Literal['vbc'] = 'vbc'

    @classmethod
    def create_endpoint_model_from_dict(cls, d) -> Endpoint:
        if d['type'] == 'phone':
            return cls.PhoneEndpoint.model_validate(d)
        elif d['type'] == 'app':
            return cls.AppEndpoint.model_validate(d)
        elif d['type'] == 'websocket':
            return cls.WebsocketEndpoint.model_validate(d)
        elif d['type'] == 'sip':
            return cls.WebsocketEndpoint.model_validate(d)
        elif d['type'] == 'vbc':
            return cls.WebsocketEndpoint.model_validate(d)
        else:
            raise ValueError(
                'Invalid "type" specified for endpoint object. Cannot create a ConnectEndpoints.Endpoint model.'
            )
