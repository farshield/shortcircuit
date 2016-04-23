# tripwire.py

import json
import requests
import urlparse
import logging
from datetime import datetime
from solarmap import SolarMap


class Tripwire:
    """
    Tripwire handler
    """

    def __init__(self, eve_db, username, password, url):
        self.eve_db = eve_db
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

                    # Retrieve signature meta data
                    source = convert_to_int(sig["systemID"])
                    dest = convert_to_int(sig["connectionID"])
                    sig_source = sig["signatureID"]
                    sig_dest = sig["sig2ID"]
                    code_source = sig["type"]
                    code_dest = sig["sig2Type"]
                    if sig["life"] == "Stable":
                        wh_life = 1
                    else:
                        wh_life = 0
                    if sig["mass"] == "Stable":
                        wh_mass = 2
                    elif sig["mass"] == "Destab":
                        wh_mass = 1
                    else:
                        wh_mass = 0

                    # Compute time elapsed from this moment to when the signature was updated
                    last_modified = datetime.strptime(sig["time"], "%Y-%m-%d %H:%M:%S")
                    delta = datetime.utcnow() - last_modified
                    time_elapsed = round(delta.total_seconds() / 3600.0, 1)

                    if source != 0 and dest != 0:
                        # Determine wormhole size
                        size_result1 = self.eve_db.get_whsize_by_code(code_source)
                        size_result2 = self.eve_db.get_whsize_by_code(code_dest)
                        if size_result1 in [0, 1, 2, 3]:
                            wh_size = size_result1
                        elif size_result2 in [0, 1, 2, 3]:
                            wh_size = size_result2
                        else:
                            # Wormhole codes are unknown => determine size based on class of wormholes
                            wh_size = self.eve_db.get_whsize_by_system(source, dest)

                        # Add wormhole conection to solar system
                        solar_map.add_connection(
                            source,
                            dest,
                            SolarMap.WORMHOLE,
                            [sig_source, code_source, sig_dest, code_dest, wh_size, wh_life, wh_mass, time_elapsed],
                        )

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
