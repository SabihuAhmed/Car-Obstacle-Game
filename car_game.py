import random
import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

HW, HH = 300, 350                      # world: [-HW, HW] x [-HH, HH]
LANES = (-95, -47, 47, 95)             # enemy spawn lanes
STEP = 48                              # player move per key press
COLORS = [(.95, .25, .2), (.25, .6, 1), (1, .65, .15), (.65, .35, .9), (.2, .8, .45)]
WHITE, YELLOW = (1, 1, 1), (1, .9, .25)

px, py = 0, -235                       # player position
enemies = []                           # each: [x, y, color, speed]
score, offset, spawn = 0, 0.0, 0.0     # offset = scrolling road position
paused, over, last = True, False, 0


# ---------------------------- drawing helpers ----------------------------
def rect(x, y, w, h, color):
    glColor3f(*color)
    glRectf(x, y, x + w, y + h)


def circle(cx, cy, r, color):
    """Filled midpoint circle: each octant point gives 4 horizontal spans."""
    glColor3f(*color)
    x, y, d = 0, r, 3 - 2 * r
    glBegin(GL_LINES)
    while x <= y:
        for dy, half in ((y, x), (-y, x), (x, y), (-x, y)):
            glVertex2f(cx - half, cy + dy)
            glVertex2f(cx + half, cy + dy)
        if d < 0:
            d += 4 * x + 6
        else:
            d += 4 * (x - y) + 10
            y -= 1
        x += 1
    glEnd()


def text(x, y, s, color=WHITE):
    glColor3f(*color)
    glRasterPos2f(x, y)
    for ch in s:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(ch))


def draw_car(x, y, color, facing_up=True):
    glPushMatrix()
    glTranslatef(x, y, 0)
    if not facing_up:
        glRotatef(180, 0, 0, 1)
    rect(-18, -30, 36, 60, color)                       # body
    rect(-12, 0, 24, 12, (.62, .86, .96))               # windscreen
    for wx in (-20, 20):
        for wy in (-18, 18):
            circle(wx, wy, 6, (.03, .03, .03))          # wheels
    for hx in (-10, 10):
        circle(hx, 27, 3, (1, .95, .5))                 # headlights
    glPopMatrix()


def draw_road():
    rect(-HW, -HH, HW * 2, HH * 2, (.10, .38, .17))     # grass
    rect(-150, -HH, 300, HH * 2, (.19, .20, .22))       # road
    for edge in (-143, 137):
        rect(edge, -HH, 6, HH * 2, (.95, .92, .7))      # side lines
    y = -HH - 50 + offset
    while y < HH:                                       # dashed centre line
        rect(-4, y, 8, 38, (.95, .95, .88))
        y += 95


# ------------------------------- game logic -------------------------------
def reset(start_paused=False):
    global px, py, enemies, score, spawn, paused, over
    px, py, enemies, score, spawn = 0, -235, [], 0, 0.0
    paused, over = start_paused, False


def update(dt):
    global offset, spawn, score, over, enemies
    if paused or over:
        return
    offset = (offset + 220 * dt) % 95
    spawn += dt
    if spawn >= max(.6, 1.25 - score * .02):            # gets harder with score
        spawn = 0.0
        enemies.append([random.choice(LANES), HH + 60,
                        random.choice(COLORS), random.uniform(150, 210)])
    for e in enemies:
        e[1] -= e[3] * dt
        if abs(e[0] - px) < 35 and abs(e[1] - py) < 55:  # box collision
            over = True
    score += sum(e[1] < -HH - 60 for e in enemies)       # left the screen = dodged
    enemies = [e for e in enemies if e[1] >= -HH - 60]


def move(dx, dy):
    global px, py
    if not (paused or over):
        px = max(-105, min(105, px + dx * STEP))
        py = max(-300, min(250, py + dy * STEP))


# ------------------------------ GLUT callbacks ----------------------------
def display():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    draw_road()
    for e in enemies:
        draw_car(e[0], e[1], e[2], facing_up=False)
    draw_car(px, py, (.10, .85, .95))

    text(-285, 325, f"SCORE: {score}", YELLOW)
    text(-285, -335, "Arrows/WASD: Move   SPACE: Pause   R: Restart")
    msg = "GAME OVER - R to restart" if over else "PAUSED - SPACE to play" if paused else ""
    if msg:
        rect(-135, -22, 270, 44, (.05, .05, .07))
        text(-len(msg) * 4.5, -5, msg, YELLOW)
    glutSwapBuffers()


def timer(_):
    global last
    now = glutGet(GLUT_ELAPSED_TIME)
    update(min((now - last) / 1000, .05))
    last = now
    glutPostRedisplay()
    glutTimerFunc(16, timer, 0)


def keyboard(key, *_):
    global paused
    key = key.lower()
    keys = {b'a': (-1, 0), b'd': (1, 0), b'w': (0, 1), b's': (0, -1)}
    if key == b'\x1b':
        sys.exit()
    elif key == b' ' and not over:
        paused = not paused
    elif key == b'r':
        reset()
    elif key in keys:
        move(*keys[key])


def special(key, *_):
    arrows = {GLUT_KEY_LEFT: (-1, 0), GLUT_KEY_RIGHT: (1, 0),
              GLUT_KEY_UP: (0, 1), GLUT_KEY_DOWN: (0, -1)}
    if key in arrows:
        move(*arrows[key])


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(HW * 2, HH * 2)
    glutCreateWindow(b"2D Car Dodge Game - PyOpenGL")
    glClearColor(0, 0, 0, 1)
    glMatrixMode(GL_PROJECTION)
    gluOrtho2D(-HW, HW, -HH, HH)
    glMatrixMode(GL_MODELVIEW)
    reset(start_paused=True)
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special)
    glutTimerFunc(16, timer, 0)
    glutMainLoop()


if __name__ == "__main__":
    main()