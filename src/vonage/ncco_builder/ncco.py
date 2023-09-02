from pydantic import (
    BaseModel,
    Field,
    FieldValidationInfo,
    field_validator,
    constr,
    confloat,
    conint,
)
from typing import Union, List, Literal

from .connect_endpoints import ConnectEndpoints
from .input_types import InputTypes


class Ncco:
    class Action(BaseModel):
        action: str = None

    class Record(Action):
        """Use the record action to record a call or part of a call."""

        format: Literal['mp3', 'wav', 'ogg'] = None
        split: Literal['conversation'] = None
        channels: conint(ge=1, le=32) = None
        endOnSilence: conint(ge=3, le=10) = None
        endOnKey: constr(pattern='^[0-9*#]$') = None
        timeOut: conint(ge=3, le=7200) = None
        beepStart: bool = None
        eventUrl: Union[List[str], str] = None
        eventMethod: constr(to_upper=True) = None
        action: Literal['record'] = 'record'

        @field_validator('channels')
        @classmethod
        def enable_split(cls, v, field_info: FieldValidationInfo):
            if field_info.data['split'] is None:
                field_info.data['split'] = 'conversation'
            return v

        @field_validator('eventUrl')
        @classmethod
        def ensure_url_in_list(cls, v):
            return Ncco._ensure_object_in_list(v)

    class Conversation(Action):
        """You can use the conversation action to create standard or moderated conferences,
        while preserving the communication context.
        Using conversation with the same name reuses the same persisted conversation."""

        name: str
        musicOnHoldUrl: Union[List[str], str] = None
        startOnEnter: bool = None
        endOnExit: bool = None
        record: bool = None
        canSpeak: List[str] = None
        canHear: List[str] = None
        mute: bool = None
        action: Literal['conversation'] = 'conversation'

        @field_validator('musicOnHoldUrl')
        @classmethod
        def ensure_url_in_list(cls, v):
            return Ncco._ensure_object_in_list(v)

        @field_validator('mute')
        @classmethod
        def can_mute(cls, v, field_info: FieldValidationInfo):
            if field_info.data['canSpeak'] is not None:
                raise ValueError('Cannot use mute option if canSpeak option is specified.')
            return v

    class Connect(Action):
        """You can use the connect action to connect a call to endpoints such as phone numbers or a VBC extension.

        If specifying a value for the "from" field, name it with a trailing underscore, i.e. "from_".
        """

        endpoint: Union[dict, ConnectEndpoints.Endpoint, list]
        from_: str = Field(default=None, serialization_alias='from', pattern=r'^[1-9]\d{6,14}$')
        randomFromNumber: bool = None
        eventType: Literal['synchronous'] = None
        timeout: int = None
        limit: conint(le=7200) = None
        machineDetection: Literal['continue', 'hangup'] = None
        advancedMachineDetection: dict = None
        eventUrl: Union[List[str], str] = None
        eventMethod: constr(to_upper=True) = None
        ringbackTone: str = None
        action: Literal['connect'] = 'connect'

        @field_validator('endpoint')
        @classmethod
        def validate_endpoint(cls, v):
            if type(v) is dict:
                return [ConnectEndpoints.create_endpoint_model_from_dict(v)]
            elif type(v) is list:
                return [ConnectEndpoints.create_endpoint_model_from_dict(v[0])]
            else:
                return [v]

        @field_validator('randomFromNumber')
        @classmethod
        def check_from_not_set(cls, v, field_info: FieldValidationInfo):
            if v is True and 'from_' in field_info.data:
                if field_info.data['from_'] is not None:
                    raise ValueError(
                        'Cannot set a "from" ("from_") field and also the "randomFromNumber" = True option'
                    )
            return v

        @field_validator('eventUrl')
        @classmethod
        def ensure_url_in_list(cls, v):
            return Ncco._ensure_object_in_list(v)

        @field_validator('advancedMachineDetection')
        @classmethod
        def validate_advancedMachineDetection(cls, v):
            if 'behavior' in v and v['behavior'] not in ('continue', 'hangup'):
                raise ValueError(
                    'advancedMachineDetection["behavior"] must be one of: "continue", "hangup".'
                )
            if 'mode' in v and v['mode'] not in ('detect, detect_beep'):
                raise ValueError(
                    'advancedMachineDetection["mode"] must be one of: "detect", "detect_beep".'
                )
            return v

    class Talk(Action):
        """The talk action sends synthesized speech to a Conversation."""

        text: constr(max_length=1500)
        bargeIn: bool = None
        loop: conint(ge=0) = None
        level: confloat(ge=-1, le=1) = None
        language: str = None
        style: int = None
        premium: bool = None
        action: Literal['talk'] = 'talk'

    class Stream(Action):
        """The stream action allows you to send an audio stream to a Conversation."""

        streamUrl: Union[List[str], str]
        level: confloat(ge=-1, le=1) = None
        bargeIn: bool = None
        loop: conint(ge=0) = None
        action: Literal['stream'] = 'stream'

        @field_validator('streamUrl')
        @classmethod
        def ensure_url_in_list(cls, v):
            return Ncco._ensure_object_in_list(v)

    class Input(Action):
        """Collect digits or speech input by the person you are are calling."""

        type: Union[
            Literal['dtmf', 'speech'],
            List[Literal['dtmf']],
            List[Literal['speech']],
            List[Literal['dtmf', 'speech']],
        ]
        dtmf: Union[InputTypes.Dtmf, dict] = None
        speech: Union[InputTypes.Speech, dict] = None
        eventUrl: Union[List[str], str] = None
        eventMethod: constr(to_upper=True) = None
        action: Literal['input'] = 'input'

        @field_validator('type', 'eventUrl')
        @classmethod
        def ensure_value_in_list(cls, v):
            return Ncco._ensure_object_in_list(v)

        @field_validator('dtmf')
        @classmethod
        def ensure_input_object_is_dtmf_model(cls, v):
            if type(v) is dict:
                return InputTypes.create_dtmf_model(v)
            else:
                return v

        @field_validator('speech')
        @classmethod
        def ensure_input_object_is_speech_model(cls, v):
            if type(v) is dict:
                return InputTypes.create_speech_model(v)
            else:
                return v

    class Notify(Action):
        """Use the notify action to send a custom payload to your event URL."""

        payload: dict
        eventUrl: Union[List[str], str]
        eventMethod: constr(to_upper=True) = None
        action: Literal['notify'] = 'notify'

        @field_validator('eventUrl')
        @classmethod
        def ensure_url_in_list(cls, v):
            return Ncco._ensure_object_in_list(v)

    @staticmethod
    def build_ncco(*args: Action, actions: List[Action] = None) -> str:
        ncco = []
        if actions is not None:
            for action in actions:
                ncco.append(action.model_dump(by_alias=True, exclude_none=True))
        for action in args:
            ncco.append(action.model_dump(by_alias=True, exclude_none=True))
        return ncco

    @staticmethod
    def _ensure_object_in_list(obj):
        if type(obj) != list:
            return [obj]
        else:
            return obj
