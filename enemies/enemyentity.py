'''
Created on Nov 16, 2013

@author: AbrarSyed
'''

import enemybase
import pygame
import maptile

class EnemyEntity():
    '''
    The class that represents every entity
    properties:
    type (instance of EnemyBase)
    speed
    health
    loc_x
    loc_y
    direction
    alive
    dot_time_left
    dot_damage
    '''

    def __init__(self, enemy_type, spritegroup):
        '''
        creates a new eneity of the specifid enemy_type.
        '''
        self.speed = enemy_type.defSpeed
        self.health = enemy_type.defHealth
        self.type = enemy_type
        self.sprite = pygame.sprite.Sprite()
        spritegroup.add(self.sprite)
        
    def spawn(self, game_map, loc_x, loc_y):
        '''
        actually spawns the entity with the given type.
        '''
        self.loc_x = loc_x
        self.loc_y = loc_y
        self.path_index = 0
        self.dot_active = False
        self.dot_time = 0
        self.dot_damage = 0
        self.alive = True
        self.map = game_map
        size = game_map.getTileSize()
        self.sprite.rect = pygame.Rect(loc_x, loc_y, size[0], size[1])
        self.needs_dir_update = True
        
    def update(self):
        type.update(self)
    
    def applyDot(self):
        if self.dot_time_left <= 0 :
            return
        
        self.dot_time_left -= 1
        self.damage(self.dot_damage)
        
    def move(self):
        '''
        Moves the entity based on speed, and location
        '''
        if self.needs_dir_update :
            self.calcDirection()
        self.sprite.image = self.images[self.direction]
        deltaX = self.speed * enemybase.DIRECTION_MATRIX[self.direction][1];
        deltaY = self.speed * enemybase.DIRECTION_MATRIX[self.direction][1];
        self.loc_x += deltaX
        self.loc_y += deltaY
        self.sprite.rect = self.sprite.rect.move(deltaX, deltaY)
        self.updatePathLoc()
    
    def calcDirection(self):
        # calculate the direction
        current = self.getPathLoc()
        nextLoc = self.getNextLoc()
        delta = (current[0] - nextLoc[0], current[1] - nextLoc[1])
        for direct, val in enemybase.DIRECTION_MATRIX.iteritems() :
            if val == delta :
                self.needs_dir_update = False
                return direct;
            
    def updatePathLoc(self):
        current = self.getPathLoc()
        nextLoc = self.getNextLoc()
        
        if map.getTileCoordinates((self.loc_x, self.loc_y)).getLoc() == current :
            # its in the same place it was.. thats fine.
            return
        
        # now we can safely assume, I hope.. that the entity is currently in the NEXT location
        
        # temp stuff...
        adder = enemybase.DIRECTION_MATRIX[self.direction]
        adder = (adder[0] * .5, adder[1] * .5)
        adder = (self.loc_x + adder[0], self.loc_y + adder[1])
        if map.getTileCoordinates(adder).getLoc() != nextLoc :
            self.path_index += 1
            self.needs_dir_update = True
        
    
    def getPathLoc(self):
        return map.path[self.path_index]
    
    def getNextLoc(self):
        return map.path[self.path_index + 1] 
        
    def damage(self, ammount):
        '''
        Damages the entity and sets its alive state
        '''
        if not self.alive :
            return
        
        self.health -= ammount
        
        if self.health <= 0 :
            self.health = 0
            self.alive = False
            self.type.onDeath()
        
    def dead(self):
        if(self.health <= 0):
            return True
        else:
            return False
    
    """
    Determines if the enemy is offscreen or not. This only
    returns true if all parts of the enemy are offscreen.
    """
    def offscreen(self, mapdata):
        tilesize = mapdata.getTileSize()
        mapsize = mapdata.getMapSize()
        coordinates = self.getCoordinates()
        if(coordinates[0] < -tilesize[0] or coordinates[0] > mapsize[0]):
            return True
        elif(coordinates[1] < -tilesize[1] or coordinates[1] > mapsize[1]):
            return True
        else:
            return False

    def getCoordinates(self):
        return (self.sprite.rect.left, self.sprite.rect.top)

    """
    Returns true if the enemy is at the destination.
    """
    def atDestination(self, mapdata):
        coordinates = self.getCoordinates()
        mapsize = mapdata.getMapSize()
        # Make sure the coordinates are valid
        if(coordinates[0] < 0 or coordinates[0] >= mapsize[0] or coordinates[1] < 0
           or coordinates[1] >= mapsize[1]):
            return False        
        tile_number = mapdata.getTileCoordinates(coordinates)
        if(mapdata.tiles[tile_number[0]][tile_number[1]].type == maptile.DESTINATION):
            return True
        else:
            return False

# A little trick so we can run the game from here in IDLE
if __name__ == '__main__':
    execfile("main.py")
