""" This is the module for Movement Controller Class """
import math

class MovementController(object):
    def __init__(self, map):
        self.TURN_RADIUS_FACTOR = 50
        self.map = map
        self.x = map.x
        self.y = map.y
        self.last_x = self.x / 2
        self.last_y = self.y

    def update_position(self, player, direction=0, time_intval=2):
        """ Currently boats will only travel straight """
        speed = self.calculate_ship_speed(player, self.map.wind_speed, self.map.wind_dir)
        player.position[0] += math.sin(direction) * speed * time_intval
        player.position[1] -= math.cos(direction) * speed * time_intval

    def place_player(self, player):
        """ Places each player 110m apart. This is used when we initially spawn ships """
        player.position[0] = self.last_x
        player.position[1] = self.y / 2
        self.last_x = self.last_x + 110

    def calculate_ship_speed(self, player, wind_speed, wind_direction):

        theta = player.heading - (wind_direction * math.pi / 180)
        alpha = player.ship.max_angle_in_rads() - math.pi / 2

        if math.pi / 2 >= theta >= 0 or 2 * math.pi >= theta >= 3 * math.pi / 2:
            speed = player.ship.sails * ((player.ship.max_ratio * wind_speed - wind_speed) *
                    math.fabs(math.sin(theta)) + wind_speed)
        elif math.pi / 2 + alpha >= theta > math.pi / 2:
            speed = player.ship.sails * (0.5 * (player.ship.max_ratio * wind_speed *
                    math.cos((math.pi / alpha) * (theta - (math.pi / 2))) +
                    max_ratio * wind_speed))
        elif 3 * math.pi / 2 + 2 * alpha > theta >= 3 * math.pi / 2 - alpha:
            speed = player.ship.sails * (0.5 * (player.ship.max_ratio * wind_speed *
                    math.cos((math.pi / alpha) * (theta - (3 * math.pi / 2 + 2 * alpha))) +
                    player.ship.max_ratio * wind_speed))
        else:
            speed = 0

        return speed

    def change_heading(self, player, direction):
        """ Changes the heading of a player given a degree (0-359) """
        if 180 >= direction >= -180:
            player.heading = direction

    def set_sails(self, player, sails):
        """ Sets the sail ratio between 0.0 and 1.0 """
        if 0.0 <= float(sails) <= 1.0:
            player.ship.sails = float(sails)

    def turn_radius(self, player):
        return player.ship_speed / player.ship.angular_velocity()
