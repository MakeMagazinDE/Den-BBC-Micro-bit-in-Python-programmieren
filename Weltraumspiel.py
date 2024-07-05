from microbit import *

import music
import random

STATE_START = 0
STATE_RUN = 1
STATE_END = 2

LEFT = -1
STOP = 0
RIGHT = 1

LOST = 0
WIN = 1
UNKNOWN = -1

lost_or_win = UNKNOWN

ACCELEROMETER = False

MICROPHONE = False

THEME_MELODY = [ 'G4:4', 'G4:4', 'G4:4', 'D4:2','A4:8', 'G4:2', 'C5:8', 'B4:4',
                 'A4:2']

SHIP_IMAGES = [
    Image("00000:"
          "00000:"
          "00900:"
          "09490:"
          "94449"),
    Image("00000:00900:09490:94449:09490"),
    Image("00900:09490:94449:09490:00900"),
    Image("09490:94449:09490:00900:00000"),
    Image("94449:09490:00900:00000:00000")
]

game_state = STATE_START
stone_count = 0

def start_game():
    music.play(THEME_MELODY, wait=False,loop=True)

    while True:
        # Taste abfragen
        if button_a.was_pressed() or button_b.was_pressed():
            break

        # Raumschiff zeigen
        for image in SHIP_IMAGES:
            display.show(image)
            sleep(100)

    music.stop()


class Timer:
    def __init__(self,max_value) -> None:
        self.max_value = max_value
        self.current_value = max_value

    def update_and_check(self, difference)-> bool :
        result = False
        self.current_value -= difference
        if self.current_value < 0:
            self.current_value = self.max_value
            result = True

        return result

class Actor:
    def __init__(self, x, y, speed=0) -> None:
        self.x = x
        self.y = y
        self.timer = Timer(speed)

    def update(self):
        pass


class Player(Actor):
    def __init__(self, x, y, direction=STOP, speed=0) -> None:
        super().__init__(x, y, speed)
        self.direction = direction

    def update(self):
        if self.direction == LEFT:
            self.x = max(0,self.x-1)

        if self.direction == RIGHT:
            self.x = min(4,self.x+1)


class Rocket(Actor):
    def __init__(self, x=-1, y=-1, speed=0) -> None:
        super().__init__(x, y, speed)
        if x == -1:
            self.init()

    def init(self):
        self.x = player.x
        self.y = player.y-1

    def update(self):
        self.y -= 1

        if self.y < 0 :
            self.init()

        # hit rocket a stone?
        if stone.x == rocket.x and stone.y == rocket.y:
            global stone_count
            stone_count += 1
            self.init()
            stone.init()


class Stone(Actor):
    def __init__(self, x=-1, y=-1, speed=0) -> None:
        super().__init__(x, y, speed)
        if x == -1:
            self.init()

    def init(self):
        self.x = random.randint(0,4)
        self.y = 0

    def update(self):
        self.y += 1

        if self.y > 4:
            self.init()

        # hit stone player?
        if self.x == player.x and self.y == player.y:
            lost_or_win = LOST


player = Player(0,4,direction=STOP,speed=20)
rocket = Rocket(speed=50)
stone  = Stone(speed=200)

actors = [player, rocket, stone]

def input():
    if button_a.is_pressed():
        player.direction = LEFT
    elif button_b.is_pressed():
        player.direction = RIGHT
    else:
        player.direction = STOP

    if ACCELEROMETER:
        if accelerometer.is_gesture("left"):
            player.direction = LEFT
        elif accelerometer.is_gesture("right"):
            player.direction = RIGHT
        else:
            player.direction = STOP

    if MICROPHONE:
        if microphone.is_event(SoundEvent.QUIET):
            player.direction = LEFT
        elif microphone.is_event(SoundEvent.LOUD):
            player.direction = RIGHT
        else:
            player.direction = STOP


def update(difference):
    for a in actors:
        if a.timer.update_and_check(difference):
            a.update()


def paint():
    display.clear()
    display.set_pixel(player.x,player.y,9)
    display.set_pixel(rocket.x,rocket.y,4)
    display.set_pixel(stone.x, stone.y, 8)


def game_loop(difference):
    input()
    update(difference)
    paint()

def do_gameloop(last_run):
    global game_state, lost_or_win

    now = running_time()
    game_loop(now-last_run)
    last_run = now

    if stone_count > 2:
        lost_or_win = WIN

    if lost_or_win != UNKNOWN:
        game_state = STATE_END

def end_game():
    if lost_or_win == WIN:
        display.show("Win")
    else:
        display.show("Lost")


while True:
    last_run = running_time()

    if game_state == STATE_START:
        start_game()
        game_state = STATE_RUN

    elif game_state == STATE_RUN:
        do_gameloop(last_run)

    elif game_state == STATE_END:
        end_game()

