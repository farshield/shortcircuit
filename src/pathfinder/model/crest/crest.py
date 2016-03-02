# evecrest.py

import time
import json
import logging
import threading
import uuid
import pycrest
from pycrest.errors import APIException
from server import StoppableHTTPServer, AuthHandler


class Crest:
    """
    CREST
    """
    def __init__(self, login_callback):
        self.login_callback = login_callback
        self.httpd = None
        self.state = None
        self.client_id = "0428d86e5a03494ea5f6124ecb01995d"
        self.api_key = "rdQ21g0F4M1WJYEklJ1UscK1P2dDXsgUhhZattfX"
        self.client_callback = "http://127.0.0.1:7444"
        self.scopes = ['characterLocationRead', 'characterNavigationWrite']

        self.con = None
        self.char_id = None
        self.char_name = None

        self.eve = pycrest.EVE(
            client_id=self.client_id,
            api_key=self.api_key,
            redirect_uri=self.client_callback,
            testing=False
        )

    def start_server(self):
        if self.httpd:
            self.stop_server()
            time.sleep(0.1)
        logging.debug("Starting server")
        self.httpd = StoppableHTTPServer(('127.0.0.1', 7444), AuthHandler)
        server_thread = threading.Thread(target=self.httpd.serve, args=(self.handle_login, ))
        server_thread.setDaemon(True)
        server_thread.start()

        self.state = str(uuid.uuid4())
        return self.eve.auth_uri(scopes=self.scopes, state=self.state)

    def stop_server(self):
        logging.debug("Stopping server")
        if self.httpd:
            self.httpd.stop()
            self.httpd = None

    def handle_login(self, message):
        if not message:
            return
        if 'state' in message:
            if message['state'][0] != self.state:
                logging.warning("OAUTH state mismatch")
                return

        if 'code' in message:
            try:
                self.con = self.eve.authorize(message['code'][0])
                self.eve()
                whoami = self.con.whoami()
                self.char_id = whoami['CharacterID']
                self.char_name = whoami['CharacterName']
            except APIException:
                self.char_id = None
                self.char_name = None
            finally:
                self.login_callback(self.char_name)

        self.stop_server()

    def get_char_location(self):
        current_location = None
        if self.con:
            uri = '{}characters/{}/location/'.format(self.eve._authed_endpoint, self.char_id)
            try:
                current_location = self.con.get(uri)['solarSystem']['name']
            except (KeyError, TypeError, APIException):
                pass
        return current_location

    def set_char_destination(self, sys_id):
        success = False
        if self.con:
            solar_system = 'https://crest-tq.eveonline.com/solarsystems/{}/'.format(sys_id)
            uri = '{}characters/{}/navigation/waypoints/'.format(self.eve._authed_endpoint, self.char_id)
            post_data = json.dumps(
                {
                    'solarSystem': {'href': solar_system, 'id': sys_id},
                    'first': False,
                    'clearOtherWaypoints': True
                }
            )
            try:
                self.con.post(uri, data=post_data)
            except APIException:
                pass
            else:
                success = True
        return success

    def logout(self):
        self.con = None
        self.char_id = None
        self.char_name = None


def login_cb(char_name):
    print "Welcome, {}".format(char_name)


def main():
    import code

    crest = Crest(login_cb)
    print crest.start_server()
    gvars = globals().copy()
    gvars.update(locals())
    shell = code.InteractiveConsole(gvars)
    shell.interact()

if __name__ == "__main__":
    main()
