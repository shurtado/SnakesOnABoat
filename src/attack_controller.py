""" This is the module for our Attack controller """
""" Created by Michael Delong for Snakes On a Boat server """

import math

class AttackController(object):

    def __init__(self, distance=500):
        self.max_distance = distance

    def fire_cannon(self, p1, p2):
        """ Fires a single cannon; p1 is the firing player, and fires on p2 """
        if self.in_range(p1, p2):   #fire if ships are in range
            self.calculate_damage(p2, 1)
            if p1.position[0] < p2.position[0]:
                return 'S'
            else:
                return 'P'
        else:
            return False

    def fire_broadside(self, p1, p2):
        """ Fires a broadside; player p1 fires on player p2 """
        if self.in_range(p1, p2):   # fire if ships are in range
            self.calculate_damage(p2, p1.ship.broadside_damage())
            if p1.position[0] < p2.position[0]:
                return 'S'
            else:
                return 'P'
        else:
            return False

    def in_range(self, p1, p2):
        """ Determines if two players are within firing range of each other """

        # calculate horizontal and vertical distances between ships
        xdist = abs(p1.position[0] - p2.position[0])
        ydist = abs(p1.position[1] - p2.position[1])
        distance = math.sqrt((xdist * xdist) + (ydist * ydist)) # calculate true distance between ships
        return distance <= self.max_distance

    def calculate_damage(self, player, damage):
        """ Calculates the damage done to a player, and updates player hitpoints """

        # update hitpoints and maximum speed for player
        player.ship.take_damage(damage)
        self.update_max_speed(player, damage)

    def alive(self, player):
        """ Used to determine if a player has been destroyed """

        return player.ship.hit_points > 0

    def surrender(self, player):
        """" player requests surrender """

        player.ship.hit_points = 0

    def update_max_speed(self, player, damage):
        """ Updates the maximum ship speed of player based on damage received """

        player.ship.max_speed = player.ship.max_speed - damage
        if player.ship.max_speed < 0:  player.ship.max_speed = 0 # speed can't be less than 0

