from vonage import Ncco, ConnectEndpoints, InputTypes

record = Ncco.Record(eventUrl='http://example.com/events')

conversation = Ncco.Conversation(name='my_conversation')

connect = Ncco.Connect(
    endpoint=ConnectEndpoints.PhoneEndpoint(number='447000000000'),
    from_='447400000000',
    randomFromNumber=False,
    eventType='synchronous',
    timeout=15,
    limit=1000,
    machineDetection='hangup',
    eventUrl='http://example.com',
    eventMethod='PUT',
    ringbackTone='http://example.com',
)

talk_minimal = Ncco.Talk(text='hello')

talk = Ncco.Talk(text='hello', bargeIn=True, loop=3, level=0.5, language='en-GB', style=1, premium=True)

stream = Ncco.Stream(streamUrl='https://example.com/stream/music.mp3', level=0.1, bargeIn=True, loop=10)

input = Ncco.Input(
    type=['dtmf', 'speech'],
    dtmf=InputTypes.Dtmf(timeOut=5, maxDigits=12, submitOnHash=True),
    speech=InputTypes.Speech(
        uuid='my-uuid',
        endOnSilence=2.5,
        language='en-GB',
        context=['sales', 'billing'],
        startTimeout=20,
        maxDuration=30,
        saveAudio=True,
    ),
    eventUrl='http://example.com/speech',
    eventMethod='put',
)

notify = Ncco.Notify(payload={"message": "world"}, eventUrl=["http://example.com"], eventMethod='PUT')

basic_ncco = [{"action": "talk", "text": "hello"}]

two_part_ncco = [
    {
        'action': 'record',
        'eventUrl': ['http://example.com/events'],
    },
    {'action': 'talk', 'text': 'hello'},
]

insane_ncco = [
    {'action': 'record', 'eventUrl': ['http://example.com/events']},
    {'action': 'conversation', 'name': 'my_conversation'},
    {
        'action': 'connect',
        'endpoint': [{'number': '447000000000', 'type': 'phone'}],
        'eventMethod': 'PUT',
        'eventType': 'synchronous',
        'eventUrl': ['http://example.com'],
        'from': '447400000000',
        'limit': 1000,
        'machineDetection': 'hangup',
        'randomFromNumber': False,
        'ringbackTone': 'http://example.com',
        'timeout': 15,
    },
    {
        'action': 'talk',
        'bargeIn': True,
        'language': 'en-GB',
        'level': 0.5,
        'loop': 3,
        'premium': True,
        'style': 1,
        'text': 'hello',
    },
    {
        'action': 'stream',
        'bargeIn': True,
        'level': 0.1,
        'loop': 10,
        'streamUrl': ['https://example.com/stream/music.mp3'],
    },
    {
        'action': 'input',
        'dtmf': {'maxDigits': 12, 'submitOnHash': True, 'timeOut': 5},
        'eventMethod': 'PUT',
        'eventUrl': ['http://example.com/speech'],
        'speech': {
            'context': ['sales', 'billing'],
            'endOnSilence': 2.5,
            'language': 'en-GB',
            'maxDuration': 30,
            'saveAudio': True,
            'startTimeout': 20,
            'uuid': 'my-uuid',
        },
        'type': ['dtmf', 'speech'],
    },
    {'action': 'notify', 'eventMethod': 'PUT', 'eventUrl': ['http://example.com'], 'payload': {'message': 'world'}},
]
