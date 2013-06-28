import random, pygame, math, sys, os
import socket, select, re, ConfigParser

enemyPOS = ()

FPS = 20
SCREENWIDTH = 360
SCREENHEIGHT = 600

FONT = os.path.join('data','magic.ttf')

PADDING = 5
BORDER = 2

topHeight = 80
topRect = (PADDING, PADDING, SCREENWIDTH - PADDING * 2, topHeight)
botRect = (PADDING, PADDING * 2 + topRect[3], SCREENWIDTH - PADDING * 2, SCREENHEIGHT - topHeight - PADDING * 3)

WHITE = (255, 255, 255)
BLACK = (  0,   0,   0)
RED = (255,   0,   0)
GREEN = (  0, 255,   0)
DGREEN = (  0, 155,   0)
BLUE = (  0,   0, 255)
LGREY = (230, 240, 230)
DGREY = ( 50, 100,  50)

def main():
	global CLOCK, SCREEN, BACKGROUND, TARGET, ARROW, RUNNING, hit_list, enemyPOS
	
	pygame.mixer.pre_init(44100, -16, 2, 2048)
	pygame.init()
	CLOCK = pygame.time.Clock()
	SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
	pygame.display.set_caption("Hit'n'Miss")
	
	pygame.mixer.music.load(os.path.join('data','forest.wav'))
	pygame.mixer.music.set_volume(0.1)
	pygame.mixer.music.play(-1)
	
	BACKGROUND = pygame.image.load(os.path.join('data','tree.jpg'))
	TARGET = pygame.image.load(os.path.join('data','target.png'))
	ARROW = pygame.image.load(os.path.join('data','arrow.png'))
	
	if splashScreen():
		
		game = choiceScrolls('Single Player','Multi Player')
		
		if game == 'Single Player':
			Running = True
			
			while Running:
				enemyPOS = (random.randrange(botRect[0] + TARGET.get_width(), SCREENWIDTH - PADDING - TARGET.get_width()),
				random.randrange(botRect[1] + TARGET.get_width(), SCREENHEIGHT - PADDING - TARGET.get_width()))
				#print (enemyPOS)
				hit_list = []
				if runGame():
					if not winScreen():
						break
					again = choiceScrolls('Play Again','Quit')
					if again == "Quit" or not again:
						break
				else:
					break
		elif game == 'Multi Player':

			game = choiceScrolls('Client', 'Server')
			
			if game == 'Client' or game == 'Server':
				RUNNING = True
				
				while RUNNING:
					hit_list = []
					pos = setTarget(game)
					if pos:
						if runGame(pos):
							if not winScreen():
								break
							again = choiceScrolls('Play Again','Quit')
							if again == "Quit" or not again:
								break
						else:
							break
					else:
						break
	
	terminate()

def splashScreen():
	backRect = BACKGROUND.get_rect()
	
	logoBall = pygame.image.load(os.path.join('data','logo.png'))
	degrees = 0
	
	title = "Hit'n'Miss"
	
	titleFont = pygame.font.Font(FONT, 75)
	titleSurf = titleFont.render(title, True, DGREEN)
	titleRect = titleSurf.get_rect()
	titleRect.center = (SCREENWIDTH / 2, 250)
	
	message = "Click to continue..."
	
	messageFont = pygame.font.Font(FONT, 40)
	messageSurf = messageFont.render(message, True, WHITE)
	messageRect = messageSurf.get_rect()
	messageRect.center = (SCREENWIDTH/2, 550)
	
	while True:
		SCREEN.blit(BACKGROUND, (0,0))
		
		rotatedSurf = pygame.transform.rotate(logoBall, degrees)
		rotatedRect = rotatedSurf.get_rect()
		rotatedRect.center = (SCREENWIDTH / 2, 250)
		SCREEN.blit(rotatedSurf, rotatedRect)
		
		SCREEN.blit(titleSurf, titleRect)
		
		SCREEN.blit(messageSurf, messageRect)
		
		pygame.display.update()
		CLOCK.tick(FPS)
		
		degrees -= 2
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return False
			elif event.type == pygame.MOUSEBUTTONDOWN:
				return True

def choiceScrolls(message1, message2):
	backRect = BACKGROUND.get_rect()
	
	sign = pygame.image.load(os.path.join('data','sign1.png'))
	signRect = sign.get_rect()
	signRect.center = (SCREENWIDTH/2, SCREENHEIGHT/2 - 20)
	
	scroll = pygame.image.load(os.path.join('data','scroll.png'))
	scrollRect = scroll.get_rect()
	scrollRect.center = (SCREENWIDTH/2, SCREENHEIGHT/2)
	
	scrollRect2 = scroll.get_rect()
	scrollRect2.center = (SCREENWIDTH/2, SCREENHEIGHT/2 + 130)
	
	messageFont = pygame.font.Font(FONT, 35)
	
	scrollCol = BLACK
	scroll2Col = BLACK
	
	click = pygame.mixer.Sound(os.path.join('data','click.wav'))
	
	while True:
		messageSurf1 = messageFont.render(message1, True, scrollCol)
		messageSurf2 = messageFont.render(message2, True, scroll2Col)
		messageRect1 = messageSurf1.get_rect()
		messageRect2 = messageSurf2.get_rect()
		messageRect1.center = (SCREENWIDTH/2, SCREENHEIGHT/2)
		messageRect2.center = (SCREENWIDTH/2, SCREENHEIGHT/2 + 130)
	
		SCREEN.blit(BACKGROUND, (0,0))
		
		SCREEN.blit(sign, signRect)
		
		SCREEN.blit(scroll, scrollRect)
		SCREEN.blit(messageSurf1, messageRect1)
		SCREEN.blit(scroll, scrollRect2)
		SCREEN.blit(messageSurf2, messageRect2)
		
		pygame.display.update()
		CLOCK.tick(FPS)
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return False
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if scrollRect.collidepoint(event.pos):
					click.play()
					return message1
				if scrollRect2.collidepoint(event.pos):
					click.play()
					return message2
			elif event.type == pygame.MOUSEMOTION:
				if scrollRect.collidepoint(event.pos):
					scrollCol = DGREEN
					scroll2Col = BLACK
				elif scrollRect2.collidepoint(event.pos):
					scrollCol = BLACK
					scroll2Col = DGREEN
				else:
					scrollCol = BLACK
					scroll2Col = BLACK

def setTarget(who):
	message = "Place Your Target"

	myTarget = TARGET.copy()

	targetRect = myTarget.get_rect()
	targetRad = targetRect[2] / 2

	placeRect = pygame.Rect(botRect[0] + targetRad, botRect[1] + targetRad, botRect[2] - targetRad * 2, botRect[3] - targetRad * 2)

	targetRect.center = (placeRect[0] + placeRect[2] / 2, placeRect[1] + placeRect[3] / 2)

	while True:
		SCREEN.blit(BACKGROUND, (0,0))
		drawLayout()

		drawMessage(message, 20)
		
		drawBox(placeRect, GREEN)

		SCREEN.blit(myTarget, targetRect)

		pygame.display.update()
		CLOCK.tick(FPS)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return
			elif event.type == pygame.MOUSEMOTION:
				if placeRect.collidepoint(event.pos):
					targetRect.center = event.pos
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if placeRect.collidepoint(event.pos):
					if who == 'Server':
						setupServer(event.pos)
					elif who == 'Client':
						setupClient(event.pos)
					return(event.pos)

def setupServer(pos):
	global enemyPOS
	
	config = ConfigParser.ConfigParser()
	config.read("settings.ini")
	
	HOST = ''                 # Symbolic name meaning the local host
	PORT = int(config.get("Server", "PORT")) # Arbitrary non-privileged port
	
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind((HOST, PORT))
	s.listen(1)
	conn, addr = s.accept()
	#print ('Connected by', addr)
	msg = conn.recv(1024)
	enemyPOS = tuple(int(v) for v in re.findall("[0-9]+", str(msg)))
	conn.send(str(pos))
	conn.close()
	
def setupClient(pos):
	global enemyPOS
	
	config = ConfigParser.ConfigParser()
	config.read("settings.ini")
	
	HOST = config.get("Server", "IP")     # The remote host
	PORT = int(config.get("Server", "PORT"))  # The same port as used by the server
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.connect((HOST, PORT))
	s.send(str(pos))
	msg = s.recv(1024)
	enemyPOS = tuple(int(v) for v in re.findall("[0-9]+", str(msg)))
	s.close()

def runGame(pos=None):
	global score
	
	Shots = 0
	Hits = 0
	
	myTarget = TARGET.copy()
	myTarget.set_alpha(128)
	targetRect = myTarget.get_rect()
	if pos:
		targetRect.center = pos

	targetRad = targetRect[2] / 2
	
	box = pygame.Rect(botRect)
	
	message = 'Find The Target'
	
	hitSound = pygame.mixer.Sound(os.path.join('data','hit.wav'))
	missSound = pygame.mixer.Sound(os.path.join('data','miss.wav'))

	while True:
		SCREEN.blit(BACKGROUND, (0,0))
		drawLayout()

		drawMessage(message, 28)
		if pos:
			SCREEN.blit(myTarget, targetRect)

		for hit in hit_list:
			arrow_clip = pygame.Rect(ARROW.get_width()/5*hit[2], 0, ARROW.get_width()/5 ,ARROW.get_height())
			ARROW.set_clip(arrow_clip)
			arrow_draw = ARROW.subsurface(ARROW.get_clip())
			SCREEN.blit(arrow_draw, (hit[0] - arrow_clip[2] / 2, hit[1]))
		
		score = str(Hits) + '/' + str(Shots)
		drawScore(score)

		pygame.display.update()
		CLOCK.tick(FPS)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return False
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if box.collidepoint(event.pos):
					Shots += 1
					message = 'MISS!'
					missSound.play()
				dist = math.sqrt((enemyPOS[0] - event.pos[0])**2 + (enemyPOS[1] - event.pos[1])**2)
				if dist < targetRad:
					Hits += 1
					message = 'HIT!'
					hitSound.play()
					arrow_num = int(dist / (targetRad / 5))
					hit_list.append((event.pos[0], event.pos[1], arrow_num))
					if arrow_num == 0:
						return True

def winScreen():
	target = TARGET.copy()
	targetRect = target.get_rect()
	targetRect.center = enemyPOS

	targetRad = targetRect[2] / 2
	
	box = pygame.Rect(botRect)
	
	message = "Click to continue..."
	
	messageFont = pygame.font.Font(FONT, 40)
	messageSurf = messageFont.render(message, True, WHITE)
	messageRect = messageSurf.get_rect()
	messageRect.center = (SCREENWIDTH/2, 550)
	
	pygame.mixer.Sound(os.path.join('data','tada.wav')).play()
	
	while True:
		SCREEN.blit(BACKGROUND, (0,0))
		drawLayout()

		drawMessage('Bullseye', 35)
		SCREEN.blit(target, targetRect)

		for hit in hit_list:
			arrow_clip = pygame.Rect(ARROW.get_width()/5*hit[2], 0, ARROW.get_width()/5 ,ARROW.get_height())
			ARROW.set_clip(arrow_clip)
			arrow_draw = ARROW.subsurface(ARROW.get_clip())
			SCREEN.blit(arrow_draw, (hit[0] - arrow_clip[2] / 2, hit[1]))
		
		drawScore(score)
		
		SCREEN.blit(messageSurf, messageRect)

		pygame.display.update()
		CLOCK.tick(FPS)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return False
			elif event.type == pygame.MOUSEBUTTONDOWN:
				return True
		
	
def drawMessage(text, size):
	messageFont = pygame.font.Font(os.path.join('data','freesansbold.ttf'), size)
	messageSurf = messageFont.render(text, True, WHITE)
	messageRect = messageSurf.get_rect()
	messageRect.topleft = (25, 25)

	SCREEN.blit(messageSurf, messageRect)

def drawScore(score):
	messageFont = pygame.font.Font(os.path.join('data','freesansbold.ttf'), 25)
	messageSurf = messageFont.render(score, True, LGREY)
	messageRect = messageSurf.get_rect()
	messageRect.topleft = (275, 25)

	SCREEN.blit(messageSurf, messageRect)

def drawBox(rect, color, alpha=50):
	box = pygame.Surface((rect[2],rect[3]))
	box.set_alpha(alpha)
	box.fill(color)
	SCREEN.blit(box, (rect[0],rect[1]))
	surf = pygame.draw.rect(SCREEN, color, rect, 2)
	return surf

def drawLayout():
	# Top Container
	drawBox(topRect, DGREEN)
	# Message Box
	mBox = (PADDING * 2, PADDING * 2, topRect[2] / 3 * 2, topRect[3] - PADDING * 2)
	drawBox(mBox, LGREY)
	# Control Box
	cBox = (PADDING * 3 + mBox[2], PADDING * 2, topRect[2] - mBox[2] - PADDING * 3, mBox[3])
	drawBox(cBox, LGREY)
	# Bottom Container
	drawBox(botRect, DGREEN)

def terminate():
	pygame.quit()
	#sys.exit()

if __name__ == '__main__':
    main()