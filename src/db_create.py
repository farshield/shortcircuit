# db_create.py

import os
import sqlite3


def main():
    """
    Generates the following files:
        - system_description.csv
        - system_jumps.csv
    from the SDE database (https://developers.eveonline.com/resource/resources)
    Place "universeDataDx.db" in the database resource directory for this script to run
    :return:
    """
    db_dir = os.path.join("..", "resources", "database")
    eve_db_file = os.path.join(db_dir, "universeDataDx.db")
    system_jumps_file = os.path.join(db_dir, "system_jumps.csv")
    system_description_file = os.path.join(db_dir, "system_description.csv")

    # read Eve SQL databse
    with sqlite3.connect(eve_db_file) as sql_con:
        cursor = sql_con.cursor()

        # write solar system jumps file (gate connections)
        result = cursor.execute('SELECT fromSolarSystemID, toSolarSystemID FROM mapSolarSystemJumps')
        with open(system_jumps_file, "w") as f_out:
            for row in result.fetchall():
                f_out.write("{};{}\n".format(row[0], row[1]))

        # write solar system description file (id, name, security class, security value)
        result = cursor.execute('SELECT regionID, solarSystemID, solarSystemName, security FROM mapSolarSystems')
        with open(system_description_file, "w") as f_out:
            for row in result.fetchall():
                region_id = row[0]
                system_id = row[1]
                system_name = row[2]
                security = float(row[3])

                # try and compute wormhole class or k-space class (HS, LS, NS)
                query = cursor.execute(
                    'SELECT wormholeClassID FROM mapLocationWormholeClasses WHERE locationID=?',
                    (region_id, )
                )
                system_class = query.fetchone()
                if system_class:
                    system_class = system_class[0]
                else:
                    query = cursor.execute(
                        'SELECT wormholeClassID FROM mapLocationWormholeClasses WHERE locationID=?',
                        (system_id, )
                    )
                    system_class = query.fetchone()
                    if system_class:
                        system_class = system_class[0]
                    else:
                        system_class = "Unknown"

                if system_class != "Unknown":
                    if system_class in [1, 2, 3, 4, 5, 6, 12, 13, 14, 15, 16, 17, 18]:
                        system_class = "C{}".format(system_class)
                    else:
                        if 0.45 <= security:
                            system_class = "HS"
                        elif 0 <= security < 0.45:
                            system_class = "LS"
                        else:
                            system_class = "NS"

                if security < 0:
                    security_format = "{:.2f}".format(security)
                elif 0 <= security <= 0.1:
                    security_format = "0.1"
                else:
                    security_format = "{:.1f}".format(security)
                f_out.write("{};{};{};{}\n".format(system_id, system_name, system_class, security_format))


if __name__ == "__main__":
    main()
