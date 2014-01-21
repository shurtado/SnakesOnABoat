import elixir
from src.models import *

# Creates an empty database and initializes the mapping
elixir.setup_all(True)

if __name__ == '__main__':

    ships = [{'hit_points': 100, 'max_speed': 200, 'num_cannons': 10,
                'ship_type': ShipType.CORVETTE, 'name': u"HMS Surprise",
                'max_theta': 180, 'max_ratio': 2, 'turn_radius_factor': 1,
                'sails': 0.0},
             {'hit_points': 125, 'max_speed': 100, 'num_cannons': 10,
                 'ship_type': ShipType.GALLEON, 'name': u"HMS Kitabi",
                 'max_theta': 180, 'max_ratio': 2, 'turn_radius_factor': 1,
                 'sails': 0.0},
             {'hit_points': 200, 'max_speed': 50, 'num_cannons': 15,
                 'ship_type': ShipType.GALLEON, 'name': u"HMS Brigader",
                 'max_theta': 180, 'max_ratio': 2, 'turn_radius_factor': 1,
                 'sails': 0.0}]

    maps = [{'name': u"Summoner's Rift", 'x': 1000, 'y': 1000, 'wind_speed': 10,
                'wind_dir': 0}]

    # get the name of all ships in the DB
    all_ships = [s.name for s in Ship.query.all()]
    all_maps = [m.name for m in Map.query.all()]

    # insert dummy data
    for s in ships:
        # if the ship doesn't exist
        if s['name'] not in all_ships:
            Ship(**s)

    for m in maps:
        # if the map doesn't exist
        if m['name'] not in all_maps:
            Map(**m)

    # commit
    elixir.session.commit()

    print "Database contains:"
    for s in Ship.query.all():
        print "\t%s" % s
    for m in Map.query.all():
        print "\t%s" % m
