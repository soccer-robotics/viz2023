''' IMPORTS '''
import pygame
import math
from random import randint
from pygame.locals import *
from sys import exit
import comm
import serial

''' DISPLAY SETUP '''
pygame.init()
screen_size = [800, 600]
screen = pygame.display.set_mode(screen_size, RESIZABLE)
pygame.display.set_caption("Radian 2023 Sensor View")

''' CONSTANTS '''
class color:
    BLACK = (42, 43, 46)
    DARKBLACK = (37, 35, 35)
    WHITE = (255, 255, 255)
    RED = (230, 16, 80)
    GREEN = (0, 133, 113)
    BLUE = (7, 195, 224)
    GRAY = (128, 168, 128)
    GREY = (84, 84, 84)

arrow_points = [
    (0, 0),
    (5, 5),
    (3, 5),
    (3, 10),
    (-3, 10),
    (-3, 5),
    (-5, 5),
    (0, 0)
]
arrow_points = [[x*5, y*5] for x, y in arrow_points]
lg_arrow_points = [[x*2, y*2] for x, y in arrow_points]

mini_arrow_points = [
    (-10, 10),
    (0, 0),
    (10, 10)
]

font = pygame.font.SysFont("Segoe UI", 25)

''' DISPLAY FUNCTIONS '''
def rotate_point(point, angle, ref):
    angle = -math.radians(angle)
    x, y = point
    x -= ref[0]
    y -= ref[1]
    x, y = x * math.cos(angle) - y * math.sin(angle), x * math.sin(angle) + y * math.cos(angle)
    return (x, y)

def draw_rotated_polygon(screen, color, x, y, points, angle, stroke = 0):
    # calculate center of polygon
    a, b = 0, 0
    for point in points:
        a += point[0]
        b += point[1]
    a /= len(points)
    b /= len(points)

    # rotate points
    rotated_points = []
    for point in points:
        rotated = rotate_point(point, angle, (a, b))
        rotated_points.append([rotated[0]+x, rotated[1]+y])
    pygame.draw.polygon(screen, color, rotated_points, stroke)

''' CLASSES '''
class Field:
    def __init__(self, screen):
        self.screen = screen
        self.margin = 50 # pixels
        
        self.width = 182 # cm
        self.height = 243 # cm

        self.padding = 25 # cm -> the distance between field edge and field border
        
        self.tof_front = 100
        self.tof_left = 50
        self.tof_right = 60
        self.tof_back = 100
        self.theta = 0

    def calc_field_size(self):
        w = screen_size[0] // 2 - self.margin * 2
        h = screen_size[1] - self.margin * 2
        return min(w, h * self.width / self.height), min(h, w * self.height / self.width)

    def field2screen(self, x, y):
        # x, y: cm
        w, h = self.calc_field_size()
        x = (screen_size[0] // 2 - w) // 2 + (x * w) / self.width
        y = (screen_size[1] - h) // 2 + (y * h) / self.height
        return x, y

    def draw(self):
        # Field occupies left half of the display
        w, h = self.calc_field_size()
        # Draw field
        pygame.draw.rect(self.screen, color.DARKBLACK, (0, 0, screen_size[0] // 2, screen_size[1]))
        pygame.draw.rect(
            self.screen,
            color.GREEN,
            (
                self.field2screen(0, 0)[0],
                self.field2screen(0, 0)[1],
                w,
                h
            )
        )
        # Field border
        pygame.draw.rect(
            self.screen,
            color.GRAY,
            (
                self.field2screen(self.padding, self.padding)[0],
                self.field2screen(self.padding, self.padding)[1],
                w - (self.padding * 2 * w) / self.width,
                h - (self.padding * 2 * h) / self.height,
            ),
            3
        )
        # Goals
        pygame.draw.rect(
            self.screen,
            color.GRAY,
            (
                self.field2screen(self.padding + 62/2, self.padding)[0],
                self.field2screen(self.padding + 62/2, self.padding)[1],
                (70 * w) / self.width,
                (25 * h) / self.height,
            ),
            3
        )
        pygame.draw.rect(
            self.screen,
            color.GRAY,
            (
                self.field2screen(self.padding + 62/2, self.padding)[0],
                self.field2screen(self.padding + 62/2, self.height - 25 - self.padding)[1],
                (70 * w) / self.width,
                (25 * h) / self.height,
            ),
            3
        )
        # Robot range of error
        robot_topleft = self.field2screen(self.tof_left, self.tof_front)
        robot_bottomright = self.field2screen(self.width - self.tof_right, self.height - self.tof_back)
        
        pygame.draw.rect(
            self.screen,
            color.BLACK,
            (
                robot_topleft[0],
                robot_topleft[1],
                robot_bottomright[0] - robot_topleft[0],
                robot_bottomright[1] - robot_topleft[1]
            ),
            3
        )
        # TOF readings
        pygame.draw.line(self.screen, color.BLACK,
            self.field2screen(self.tof_left + (self.width - self.tof_left - self.tof_right)//2, 0),
            self.field2screen(self.tof_left + (self.width - self.tof_left - self.tof_right)//2, self.tof_front)
        , 3)
        pygame.draw.line(self.screen, color.BLACK,
            self.field2screen(self.tof_left + (self.width - self.tof_left - self.tof_right)//2, self.height - self.tof_back),
            self.field2screen(self.tof_left + (self.width - self.tof_left - self.tof_right)//2, self.height)
        , 3)
        pygame.draw.line(self.screen, color.BLACK,
            self.field2screen(0, self.tof_front + (self.height - self.tof_front - self.tof_back)//2),
            self.field2screen(self.tof_left, self.tof_front + (self.height - self.tof_front - self.tof_back)//2)
        , 3)
        pygame.draw.line(self.screen, color.BLACK,
            self.field2screen(self.width, self.tof_front + (self.height - self.tof_front - self.tof_back)//2),
            self.field2screen(self.width - self.tof_right, self.tof_front + (self.height - self.tof_front - self.tof_back)//2)
        , 3)
        self.screen.blit( # forward
            font.render(f"{self.tof_front} cm", True, color.WHITE),
            [screen_size[0] // 4 - font.size(f"{self.tof_front} cm")[0] // 2, 10]
        )
        self.screen.blit( # backward
            font.render(f"{self.tof_back} cm", True, color.WHITE),
            [screen_size[0] // 4 - font.size(f"{self.tof_back} cm")[0] // 2, screen_size[1] - 40]
        )
        self.screen.blit( # left
            pygame.transform.rotate(font.render(f"{self.tof_left} cm", True, color.WHITE), 90),
            [10, screen_size[1] // 2 - font.size(f"{self.tof_left} cm")[0] // 2]
        )
        self.screen.blit( # right
            pygame.transform.rotate(font.render(f"{self.tof_right} cm", True, color.WHITE), 90),
            [screen_size[0] // 2 - 40, screen_size[1] // 2 - font.size(f"{self.tof_right} cm")[0] // 2]
        )
        # Robot estimated position
        robot_est = (robot_topleft[0] + robot_bottomright[0]) // 2, (robot_topleft[1] + robot_bottomright[1]) // 2
        pygame.draw.circle(self.screen, color.WHITE, robot_est, 5)
        draw_rotated_polygon(
            self.screen,
            color.WHITE,
            robot_est[0],
            robot_est[1],
            arrow_points,
            -self.theta,
            stroke = 3
        )

class Robot:
    def __init__(self, screen):
        self.screen = screen
        self.theta = 0
        self.ir = [0 for _ in range(24)]
        self.line = [randint(0, 1024) for _ in range(24)]
        self.gate = 0
        
        self.radius = 10 # percent of screen width

    def draw(self):
        # robot shell
        pygame.draw.circle(self.screen, color.WHITE, (screen_size[0] * 3 // 4, screen_size[1] // 2), self.radius * screen_size[0] // 100, 2)
        # line sensors
        for i in range(len(self.line)):
            pt = rotate_point([0, -(self.radius - 2) * screen_size[0] // 100], i * 360 // len(self.line), [0, 0])
            pygame.draw.circle(
                self.screen,
                [j * (self.line[i] / 1024) for j in color.BLUE],
                [pt[0] + screen_size[0] * 3 // 4, pt[1] + screen_size[1] // 2],
                15
            )
            pygame.draw.circle(
                self.screen,
                color.WHITE,
                [pt[0] + screen_size[0] * 3 // 4, pt[1] + screen_size[1] // 2],
                15,
                2
            )
        # ir sensors
        pts = []
        for i in range(len(self.ir)):
            pt1 = rotate_point([self.radius * screen_size[0] // 100, 0], i * 360 // len(self.ir), [0, 0])
            pt2 = rotate_point([(self.radius + self.ir[i] / 50) * screen_size[0] // 100, 0], i * 360 // len(self.ir), [0, 0])
            pygame.draw.line(
                self.screen,
                color.GREY,
                [pt1[0] + screen_size[0] * 3 // 4, pt1[1] + screen_size[1] // 2],
                [pt2[0] + screen_size[0] * 3 // 4, pt2[1] + screen_size[1] // 2],
                2
            )
            pts.append([pt2[0] + screen_size[0] * 3 // 4, pt2[1] + screen_size[1] // 2])

            ptText= rotate_point([(self.radius + 2) * screen_size[0] // 100, 0], i * 360 // len(self.ir), [0, 0])
            self.screen.blit(
                font.render(str(i), True, color.WHITE),
                [ptText[0] + screen_size[0] * 3 // 4 - font.size(str(i))[0] // 2, ptText[1] + screen_size[1] // 2 - font.size(str(i))[1] // 2]
            )
        pygame.draw.polygon(self.screen, color.GREY, pts, 2)
        # ir average
        x = 0
        y = 0
        for i in range(len(self.ir)):
            pt = rotate_point([0, -(self.radius + self.ir[i] / 100) * screen_size[0] // 100], i * 360 // len(self.ir), [0, 0])
            x += pt[0]
            y += pt[1]
        x /= len(self.ir)
        y /= len(self.ir)
        ball_angle = math.atan2(y, x) * 180 / math.pi
        ball_dist = math.sqrt(x**2 + y**2)

        pt1 = rotate_point([0, -self.radius * screen_size[0] // 100], ball_angle, [0, 0])
        pt2 = rotate_point([0, -(self.radius + ball_dist) * screen_size[0] // 100], ball_angle, [0, 0])
        pygame.draw.line(
            self.screen,
            color.WHITE,
            [pt1[0] + screen_size[0] * 3 // 4, pt1[1] + screen_size[1] // 2],
            [pt2[0] + screen_size[0] * 3 // 4, pt2[1] + screen_size[1] // 2],
            2
        )
        draw_rotated_polygon(screen, color.WHITE, pt2[0] + screen_size[0] * 3 // 4, pt2[1] + screen_size[1] // 2, mini_arrow_points, ball_angle, stroke = 2)
        
        # gate sensor
        pygame.draw.rect(
            self.screen,
            color.GRAY,
            (
                screen_size[0] * 3 // 4 - 0.5 * self.radius * screen_size[0] // 100,
                screen_size[1] * 1 // 8,
                1 * self.radius * screen_size[0] // 100,
                0.5 * self.radius * screen_size[0] // 100
            ),
            0 if self.gate else 2
        )
        surf = font.render(
            {0: "Gate Open", 1: "Gate Blocked"}[self.gate],
            True,
            {0: color.WHITE, 1: color.BLACK}[self.gate]
        )
        screen.blit(
            surf,
            (screen_size[0] * 3 // 4 - surf.get_width() // 2, screen_size[1] * 1 // 8 + 0.25 * self.radius * screen_size[0] // 100 - surf.get_height() // 2)
        )
        # gyro
        draw_rotated_polygon(screen, color.RED, screen_size[0] * 3 // 4, screen_size[1] // 2, lg_arrow_points, self.theta, stroke = 2)
        surf = font.render(
            str(self.theta),
            True,
            color.RED
        )
        screen.blit(
            surf,
            (screen_size[0] * 3 // 4 - surf.get_width() // 2, screen_size[1] * 1 // 2 - surf.get_height() // 2)
        )
    
    def update(self):
        ''' FAKE UPDATE -> REMEMBER TO REMOVE
        for i in range(len(self.ir)):
            self.ir[i] = min(max(self.ir[i] + randint(-40, 40), 0), 1024)
        for i in range(len(self.line)):
            self.line[i] = min(max(self.line[i] + randint(-40, 40), 0), 1024)
        '''
        try:
            data = comm.readline()
            status = "ok"
            if data["type"] == "infra":
                self.ir = data["info"]
            elif data["type"] == "gyro":
                self.theta = data["info"][0]
        except IndexError:
            status = "signal lost"
            comm.reconnect()
        except serial.serialutil.SerialException:
            status = "signal lost"
            comm.reconnect()

''' MAIN LOOP '''
clock = pygame.time.Clock()

field = Field(screen)
robot = Robot(screen)

while True:
    # Graphics
    screen.fill(color.BLACK)

    field.theta = robot.theta
    field.draw()
    robot.draw()
    robot.update()

    screen.blit(
        font.render("Radian Sensor Monitor", True, color.WHITE),
        (screen_size[0] // 2 - font.size("Radian Sensor Monitor")[0] // 2, 10)
    )
    screen.blit(
        font.render("Field View", True, color.GREY),
        (20, 10)
    )
    screen.blit(
        font.render("Robot View", True, color.GREY),
        (screen_size[0] - font.size("Robot View")[0] - 20, 10)
    )

    # Event handling
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
        if event.type == VIDEORESIZE:
            screen_size = [event.w, event.h]
            screen = pygame.display.set_mode(screen_size, RESIZABLE)    
    pygame.display.flip()
    clock.tick(60)