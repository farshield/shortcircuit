# Pathfinder

## Description
Pathfinder is a desktop application which is able to find the shortest path between solar systems (including wormholes) using data retrieved from Eve SDE and 3rd party wormhole mapping tools. The application is able to run on all systems where Python and PySide vesion 1.2.4 are supported.

**Features:**

1. Ability to add wormhole connections from [Tripwire](https://tripwire.eve-apps.com/)
2. CREST authentication for reading the player location and setting the destination in-game
3. Avoidance list
4. Wormhole restrictions for: size, life, mass, last updated
5. Instructions specify the signature and type of the wormhole (makes navigation easier)
6. One-line output which can be copy-pasted for those lazy fleet members

## Usage
```bash
$ pip install -r requirements.txt
$ cd src
$ python main.py
```

Some users reported having troubles when installing PySide on Linux/Mac. Try using your built-in package manager. Example for debian-based systems:
```bash
$ sudo apt-get install python-pyside
```

## Releases
Binaries (executables) can be downloaded from [here](https://github.com/farshield/pathfinder/releases)

## About CREST
Using CREST is optional, but it provides features like getting current player location or setting in-game destination automatically.

Pathfinder uses almost the same CREST model as PyFa. You can find more about it [here](https://github.com/pyfa-org/Pyfa/wiki/CREST). Implicit mode only allows for a 20 minutes session, after that you have to relog. If you don't want to use the "implicit" mode, you can create your own keys at this [location](https://developers.eveonline.com/applications). This will permit you to stay logged in for a longer period of time. Application form should look something like [this](http://i.imgur.com/qhIPG6r.png). Of course you can give it a different name and description, but you have to type in the correct callback URL `http://127.0.0.1:7444` and select the correct scopes (`characterLocationRead` and `characterNavigationWrite`).

## Eve-Scout
![TripwireConfig](http://i.imgur.com/GiJ2zc3.png)

If you enable Eve-Scout option then wormhole connections to/from Thera updated by [Eve-Scout](https://www.eve-scout.com/) will be retrieved, also. However, if you use the public Tripwire server, which is `https://tripwire.eve-apps.com/`, then there's no need to enable this option because Eve-Scout is updating Thera connections on the public Tripwire server automatically.

This is only useful if you or your corp/alliance have their own Tripwire server.

## Security prioritization
Security prioritization mechanism is defined by four values which represent a weight, or an effort:

* HS - the amount of effort it takes to jump a gate to high-sec
* LS - the amount of effort it takes to jump a gate to low-sec
* NS - the amount of effort it takes to jump a gate to null-sec
* WH - the amount of effort it takes to jump a wormhole to any system

Values may range from 1 to 100 and if all values are equal (ex. all equal to 1), then this function is practically disabled.

![SecPrio](http://i.imgur.com/wUaSe3e.png)

In the above scenario the user specified that the effort is the same for taking gates to high-sec or low-sec and there's no need to prioritize one above the other. Compared to this, it's ten times more difficult to take gates to null-sec and three times more difficult to take any wormholes compared to high-sec/low-sec gates.

For example, this may be useful when trying to avoid null-sec systems if possible, unless it shortens the path considerably, and when wormholes aren't bookmarked.

## Screenshot
![Screenshot](http://i.imgur.com/qlLLDFn.png)

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
1. Improve the searching algorithm and offer the possibility to prioritize certain security values (ex. avoid low-sec/null-sec if possible)
2. Add support for more 3rd party wormhole mapping tools
3. Combine data from multiple sources (multiple Tripwire accounts, etc.)
4. Suggestions?

## Contacts
For any questions please contact Valtyr Farshield. Contract me some Quafe. Thank you :)
