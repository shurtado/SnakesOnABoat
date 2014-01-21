""" This is the Module for Player Class """

class PlayerStatus(object):
    """ This class is used as an Enum type to identify the status of each player
        in the game """
    DEFEATED = "Defeated"
    WON = "Won"
    SURRENDERED = "Surrendered"
    PLAYING = "Playing"
    SUNK = "Sunk"
    GROUND = "Ground"
    ON_FIRE = "On Fire"
    ADRIFT = "a drift" 

class Player(object):
    """ This Player class represents the player, the ship the player has, the position,
        player name, etc. Will be expanded to add teams later """

    def __init__(self, client):
        self.client = client
        self.name = ""
        self.id = self.client.id
        self.position = [0, 0]
        self.ship_speed = 0
        self.ship = None
        self.heading = 0
        self.player_state = PlayerStatus.PLAYING

    def add_ship(self, ship):
        self.ship = ship

    def update_state(self, state, ID):
	self.player_state = state
	self.id = ID

	
    def update_position(self, position):
        self.position = position

    def in_bounds(self):
        pass #check if ship has gone past boundaries of map
