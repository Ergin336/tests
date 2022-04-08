from __future__ import division, print_function
from webthing import (Action, Event, MultipleThings, Property, Thing,
                      WebThingServer)
import logging
import random
import time
import tornado.ioloop
import uuid

class OverheatedEvent(Event):

    def __init__(self, thing, data):
        Event.__init__(self, thing, 'overheated', data=data)

class FadeAction(Action):

    def __init__(self, thing, input_):
        Action.__init__(self, uuid.uuid4().hex, thing, 'fade', input_=input_)

    def perform_action(self):
        time.sleep(self.input['duration'] / 1000)
        self.thing.set_property('brightness', self.input['brightness'])
        self.thing.add_event(OverheatedEvent(self.thing, 102))


class FakeGpioHumiditySensor(Thing):
    """
        PALWatch publishing the activity state of the user
    """

    def __init__(self):
        Thing.__init__(
            self,
            'urn:dev:ops:palwatch',
            'PALWatch',
            ['Reconocimiento de la Actividad Humana'],
            'PALWatch en la red'
        )

        self.level = "out_of_range"
        self.add_property(
            Property(self,
                     'level',
                     self.level,
                     metadata={
                         '@type': 'ActivityProperty',
                         'title': 'Activity',
                         'type': 'string',
                         'description': 'La actividad actual del usuario',
                         'sentado': 0,
                         'de pie': 1,
                         'caminando': 2,
                         'readOnly': True,
                     }))

        logging.debug('starting the sensor update looping task')
        self.timer = tornado.ioloop.PeriodicCallback(
            self.update_level,
            1000
        )
        self.timer.start()

    def update_level(self):
        new_state = "sentado"
        logging.debug('Estado actual de Ergin: %s', new_state)
        self.level.notify_of_external_update(new_state)

    def cancel_update_level_task(self):
        self.timer.stop()

    @staticmethod
    def read_from_gpio():
        """Mimic an actual sensor updating its reading every couple seconds.
        """
        return abs(70.0 * random.random() * (-0.5 + random.random()))


def run_server():
    # Create a thing that represents a humidity sensor
    sensor = FakeGpioHumiditySensor()

    # If adding more than one thing, use MultipleThings() with a name.
    # In the single thing case, the thing's name will be broadcast.
    server = WebThingServer(MultipleThings([sensor],
                                           'PALWatch'),
                            port=8888)
    try:
        logging.info('starting the server')
        server.start()
    except KeyboardInterrupt:
        logging.debug('canceling the sensor update looping task')
        sensor.cancel_update_level_task()
        logging.info('stopping the server')
        server.stop()
        logging.info('done')


if __name__ == '__main__':
    logging.basicConfig(
        level=10,
        format="%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s"
    )
    run_server()
