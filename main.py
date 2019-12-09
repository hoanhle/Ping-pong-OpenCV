import pygame
import sys
from pygame.locals import*
import cv2
import numpy as np
import random, time
from pygame.locals import *

# Loading all sounds
pygame.mixer.init()  ## For sound
shooting = pygame.mixer.Sound("sound/bounce.ogg")


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
window_height = 300
window_width = 400
display_surf = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Pong")
# Loading all images

background = pygame.image.load("starfield.png").convert()

fps = 200
fps_clock = pygame.time.Clock()
cap = cv2.VideoCapture(0)

# Threshold for binary
lower = np.array([60,25,30], dtype = 'uint8')
upper = np.array([255,220,255], dtype = 'uint8')
flag = 0


class Paddle:
    def __init__(self, x, w, h):
        self.w = w
        self.h = h
        self.x = x
        self.y = window_height / 2
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)


    def draw(self):
        pygame.draw.rect(display_surf, WHITE, self.rect)



    def detectMove(self, cy):
        self.rect.y = cy
        self.draw()

class AutoPaddle(Paddle):
    def __init__(self, x, w, h, speed, ball):
        super().__init__(x, w, h)
        self.speed = speed
        self.ball = ball


    def move(self):
        if self.ball.dir_x == 1:
            if self.rect.y + self.rect.h/2 < self.ball.rect.bottom:
                self.rect.y += self.speed
            if self.rect.y + self.rect.h/2 > self.ball.rect.bottom:
                self.rect.y -= self.speed


class ScoreBoard:
    def __init__(self, score=0):
        self.x = window_width - 150
        self.y = 20
        self.score = score
        self.font = pygame.font.Font('freesansbold.ttf', 20)

    def display(self, score):
        result_srf = self.font.render('Score : %s' % score, True, WHITE)
        result_rect = result_srf.get_rect()
        result_rect.topleft = (window_width - 150, 20)
        display_surf.blit(result_srf, result_rect)


class Ball:
    def __init__(self, x, y, w, h, speed):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.speed = speed
        self.dir_x = -1  # left = -1 and right = 1
        self.dir_y = -1   # up = -1 and down = 1
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self):
        pygame.draw.rect(display_surf, WHITE, self.rect)

    def bounce(self, axis):
        if axis == 'x':
            self.dir_y *= -1
        if axis == 'y':
            self.dir_x *= -1
        shooting.play()

    def hit_ceiling(self):
        if self.dir_y == -1 and self.rect.top <= self.h:
            return True
        else:
            return False

    def hit_floor(self):
        if self.dir_y == 1 and self.rect.bottom >= window_height - self.h:
            return True
        else:
            return False

    def hit_wall(self):
        if (self.dir_x == -1 and self.rect.left <= self.w) or (self.dir_x == 1 and self.rect.right >= window_width - self.w):
            return True
        else:
            return False

    def hit_paddle_user(self, paddle):
        if self.rect.left == paddle.rect.right and self.rect.bottom >= paddle.rect.top and self.rect.top <= paddle.rect.bottom:
            return True
        else:
            return False

    def hit_paddle_computer(self, paddle):
        if self.rect.right == paddle.rect.left and self.rect.bottom >= paddle.rect.top and self.rect.top <= paddle.rect.bottom:
            return True
        else:
            return False

    def move(self):
        self.rect.x += (self.dir_x * self.speed)
        self.rect.y += (self.dir_y * self.speed)
        if self.hit_ceiling() or self.hit_floor():
            self.bounce('x')


class Game:
    def __init__(self, line_thickness=10, speed=5):
        self.line_thickness = line_thickness
        self.speed = speed
        ball_x = window_width / 2
        ball_y = window_height / 2
        ball_w = self.line_thickness
        ball_h = self.line_thickness
        self.ball = Ball(ball_x, ball_y, ball_w, ball_h, self.speed)
        self.paddles = {}
        paddle_x = 20
        paddle_w = self.line_thickness
        paddle_h = 50
        self.paddles['user'] = Paddle(paddle_x, paddle_w, paddle_h)
        self.paddles['computer'] = AutoPaddle(window_width - paddle_x - 10, paddle_w, paddle_h, self.speed, self.ball)
        self.score = ScoreBoard()

    def draw_arena(self):
        display_surf.blit(background, [0,0])


    def update(self):
        self.draw_arena()
        self.ball.draw()
        self.paddles['user'].draw()
        self.paddles['computer'].draw()
        self.ball.move()
        self.paddles['computer'].move()
        if self.ball.hit_paddle_user(self.paddles['user']):
            self.ball.bounce('y')
            self.score.score += 1
        self.score.display(self.score.score)
        if self.ball.hit_paddle_computer(self.paddles['computer']):
            self.ball.bounce('y')


def main():

    pygame.init()
    game = Game()

    while cap.isOpened():
        _, frame = cap.read()
        frame_resize = cv2.resize(frame, (500, 400))
        grayimage = cv2.cvtColor(frame_resize, cv2.COLOR_RGB2GRAY)
        cascade_file = cv2.CascadeClassifier("fist.xml")
        fist = cascade_file.detectMultiScale(grayimage,scaleFactor=1.1,
                                            minNeighbors=5,
                                            minSize=(30, 30),
                                            flags=cv2.CASCADE_SCALE_IMAGE)
        for x, y, w, h in fist:
            k = cv2.rectangle(frame_resize, (x, y), (x + w, y + h), (255, 255, 255), 5)

            cx = int(x + (w / 2))
            cy = y -50
            cv2.circle(frame_resize, (cx, cy), 10, (255, 255, 0))
            game.paddles['user'].detectMove(cy)
        k = cv2.waitKey(40)

        if k == ord(' '):
            break

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()





        cv2.imshow("contour", frame_resize)
        game.update()
        if game.ball.hit_wall():
            break
        pygame.display.update()
        fps_clock.tick(fps)
    print('Your score:', game.score.score)


if __name__ == '__main__':
    main()
