""" This is the module with all our model definitions """

import math

import elixir

import settings

elixir.metadata.bind = settings.DATABASE

class ShipType(object):
    """ This class is used as an ENUM type to represent our ship types """
    CORVETTE = u"Corvette"
    GALLEON = u"Galleon"

class ShipState(object):
    """ This class is used as an ENUM type to represent our ship state """
    NORMAL = 0
    SUNK = 1
    GROUNDED = 2
    ON_FIRE = 3
    A_DRIFT = 4
    SURRENDERED = 5

class Ship(elixir.Entity):
    """ This represents our ship and all the fields it needs to store our data """
    elixir.using_options(tablename="soab_ship")

    hit_points = elixir.Field(elixir.Integer)
    max_hit_points = elixir.Field(elixir.Integer)
    max_speed = elixir.Field(elixir.Integer)
    num_cannons = elixir.Field(elixir.Integer)
    ship_type = elixir.Field(elixir.UnicodeText) # From our ShipType
    name = elixir.Field(elixir.UnicodeText)
    turn_radius_factor = elixir.Field(elixir.Float)
    max_ratio = elixir.Field(elixir.Float)
    max_theta = elixir.Field(elixir.Integer)
    sails = elixir.Field(elixir.Float)

    state = ShipState.NORMAL

    def max_angle_in_rads(self):
        return self.max_theta * math.pi / 180

    def angular_velocity(self, turn_factor):
        return 1 / (self.turn_radius_factor * turn_factor)

    def hp_as_percent(self):
        return math.ceil(self.hit_points / self.max_hit_points)

    def broadside_damage(self):
        return math.ceil(self.num_cannons / 2)

    def take_damage(self, damage):
        self.hit_points -= damage
        if self.hit_points < 0:
            self.hit_points = 0

    def __repr__(self):
        return '<Ship "%s" (hp=%d, max_speed=%d, num_cannons=%d, type=%s)>' % (self.name,
                self.hit_points, self.max_speed, self.num_cannons, self.ship_type)

class Map(elixir.Entity):
    """ This represents our map and all the data it needs """
    elixir.using_options(tablename="soab_map")

    name = elixir.Field(elixir.UnicodeText)
    x = elixir.Field(elixir.Integer)
    y = elixir.Field(elixir.Integer)
    wind_speed = elixir.Field(elixir.Integer)
    wind_dir = elixir.Field(elixir.Integer)

    def __repr__(self):
        return '<Map "%s" (x=%d, y=%d, wind_speed=%d, wind_dir=%d)>' % (self.name,
                self.x, self.y, self.wind_speed, self.wind_dir)

elixir.setup_all()
