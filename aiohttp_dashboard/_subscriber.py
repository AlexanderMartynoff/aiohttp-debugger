from operator import itemgetter
from asyncio import sleep, ensure_future, get_event_loop
from time import time
from collections import defaultdict
from collections import namedtuple
import logging

from ._misc import MsgDirection, is_subset_dict
from ._state import DEBUGGER_KEY
from ._timeguard import TimeGuardFactory


logger = logging.getLogger(__name__)

timeguard = TimeGuardFactory(3)


class Subcriber:
    def __init__(self, websocket, state):
        self._state = state
        self._websocket = websocket

    def subscribe(self, message):
        conditions = message['data']['conditions']

        @timeguard
        def send(event):
            self._send({
                'id': message['id'],
                'event': event,
            })

        def subscribtion(event: str, parameters: dict):
            if conditions and not is_subset_dict(
                    conditions, parameters):
                return

            send(event, _state=event.__class__.__name__)

        self._state.emitter.on(
            event=message['data']['event'],
            handler=subscribtion,
            name=message['id'],
            family=id(self),
        )

    def unsubscribe(self, message):
        self._state.emitter.off(name=message['data']['id'])

    def cancel(self):
        self._state.emitter.off(family=id(self))

    def _send(self, message):
        return ensure_future(self._websocket.send_json(message))
