# server.py

import os
import BaseHTTPServer
import urlparse
import socket
import threading
import logging


# https://github.com/fuzzysteve/CREST-Market-Downloader/
class AuthHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/favicon.ico":
            return
        parsed_path = urlparse.urlparse(self.path)
        parts = urlparse.parse_qs(parsed_path.query)
        self.send_response(200)
        self.end_headers()
        script_dir = os.path.dirname(__file__)
        file_path = os.path.join(script_dir, 'server.html')
        with open(file_path) as html_file:
            self.wfile.write(html_file.read())
        self.server.callback(parts)

    def log_message(self, format, *args):
        return


# http://code.activestate.com/recipes/425210-simple-stoppable-server-using-socket-timeout/
class StoppableHTTPServer(BaseHTTPServer.HTTPServer):

    WAIT_TIMEOUT = 120

    def server_bind(self):
        BaseHTTPServer.HTTPServer.server_bind(self)

        # Allow listening for x seconds
        logging.debug("Running server for %d seconds", StoppableHTTPServer.WAIT_TIMEOUT)

        self.socket.settimeout(0.5)
        self.max_tries = StoppableHTTPServer.WAIT_TIMEOUT / self.socket.gettimeout()
        self.tries = 0
        self.run = True

    def get_request(self):
        while self.run:
            try:
                sock, addr = self.socket.accept()
                sock.settimeout(None)
                return (sock, addr)
            except socket.timeout:
                pass

    def stop(self):
        self.run = False

    def handle_timeout(self):
        self.tries += 1
        if self.tries == self.max_tries:
            logging.debug("Server timed out waiting for connection")
            self.stop()

    def serve(self, callback):
        self.callback = callback
        while self.run:
            try:
                self.handle_request()
            except TypeError:
                pass
        self.server_close()


def handle_login(message):
    """
    Development purposes
    :param message:
    :return:
    """
    logging.debug("Message: {}".format(message))


def main():
    httpd = StoppableHTTPServer(('', 7444), AuthHandler)
    threading.Thread(target=httpd.serve, args=(handle_login, )).start()
    raw_input("Press <RETURN> to stop server\n")
    httpd.stop()


if __name__ == "__main__":
    main()
