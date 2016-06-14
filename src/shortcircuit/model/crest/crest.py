# evecrest.py

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

    SERVER_CLIENT_ID = "866fe9e6ac8a4e15ad41b9816d5de11e"

    def __init__(self, implicit, client_id, client_secret, login_callback, logout_callback):
        self.login_callback = login_callback
        self.logout_callback = logout_callback
        self.httpd = None
        self.state = None
        self.client_callback = "http://127.0.0.1:7444"
        self.scopes = ['characterLocationRead', 'characterNavigationWrite']

        self.eve = None
        self.con = None
        self.char_id = None
        self.char_name = None
        self.sso_timer = None

        self.update_credentials(implicit, client_id, client_secret)

    def update_credentials(self, implicit, client_id, client_secret):
        client_id = client_id.encode('ascii', 'ignore')
        client_secret = client_secret.encode('ascii', 'ignore')
        if implicit:
            self.eve = pycrest.EVE(
                client_id=Crest.SERVER_CLIENT_ID,
                api_key=None,
                redirect_uri=self.client_callback,
                testing=False
            )
        else:
            self.eve = pycrest.EVE(
                client_id=client_id,
                api_key=client_secret,
                redirect_uri=self.client_callback,
                testing=False
            )

    def start_server(self):
        if not self.httpd:
            # Server not running - restart it
            logging.debug("Starting server")
            self.httpd = StoppableHTTPServer(
                server_address=('127.0.0.1', 7444),
                RequestHandlerClass=AuthHandler,
                timeout_callback=self.timeout_server
            )
            server_thread = threading.Thread(target=self.httpd.serve, args=(self.handle_login, ))
            server_thread.setDaemon(True)
            server_thread.start()
            self.state = str(uuid.uuid4())
        else:
            # Server already running - reset timeout counter
            self.httpd.tries = 0

        return self.eve.auth_uri(scopes=self.scopes, state=self.state)

    def timeout_server(self):
        self.httpd = None

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
        elif 'access_token' in message:
            try:
                self.con = self.eve.temptoken_authorize(
                    access_token=message['access_token'][0],
                    expires_in=int(message['expires_in'][0])
                )
                self.eve()
                whoami = self.con.whoami()
                self.char_id = whoami['CharacterID']
                self.char_name = whoami['CharacterName']
            except APIException:
                self.char_id = None
                self.char_name = None
            else:
                self.sso_timer = threading.Timer(int(message['expires_in'][0]), self._logout)
                self.sso_timer.setDaemon(True)
                self.sso_timer.start()
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
        if self.sso_timer:
            self.sso_timer.cancel()
        self._logout()

    def _logout(self):
        self.con = None
        self.char_id = None
        self.char_name = None
        self.logout_callback()


def login_cb(char_name):
    print "Welcome, {}".format(char_name)


def logout_cb():
    print "Session expired"


def main():
    import code

    implicit = True
    client_id = ""
    client_secret = ""

    crest = Crest(implicit, client_id, client_secret, login_cb, logout_cb)
    print crest.start_server()
    gvars = globals().copy()
    gvars.update(locals())
    shell = code.InteractiveConsole(gvars)
    shell.interact()

if __name__ == "__main__":
    main()
