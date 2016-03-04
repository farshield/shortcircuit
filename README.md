# Pathfinder

## Description
Pathfinder is a desktop application which is able to find the shortest path between solar systems (including wormholes) using data retrieved from Eve SDE and 3rd party wormhole mapping tools. The application is able to run on all systems where Python and PySide (PyQt) are supported.

**Features:**

1. Ability to add wormhole connections from [Tripwire](https://tripwire.eve-apps.com/)
2. CREST authentication for reading the player location and setting the destination in-game
3. Avoidance list
4. Wormhole size restrictions
5. Instructions specify the signature and type of the wormhole (makes navigation easier)
6. One-line output which can be copy-pasted for those lazy fleet members

## Usage
```bash
$ pip install -r requirements.txt
$ cd src
$ python main.py
```

## Releases
Binaries (executables) can be downloaded from [here](https://github.com/farshield/pathfinder/releases)

## About CREST
Pathfinder uses almost the same CREST model as PyFa. You can find more about it [here](https://github.com/pyfa-org/Pyfa/wiki/CREST). If you don't want to use the "implicit" mode, you can create your own keys at this [location](https://developers.eveonline.com/applications). Application form should look something like [this](http://i.imgur.com/qhIPG6r.png). Of course you can give it a different name and description, but you have to type in the correct callback URL `http://127.0.0.1:7444` and select the correct scopes (`characterLocationRead` and `characterNavigationWrite`).

## Screenshot
![Screenshot](http://i.imgur.com/ltjEsyW.png)

## Video
<a href="http://www.youtube.com/watch?feature=player_embedded&v=oM3mSKzZM0w" target="_blank"><img src="http://img.youtube.com/vi/oM3mSKzZM0w/0.jpg" alt="Pathfinder video" width="480" height="360" border="10" /></a>

## How it works
Pathfinder reconstructs its own version of the Eve solar map from the 'mapSolarSystemJumps' table of the Static Data Export database. After that, the solar map can be extended by retrieving connections from popular 3rd party wormhole mapping tools. The JSON response from [Tripwire](https://tripwire.eve-apps.com/) is processed and the connections are added to the existing solar map. Graph algorithms will compute the shortest path taking certain things into account like avoidance list and wormhole size restrictions.

Sample JSON response from Tripwire (converted to YAML for easy reading). This type of response is processed and added to the application's own solar system representation:
```yaml
id: "5642035"
signatureID: "GGC"
system: ""
systemID: "31000857"
connection: "Hutian"
connectionID: "30002217"
sig2ID: "JTC"
type: "B274"
nth: null
sig2Type: "K162"
nth2: null
lifeLength: "24"
life: "Stable"
mass: "Stable"
...
```

## Future development
1. Take into account wormhole creation/stable time
2. Add support for more 3rd party wormhole mapping tools
3. Combine data from multiple sources (multiple Tripwire accounts, etc.)
4. Improve the searching algorithm and offer the possibility to prioritize certain security values (ex. avoid low-sec/null-sec if possible)
5. Suggestions?

## Contacts
For any questions please contact Valtyr Farshield. Thank you :)
