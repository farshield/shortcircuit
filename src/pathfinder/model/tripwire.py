# tripwire.py

import json
import requests
import urlparse
import logging


class Tripwire:
    """
    Tripwire handler
    """

    def __init__(self, username, password, url):
        self.username = username
        self.password = password
        self.url = url
        self.session_requests = self.login()

    def login(self):
        response = None

        login_url = urlparse.urljoin(self.url, "login.php")
        session_requests = requests.session()

        payload = {
            "username": self.username,
            "password": self.password
        }

        try:
            result = session_requests.post(
                login_url,
                data=payload,
                headers=dict(referer=login_url)
            )
        except requests.exceptions.RequestException:
            logging.warning("Unable to connect to Tripwire")
        else:
            if result.status_code == 200:
                response = session_requests

        return response

    def get_chain(self):
        response = None

        if self.session_requests:
            refresh_url = urlparse.urljoin(self.url, "refresh.php")
            payload = {
                "mode": "init"
            }

            try:
                result = self.session_requests.get(
                    refresh_url,
                    params=payload
                )
            except requests.exceptions.RequestException as e:
                logging.error(e, exc_info=True)
            else:
                if result.status_code == 200:
                    if is_json(result.text):
                        response = result.json()

        return response

    def augment_map(self, solar_map):
        connections = 0
        chain = self.get_chain()

        if chain:
            for sig in chain["chain"]["map"]:
                if sig["type"] != "GATE":
                    connections += 1
                    source = convert_to_int(sig["systemID"])
                    dest = convert_to_int(sig["connectionID"])
                    if source != 0 and dest != 0:
                        solar_map.add_connection(source, dest)

        return connections


def is_json(response):
    """
    Check if the response parameter is a valid JSON string
    :param response:
    :return:
    """
    try:
        json.loads(response)
    except ValueError:
        return False
    return True


def convert_to_int(s):
    """
    Convert string to integer
    :param s: Input string
    :return: Interpreted value if successful, 0 otherwise
    """
    try:
        nr = int(s)
    except (ValueError, TypeError):
        nr = 0

    return nr
