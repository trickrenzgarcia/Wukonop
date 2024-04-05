#!/usr/bin/env python
import pygame
from pygame.locals import *
# Remember: make enemies BIGGER so there can be less on-screen to drag out battles
import sys
import os
import random
import math

"""Give the player momentum. Have him slow down over time upon releasing the key"""


"""Give the player a howl ability and have it consume MP. When used, create a small 1 frame rect/circle around
the player that stuns all enemies for a couple seconds. Let it trigger other events too, such
as causing some walls to crumble"""



# WORK ON BIGGER ENEMIES
""" Make common enemies that are large. e.g., something big that shoots a couple short parallel lasers.
The enemies takes a load of hits, so you have to hop between the beams whilst using your flames"""



"""Have phantoms follow behind the player. Just have copies the the player sprites in a purplish-blue
 with 50% opactity."""


pygame.init()
pygame.display.set_caption("Wukonop")
os.chdir(os.path.abspath(os.path.dirname(sys.argv[0])))
clock = pygame.time.Clock()
dfltFont = pygame.font.SysFont('Arial', 20)
flameSound = pygame.mixer.Sound('Flame.wav')
flameSound.set_volume(.2)
hitSound = pygame.mixer.Sound('Hit.wav')
hitSound.set_volume(.2)

screen = pygame.display.set_mode((450, 300), 0, 32)

blocks = []
backgrounds = []
spells = []
enemySpells = []
enemies = []

def fontTasks(text, pos, color = (20, 20, 20)):
	readyText = dfltFont.render(text, True, color)
	screen.blit(readyText, (pos[0], pos[1]))
	
	
# Fade into a level. Start with black and go to white
class Transition():
	def __init__(self):
		self.maxTime = 80
		self.time = self.maxTime
		self.proceed = False
	def render(self):
		for event in pygame.event.get():
			if event.type == QUIT:
				sys.exit()
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					pygame.quit()
					sys.exit()
				if self.time <= 10 and event.key == K_SPACE:
					self.proceed = True
		screen.fill(((255-self.time*3),(255-self.time*3),(255-self.time*3)))
		fontTasks("Entering level %d" %player.in_level, (0, 250))
		# This line of text will fade in too
		fontTasks("Press space", (0, 275), (self.time, self.time, self.time))
		# When the fade to white is nearly over and the user presses Space, proceed to the level
		if self.proceed == True or self.time > 10:
			self.time -= 1
transition = Transition()

class Background():
	def __init__(self):
		self.image = pygame.image.load('BG.jpg').convert()
		self.x = 0
	def render(self):
		screen.blit(self.image, (self.x, 0))
		
BackG = Background()

#Clear out level and load a new one
def getRGB(level_num):
	BackG.x = 0
	del blocks[:], enemies[:], backgrounds[:], spells[:], enemySpells[:]
	# Make sure player isn't moving and nullify his hit status; restore all stats to default
	player.dx = player.oldDX= player.hitBool = 0
	player.MP = player.maxMP
	player.x, player.y = 225, 100
	player.updateRect()
	transition.time = transition.maxTime # Reset trans time, which starts transition
	transition.proceed = False
	levelimg = pygame.image.load('Level%d.png'%level_num).convert_alpha()
	for x in range(levelimg.get_width()):
		for y in range(levelimg.get_height()):
			color = levelimg.get_at((x, y))
			if player.in_level <= 3:
				if color == (255, 255, 255, 255):
					blocks.append(Block(((x*20)-2, y*16), "Log"))
				elif color == (200, 200, 200, 255):
					blocks.append(Block((x*20, y*16), "LogUp"))
				elif color == (255, 0, 0, 255):
					blocks.append(Border((x*20, y*16)))
				elif color == (0, 100, 0, 255):
					blocks.append(BurnableBlock((x*20, y*16)))
				elif color == (255, 0, 255, 255):
					enemies.append(Ghost((x*20, y*16)))
				elif color == (0, 255, 255, 255):
					enemies.append(Cell((x*20, y*16)))
				elif color == (255, 255, 0, 255):
					enemies.append(Runner((x*20, y*16)))
				elif color == (0, 255, 0, 255):
					backgrounds.append(Block((x*20, y*16), 'Leaves'))

class Block():
	def __init__(self, pos, imgType = None):
		self.x = pos[0]
		self.y = pos[1]
		self.offset = (0, 0)
		self.rect = pygame.Rect(self.x, self.y, 20, 16)
		self.color = (0, 0, 0)
		if imgType == 'Leaves':
			self.image = pygame.image.load('Leaves%d.png'%random.randint(0, 1)).convert_alpha()
		elif imgType != 'Leaves' and imgType != None:
			self.image = pygame.image.load('%s.png'%imgType).convert_alpha()
		self.name = str(self.__class__)[9:] #Get the class's name
	def updateRect(self):
		self.rect.x, self.rect.y = self.x, self.y
	def render(self):
		if hasattr(self, 'image'):
			screen.blit(self.image, (self.x, self.y))
		else:
			# Handle rendering for objects without image attribute
			pass

class BurnableBlock(Block):
	def __init__(self, pos):
		Block.__init__(self, pos)
		self.image = pygame.image.load('Shrub.png').convert_alpha()
		self.onFire = False
		self.timer = 20 # when onFire == 1, count down and remove block when 0
	def burn(self):
		if self.onFire == False:
			self.onFire = True
		if self.timer == 10:
			self.image = pygame.image.load('Flame.png').convert_alpha()
		self.timer -= 1
		
					
class Border(Block):
	def __init__(self, pos):
		Block.__init__(self, pos)
		

class Player(Block):
	def __init__(self, pos):
		Block.__init__(self, pos)
		self.rect = pygame.Rect(self.x, self.y, 14, 14)
		self.image = pygame.image.load('Log.png').convert_alpha()
		self.offset = (-4, 0)
		self.orig_y = self.y
		self.dx = 0
		self.oldDX = self.dx
		self.dy = 0
		self.direction = 1
		self.MP = 2000.
		self.maxMP = self.MP
		self.in_level = 1
		self.maxHeight = 60
		self.fallspeed = 0
		self.falling = False
		self.hitBool = 0
		self.A_Down = 0
		self.D_Down = 0
	# If hit, the player will be knocked in the opposite direction he was last moving
	def gotHit(self):
		self.MP -= 700
		self.hitBool = 1
		self.oldDX = self.dx
		if self.direction == 1:
			self.dx = -7.5
		else:
			self.dx = 7.5
	def move(self):
		# If you've been hit, forcefully slide back and then restore former speed
		if self.hitBool != 0:
			if self.dx > 0: self.dx -= .5
			if self.dx < 0: self.dx += .5
			if self.dx == 0:
				self.hitBool = 0
				self.dx = self.oldDX
		if self.dx > 0:
			self.direction = 1
		elif self.dx < 0:
			self.direction = -1
		# The player's x position never changes
		# Instead, we move blocks the opposite direction
		# If you collide with a block whilst moving on the x axis, undo the block movement
		BackG.x -= (self.dx * .15)
		for bg in backgrounds:
			bg.x -= self.dx
			bg.updateRect()
		for block in blocks:
			block.x -= self.dx
			block.updateRect()
			if self.rect.colliderect(block.rect):
				# Progress to next level upon hitting the border
				if block.name == "Border":
					self.in_level += 1
					getRGB(self.in_level)
				# IMPORTANT: when you hit a wall, make sure enemies won't also have your
				# x speed subtracted. Otherwise, they'll fly off screen because they're
				# still told to move opposite of you (although you wouldn't be moving!)
				# This applies to some spells too for enemy in enemies
				for enemy in enemies:
					enemy.move_x = False
				for spell in spells:
					if spell.name != "Leaf":
						spell.move_x = False
				for enemySpell in enemySpells:
					enemySpell.move_x = False
				for bg in backgrounds:
					bg.x += self.dx
					bg.updateRect()
				for each_block in blocks:
					each_block.x += self.dx
					each_block.updateRect()
				BackG.x += (self.dx * .15)
		self.gravity()
	def gravity(self):
		# Y axis movement, however, is normal.
		# Only the player moves Y-wise, so if he hits a block whilst falling,
		# only he gets pushed up; the block doesn't move.
		if self.falling == False:
			self.y += self.dy
			self.updateRect()
			self.fallspeed = 1
			if self.rect.y < self.orig_y-self.maxHeight:
				self.falling = True
				self.dy = 0
			for block in blocks:
				#If you bump into a platform above you, fall
				if self.rect.colliderect(block.rect):
					self.rect.top = block.rect.bottom
					self.y = self.rect.y
					self.falling = True
					self.dy = 0
					break
				#If you walk off a platform, fall
				if self.rect.y == self.orig_y and self.rect.colliderect(block.rect) == False:
					self.falling = True
		#If falling... fall. If touching the ground, bring back ability to jump
		if self.falling == True:
			# Fall progressively faster
			self.y += self.fallspeed
			self.fallspeed += .14
			self.updateRect()
			#If you're on a platform, cease falling
			for block in blocks:
				if self.rect.colliderect(block.rect):
					self.rect.bottom = block.rect.top
					self.fallspeed = 0
					self.y = self.rect.y
					self.falling = False
					self.orig_y = self.rect.y
					break

# Leaf shield. Does damage, absorbs shots. Spins in front of and behind player.
class Leaf(Block):
	def __init__(self):
		# Leaves are spawned somewhere near the player at a random speed
		Block.__init__(self, (player.x+random.randint(-4, 4), player.y))
		self.move_x = True #Maybe winds will be able to stop leaves from moving?
		self.dx = random.choice([3.5, 3.9, 4.4, 4.6])*random.choice([-1, 1])
		self.dy = random.choice([-1.1, 1.1])
		self.new_y = 0
		self.color = (0, 130, 50)
		self.time = 300
		self.image = pygame.image.load('Leaf%d.png'%random.randint(0,2)).convert_alpha()
		self.offset = (0, -4)
		self.degrees = random.randint(0, 355)
		self.image = pygame.transform.rotate(self.image, self.degrees)
	def move(self):
		if self.x <= player.x - 45:
			self.x = player.x - 43
			self.dx = -self.dx
			self.dy = -self.dy
		if self.x >= player.x + 45:
			self.x = player.x + 43
			self.dx = -self.dx
			self.dy = -self.dy
		self.x += self.dx
		#We only add dy to new_y. We then add this to player.y so the leaves stay with the player
		self.new_y += self.dy 
		self.y = player.y + self.new_y
		self.time -= 1
		self.updateRect()

# Flame that goes straight in front of the player. Gets larger over time and thus a wider area of damage
class Flame(Block):
	def __init__(self):
		if player.direction == 1:
			self.x = player.x + 16
			self.dx = 4.9
		else:
			self.x = player.x
			self.dx = -4.9
		Block.__init__(self, (self.x, player.y-5))
		self.move_x = True
		self.time = 42
		self.image = pygame.image.load('Flame.png').convert_alpha()
		self.origImage = self.image
		self.height = self.image.get_height()
		self.width = self.image.get_width()
		self.sizeScale = 0.0 #How much larger the sprite will be each rendering
	def move(self):
		self.x += self.dx
		if self.move_x == True:
			self.x -= player.dx
		self.y -= .5
		self.updateRect()
		# Make the sprite .2 pixels bigger each direction each frame
		self.image = pygame.transform.scale(self.origImage, (self.width + int(self.sizeScale),\
		 self.height + int(self.sizeScale)))
		self.sizeScale += .27
		self.time -= 1
		self.rect = pygame.Rect(self.x, self.y, self.width+int(self.sizeScale), self.height+int(self.sizeScale))
		self.move_x = True


class Ghost(Block):
	def __init__(self, pos):
		Block.__init__(self, pos)
		self.color = (100, 0, 130)
		self.stunTime = 0
		self.life = 4
		self.dx = random.choice([.5, .7, .9])
		self.dy = random.choice([.5, .7, .9]) 
		self.screen_x = screen.get_width()
		self.image = pygame.image.load('Ghost.png').convert_alpha()
		self.rect = pygame.Rect(self.x, self.y, self.image.get_width()-10, self.image.get_height()-10)
		self.offset = (-4, -8)
		self.move_x = True
	def move(self):
		if self.stunTime <= 0:
			if self.x < self.screen_x + 40 and self.x > -40:
				if player.x < self.x:
					self.x -= self.dx
				if player.x > self.x:
					self.x += self.dx
				# Ghost goes down as far as the player's y - 3
				if player.y > self.y+3:
					self.y += self.dy
				if player.y < self.y:
					self.y -= self.dy
		# Also subtract the player's x movement so it moves with the screen, but only when the player isn't
		# colliding with a wall on during x movement
		if self.move_x == True:
			self.x -= player.dx
		self.updateRect()
		self.move_x = True


# Fast enemies that chase after the player
class Runner(Player):
	def __init__(self, pos):
		Player.__init__(self, pos)
		self.dx = 0
		self.stunTime = 0
		self.maxHeight = 40
		self.falling = True
		self.image = pygame.image.load('Flame.png').convert_alpha()
		self.life = 3
		self.move_x = True
		self.attackTime = 0
	# We're just using the player's gravity function and a modification of his move function
	# Instead of having blocks move away like when the player bumps them, the Runner gets pushed away
	def move(self):
		if self.stunTime <= 0:
			if player.x < self.x and self.x < 455:
				self.dx = -2
				self.attackTime += 1
			elif player.x >= self.x and self.x > 0:
				self.dx = 2
				self.attackTime += 1
			# Attack every 85 frames
			if self.attackTime == 55:
				self.attack()
			self.x += self.dx
		if self.move_x == True:
			self.x -= player.dx
		self.updateRect()
		# Only check for collision with walls if actually moving
		if self.dx != 0:
			for block in blocks:
				if self.rect.colliderect(block.rect):
					self.dy = -2.5
					if self.dx < 0:
						self.rect.left = block.rect.right
					elif self.dx > 0:
						self.rect.right = block.rect.left
					self.x = self.rect.x
		self.move_x = True
		self.gravity()
	def attack(self):
		self.attackTime = 0
		enemySpells.append(Shot((self.x, self.y)))


#Make the boss explode into a mess of CONFETTI when defeated
class Cell(Block):
	def __init__(self, pos):
		Block.__init__(self, pos)
		self.image = pygame.image.load('Nucleus.png').convert_alpha()
		self.membraneIMG = pygame.image.load('Cell.png').convert_alpha()
		self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
		self.life = 80
		self.move_x = True
		self.orig_y = 0
		self.dy = 1.2
		self.dx = 0
		self.attackTime = 0
	def move(self):
		self.attackTime += 1
		if self.attackTime == 60:
			self.attack()
		if self.orig_y > 40:
			self.dy = -1.2
		if self.orig_y < -20:
			self.dy = 1.2
		self.y += self.dy
		self.orig_y += self.dy
		if self.move_x == True:
			self.x -= player.dx
		self.updateRect()
		self.move_x = True
	def render(self):
		screen.blit(self.image, (self.x, self.y))
		screen.blit(self.membraneIMG, (self.x - 110, self.y - 90))
	# Attacking creates an array of parallel lasers and may randomly spawn a ghost
	def attack(self):
		self.attackTime = 0
		if self.x < player.x:
			bulletDY = 4
		else:
			bulletDY = -4
		for i in range(-3, 3):
			enemySpells.append(Laser((self.x, self.y+(i*54)), bulletDY))
		if random.randint(0, 8) == 0:
			enemies.append(Ghost((self.x+random.randint(0, 20), self.y+random.randint(-40, 40))))
		
		

class Shot(Block):
	def __init__(self, pos):
		Block.__init__(self, pos)
		self.move_x = True
		if self.x < player.x:
			self.dx = 3.1
		else:
			self.dx = -3.1
		self.dy = math.sin(math.radians(player.y-self.y))*1.1
		self.image = pygame.image.load('Shot.png').convert_alpha()
		self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
	def move(self):
		self.x += self.dx
		self.y += self.dy
		if self.move_x == True:
			self.x -= player.dx
		self.updateRect()
		self.move_x = True

class Laser(Block):
	def __init__(self, pos, dx = 0, dy = 0):
		Block.__init__(self, pos)
		self.dx = dx
		self.dy = dy
		self.move_x = True
		self.image = pygame.image.load('Shot.png').convert_alpha()
	def move(self):
		if self.move_x == True:
			self.x -= player.dx
		self.x += self.dx
		self.y += self.dy
		self.move_x = True
		self.updateRect()
		

player = Player((225, 100))

getRGB(1)

def inGame():
	screen.fill((0, 90, 70))
	for event in pygame.event.get():
		if event.type == QUIT:
			sys.exit()
		if event.type == KEYDOWN:
			if event.key == K_ESCAPE:
				pygame.quit()
				sys.exit()
			if event.key == K_SPACE:
				if player.falling == False:
					player.dy = -3.4
			if event.key == K_p:
				if player.MP >= 700:
					player.MP -= 700
					for i in range(13): spells.append(Leaf())
			if event.key == K_o:
				if player.MP >= 70:
					player.MP -= 70
					spells.append(Flame())
					flameSound.play()
			if event.key == K_d:
				player.D_Down = 1
				player.dx = 3.8
			if event.key == K_a:
				player.A_Down = 1
				player.dx = -3.8
			if event.key == K_n:
				getRGB(player.in_level)
		if event.type == KEYUP:
			if event.key == K_SPACE:
				if player.dy < 0:
					player.dy = 0
					player.falling = True
			if event.key == K_d:
				player.D_Down = 0
			if event.key == K_a:
				player.A_Down = 0
			if player.A_Down == 0 and player.D_Down == 0:
				player.dx = 0
				player.oldDX = 0
	
	# move the player first so everything moves with it
	# then render the player AFTER the BGs so it's on top of them
	player.move() 
	
	screen.blit(BackG.image, (BackG.x, 0))
	for bg in backgrounds:
		bg.render()
		
	player.render()
	
	for block in blocks:
		if block.name != "Border":
			block.render()
		
		for spell in spells:
			# Ignite then remove flammable blocks when hit with a flame
			if spell.name == "Flame" and spell.rect.colliderect(block.rect):
				spells.remove(spell)
				if block.name == "BurnableBlock":
					block.burn()
		
		if block.name == 'BurnableBlock' and block.onFire == True:
			block.burn()
			if block.timer < 0:
				blocks.remove(block)
		
	# Your spells.
	for spell in spells:
		spell.move()
		spell.updateRect()
		spell.render()
		if spell.name == "Leaf":
			for enemySpell in enemySpells:
				if enemySpell.rect.colliderect(spell.rect):
					enemySpells.remove(enemySpell)
		if spell.time <= 0:
			spells.remove(spell)
	
	for enemySpell in enemySpells:
		enemySpell.move()
		enemySpell.render()
		try:
			if enemySpell.rect.colliderect(player.rect):
				player.MP -= 180
				enemySpells.remove(enemySpell)
			if enemySpell.x < -20 or enemySpell.x > 490:
				enemySpells.remove(enemySpell)
		except:
			pass
	# Move enemies, render them, have them attack, etc	
	for enemy in enemies:
		enemy.move()
		enemy.render()
		if enemy.rect.colliderect(player.rect):
			enemy.life -= 10
			player.gotHit()
			
		try:
			for spell in spells:
				if spell.rect.colliderect(enemy.rect):
					hitSound.play()
					# Flame spells also push back enemies
					# Maybe this can be used for invincible enemies...?
					if spell.name == "Flame":
						if enemy.name != "Cell":
							enemy.x += spell.dx*3
							enemy.updateRect()
						enemy.life -= 3
					else:
						enemy.life -= 1
					spells.remove(spell)
					# Give the player MP each time he hits an enemy. This allows him to earn extra
					player.MP += 20
		except: pass
		if enemy.life <= 0 or enemy.x < -90:
			enemies.remove(enemy)
			
	if player.MP < player.maxMP:
		player.MP += 1
	if player.MP < 0 or player.y > screen.get_height() + 10:
		getRGB(player.in_level)
		
	pygame.draw.rect(screen, (0, 0, 0), (20, 2, 200, 20))
	pygame.draw.rect(screen, (220, 160, 0), (22, 4, 196*(player.MP/player.maxMP), 16))


while True:
	if transition.time > 1:
		transition.render()
	else:
		inGame()
	clock.tick(60)
	pygame.display.flip()