""" This is the module for our Game class """

import elixir
from random import choice
import sqlalchemy
import threading
import time

from twisted.internet import reactor
from twisted.python import log

from attack_controller import AttackController
from io_controller import IOController
from movement_controller import MovementController
from models import *
from player import Player
import settings

elixir.setup_all(True)

class Game(object):
    """ The Game class is responsible for delegating tasks to the appropriate controllers
        as well as storing Player information """

    def __init__(self, map, max_players):
        """ We initialize an action map that we use to automatically call the methods
            based on the attacks """
        self.actions = {'fireBroadside': self._fire_broadside,
                        'changeSpeed': self._change_speed,
                        'changeHeading': self._change_heading,
                        'gameSurrender': self._game_surrender}
        self.update_timeout = 0.5 # in seconds

        self.active_players = []
        self.inactive_players = []

        self.all_ships = Ship.query.all()
        try:
            self.map = Map.query.filter_by(name=map).one()
        except sqlalchemy.orm.exc.NoResultFound:
            self.map = Map(name=u"DEFAULT", x=1000, y=1000, wind_speed=10, wind_dir=0)

        self.io_controller = IOController()
        self.attack_controller = AttackController()
        self.movement_controller = MovementController(self.map)

        self.max_players = max_players

        self.response = None
        self.thread_started = False

    def send_message(self, client, message):
        """ This method takes a client (who sent the message) and the message they sent 

            This """
        try:
            parsed = self.io_controller.parse_message(message)
        except IndexError:
            return
        command = parsed['command']
        args = parsed['args']

        try:
            calling_player = [p for p in self.active_players if p.id == client.id][0]
        except IndexError:
            return "Player '%d' not found" % client.id

        try:
            return self.actions[command](calling_player, args)
        except KeyError:
            return "Command '%s' not found. '%s' in actions = %s" % (command, command,
                    command in self.actions)

    def run(self):
        """ This method starts a Thread, which updates the positions on all players """
        log.msg("Starting thread!")

        t = threading.Thread(target=self._update_pos)
        t.setDaemon(True)
        t.start()

    def _update_pos(self):
        """ This method is being run in a Thread. It is responsible for checking the
            clients list and updating all player positions in that list """
        log.msg("Starting update loop")
        while True:
            for p in self.active_players:
                self.movement_controller.update_position(p, 0, self.update_timeout)
                state_msg = self.io_controller.build_message({'command': 'shipState',
                    'args': [p.id, int(p.position[0]), int(p.position[1]), p.heading]})
                # send this message to all players
                for p in self.active_players + self.inactive_players:
                    log.msg("Sending client", p.id, "'", state_msg, "'")
                    reactor.callFromThread(p.client.transport.write, state_msg + "\n")
            time.sleep(self.update_timeout)

    def add_player(self, client):
        """ This method is responsible for creating a new client and wrapping it in
            a Player class """
        player = Player(client)
        self.movement_controller.place_player(player)
        player.add_ship(choice(self.all_ships))
        player.ship.sails = 0.0
        self.active_players.append(player)

        # send init data to client
        map_msg = self.io_controller.build_message({'command': 'mapSize',
            'args': [self.map.x, self.map.y]})
        wind_msg = self.io_controller.build_message({'command': 'wind',
            'args': [self.map.wind_speed, self.map.wind_dir]})
        player_ship_msg = self.io_controller.build_message({'command': 'playerShip',
            'args': [player.id, player.ship.max_theta, player.ship.turn_radius_factor,
                player.ship.max_ratio]})

        # send these messages to all players when they first connect
        client.broadcast(map_msg)
        client.broadcast(wind_msg)
        client.broadcast(player_ship_msg)

        other_players = [p for p in self.active_players if client.id != p.id]
        for p in other_players:
            other_ship_msg = self.io_controller.build_message({'command': 'otherShip',
                'args': [p.id, p.ship.max_theta, p.ship.turn_radius_factor,
                    p.ship.max_ratio]})
            client.broadcast(other_ship_msg)
        for p in other_players:
            other_ship_msg = self.io_controller.build_message({'command': 'otherShip',
                'args': [client.id, p.ship.max_theta, p.ship.turn_radius_factor,
                    p.ship.max_ratio]})
            p.client.broadcast(other_ship_msg)

        # Once we receive at least 1 player, start. Don't start again after
        if not self.thread_started and len(self.active_players) >= 2:
            self.run()
            self.thread_started = True

    def remove_player(self, client):
        """ This is responsible for finding the client with the client id and removing
            it from our clients list """
        to_remove = None
        for p in self.active_players:
            if p.id == client.id:
                to_remove = p
        self.active_players.remove(to_remove)

    def _fire_broadside(self, calling_player, args):
        """ Calculates a broadside attack from the calling_player to its target

            Returns the side that the firing player is firing from """
        try:
            target_player = [p for p in self.active_players if str(p.id) == args[0]][0]
        except IndexError:
            return

        side = self.attack_controller.fire_broadside(calling_player, target_player)
        return self.io_controller.build_message({'command': 'cannonsFired',
            'args': [calling_player.id, side]})

    def _change_speed(self, calling_player, args):
        """ Changes the speed of the calling_player ship and sends the new speed back to the client """
        self.movement_controller.set_sails(calling_player, args[0])
        return self.io_controller.build_message({'command': 'setSpeed',
            'args': [calling_player.id, calling_player.ship.sails]})

    def _change_heading(self, calling_player, args):
        """ Changes the heading of the calling_player and sends the new heading back to the client """
        self.movement_controller.change_heading(calling_player, int(args[0]))
        return self.io_controller.build_message({'command': 'setHeading',
            'args': [calling_player.id, calling_player.heading]})

    def _game_surrender(self, calling_player, args):
        """ Surrenders the calling_player and sending the ship status back to the client """
        self.surrender_player(calling_player)

        return self.io_controller.build_message({'command': 'gameFinished',
            'args': [calling_player.id]})

    def surrender_player(self, player):
        """ Removes the player from the global active players list """
        self.inactive_players.append(player)
        self.active_players.remove(player)
