# evecrest.py

import time
import logging
import threading
import uuid
import pycrest
from server import StoppableHTTPServer, AuthHandler


class Crest:
    """
    CREST
    """
    def __init__(self):
        self.httpd = None
        self.state = None
        self.client_id = "0428d86e5a03494ea5f6124ecb01995d"
        self.api_key = "rdQ21g0F4M1WJYEklJ1UscK1P2dDXsgUhhZattfX"
        self.client_callback = "http://127.0.0.1:7444"
        self.scopes = ['characterLocationRead', 'characterNavigationWrite']

        self.eve = pycrest.EVE(
            client_id=self.client_id,
            api_key=self.api_key,
            redirect_uri=self.client_callback,
            testing=False
        )

    def start_server(self):
        if self.httpd:
            self.stop_server()
            time.sleep(1)
        logging.debug("Starting server")
        self.httpd = StoppableHTTPServer(('127.0.0.1', 7444), AuthHandler)
        threading.Thread(target=self.httpd.serve, args=(self.handle_login, )).start()

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
            # eve = copy.deepcopy(self.eve)
            con = self.eve.authorize(message['code'][0])
            self.eve()
            whoami = con.whoami()
            print whoami

        self.stop_server()


def main():
    crest = Crest()
    print crest.start_server()
    raw_input("Press <RETURN> to stop server\n")
    crest.stop_server()

if __name__ == "__main__":
    main()
