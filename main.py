"""
main.py - The entry point into the game. This runs the main game loop.
"""

import pygame
import pygame.time
import pygame.key
import pygame.mouse
import pygame.transform
import sys
import os

import gamemap
import gamedata
import userinterface
import enemymanager
import towermgr
import camera

from effects import EffectsManager

from vector import Vector, toVector

"""
The dimensions for the screen. These should remain constant.
"""
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

"""
The max number of frames per second for the game.
"""
MAX_FPS = 60

"""
The game clock
"""
GameClock = None

"""
The title of the game. This should remain constant.
"""
TITLE = "Defensive Design"


# TODO: Put this stuff into a settings system.

# Keys for scrolling the screen.
# Dict for mapping keypresses to the direction they should move the screen.
# We should add some more extensible system for this later, but this will do for now.
KEYPRESS_SCROLL_MAP = {
        # Arrow keys.
        pygame.K_UP: (0, -1),
        pygame.K_DOWN: (0, 1),
        pygame.K_LEFT: (-1, 0),
        pygame.K_RIGHT: (1, 0),

        # WASD
        pygame.K_w: (0, -1),
        pygame.K_s: (0, 1),
        pygame.K_a: (-1, 0),
        pygame.K_d: (1, 0),
        }

# Another hacky dict for zoom keys.
# I really need to refactor this module...
KEYS_ZOOM_VIEW = {
        # PageUp/PageDown
        pygame.K_PAGEUP: 1,
        pygame.K_PAGEDOWN: -1,

        # Plus/Minus
        pygame.K_PLUS: 1,
        pygame.K_MINUS: -1,
        }

# Maps number keys to tower selection.
# Yeah, it's more hacky dicts.
KEYS_TOWER_SELECT = {
        pygame.K_1: 1,
        pygame.K_2: 2,
        pygame.K_3: 3,
        pygame.K_4: 4,
        pygame.K_5: 5,
        pygame.K_6: 6,
        pygame.K_7: 7,
        pygame.K_8: 8,
        pygame.K_9: 9,
        pygame.K_0: 10,
        }

# Screen scrolling speed in pixels per tick.
SCROLL_SPEED = 30

# Zoom speed
ZOOM_SPEED = 0.05

ZOOM_MIN = 0.2
ZOOM_MAX = 1.5

class Game(object):
    """
    The main game object.
    Holds all the stuff.
    """
    def __init__(self, map_name):
        """
        Initializes a new game object with the given map name.
        """
        # Set the title of the game.
        pygame.display.set_caption(TITLE)

        # Set up a new window.
        self.screen_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Load the map.
        self.map = gamemap.GameMap(map_name)
        
        # Set up the UI.
        self.ui = userinterface.UserInterface(self)

        # Initialize the enemy manager.
        self.enemy_mgr = enemymanager.EnemyManager(toVector(self.map.getTileSize()))

        # Initialize the tower manager.
        self.tower_mgr = towermgr.TowerManager(self)

        # Initialzie the effects manager.
        self.fx_mgr = EffectsManager(self)

        # Initialize the game clock
        self.clock = pygame.time.Clock()

        self.camera = camera.Camera(self.map.getMapSize(), (SCREEN_WIDTH, SCREEN_HEIGHT))

        # We'll have 3 surfaces, the UI surface, the effects surface, and the game surface.
        # The game surface will be for drawing the ingame stuff. It'll be translated based on camera position.
        # The UI surface will be for drawing the UI.
        # The game surface will be for drawing ingame things like turrets and enemies.
        # The effects surface will be for drawing effects such as bullet lines and explosions.
        self.game_surface = pygame.Surface(self.map.getMapSize());
        self.fx_surface = pygame.Surface(self.map.getMapSize(), flags=pygame.SRCALPHA);
        self.ui_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), flags=pygame.SRCALPHA);

        # If False, the main loop will stop running.
        self.running = False

        # If True, the game logic tick will stop and things will pause.
        # NOT CURRENTLY IMPLEMENTED. BREAKS ALL THE THINGS
        self.paused = False

        self.data = gamedata.GameData()

        self.last_tick = 0


    def main(self):
        """
        Starts the main game loop.
        """
        running = True
        while (running):
            # Handle the event queue
            event = pygame.event.poll()

            # The event queue returns an event of type NOEVENT if the queue is empty
            while event.type != pygame.NOEVENT:
                self.handleEvent(event)
                event = pygame.event.poll()

            # Delete anything already on the surface.
            self.screen_surface.fill((0, 0, 0))

            # Logic tick stuff.
            self.tick()

            # Draw the things.
            self.draw()
            
            # Flip display stuff.
            pygame.display.flip()

            # Maintain dat framerate.
            self.clock.tick(MAX_FPS)

    def quit(self):
        """
        Sets self.running to false, ending the main loop and closing the game.
        Does not quit pygame or anything.
        """
        self.running = False


    def tick(self):
        """
        Performs a single logic tick.
        This means updating the camera position, UI status, 
        and the game logic.
        """
        # TODO: Pass time delta to all the update functions.
        current_tick = pygame.time.get_ticks()
        delta = current_tick - self.last_tick if self.last_tick >= 0 else 0
        self.last_tick = current_tick

        # Update the enemies
        livesLost = self.enemy_mgr.update(self)
        self.data.lives -= livesLost

        # Update towers
        self.tower_mgr.update()

        # Update effects
        self.fx_mgr.update(delta)

        # First, update the camera.
        for key, direction in KEYPRESS_SCROLL_MAP.iteritems():
            if pygame.key.get_pressed()[key]:
                self.camera.move((direction[0] * SCROLL_SPEED, direction[1] * SCROLL_SPEED))
#         for key, zoomfactor in KEYS_ZOOM_VIEW.iteritems():
#             if pygame.key.get_pressed()[key]:
#                 self.camera.zoom(zoomfactor * ZOOM_SPEED * (self.camera.getZoom()))
        self.camera.tickUpdate()

        mouse1, mouse2, mouse3 = pygame.mouse.get_pressed()
        if mouse1:
            position = self.camera.toGameCoordinates(pygame.mouse.get_pos())
            self.ui.towerPlacePos = self.map.getTileCoordinates(position)

        # Update the UI
        self.ui.update(self.data)

    def draw(self):
        """
        Draws the game and UI.
        """
        # Clear the effects surface.
        self.fx_surface.fill(pygame.Color(0, 0, 0, 0))

        # Draw the map
        self.map.draw(self.game_surface)

        # Draw the enemies
        self.enemy_mgr.draw(self.game_surface)

        # Draw the towers
        self.tower_mgr.draw(self.game_surface, self.fx_surface)

        # Draw effects
        self.fx_mgr.draw(self.game_surface, self.fx_surface, self.ui_surface)

        # Clear the UI surface to transparent and then draw the UI
        self.ui_surface.fill(pygame.Color(0, 0, 0, 0))
        self.ui.draw(self.ui_surface, self.game_surface, self.fx_surface)

        # Blit the effects surface onto the game surface.
        self.game_surface.blit(self.fx_surface, (0, 0))

        # Now, we draw the game and UI surfaces onto the screen.
        self.screen_surface.blit(pygame.transform.scale(self.game_surface, self.camera.getSurfaceSize()), self.camera.getSurfacePos())

        self.screen_surface.blit(self.ui_surface, (0, 0))


    def enemyKilled(self, entity):
        """
        Called when an enemy is killed.
        """
        # TODO: Maybe use events for this?
        self.data.resources += entity.resources


    def handleEvent(self, event):
        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            self.handleKeyEvent(event)
        elif event.type == pygame.QUIT:
            self.quit()
        else:
            self.enemy_mgr.spawnEnemy(event, self.map.getStartingTile())
        
    def handleKeyEvent(self, event):
        if event.type == pygame.KEYDOWN:
            # If the escape key has been pressed, close the tower selection menu.
            if event.key == pygame.K_ESCAPE:
                self.ui.towerPlacePos = None
        elif event.key in KEYS_TOWER_SELECT:
            if self.ui.towerPlacePos != None:
                types = self.tower_mgr.getTowerTypes()
                selected = KEYS_TOWER_SELECT[event.key]-1
                if selected < len(types) and self.data.resources >= types[selected].cost:
                    self.tower_mgr.addTower(self.tower_mgr.getTowerTypes()[selected].createTower(self, self.ui.towerPlacePos))
                    self.data.resources -= types[selected].cost
                    self.ui.towerPlacePos = None
        else:
            if(event.type == pygame.KEYUP):
                return # TODO: Add stuff for key up events here

def run():
    pygame.init()
    # One global game object.
    global MainGame
    MainGame = Game("map1")
    MainGame.main()
    pygame.quit()

if __name__ == "__main__":
    run()

