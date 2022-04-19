import itertools
import pygame
import random
from scipy.stats import norm
import numpy as np
from model import *

pygame.init()
WIDTH = HEIGHT = 800
main_s = pygame.display.set_mode((WIDTH, HEIGHT))
vec = pygame.math.Vector2
NODE_RADIUS = 10
EDGE_THICKNESS = 3
bg_color = "black"



def button_a():
    return random.gauss(MU, SIGMA)

def button_b():
    return random.gauss(MU+1, SIGMA)

scientists = []
politicians = []
spindoctors = []
edges = []

class Node:
    def update(self):
        for score in [self.score] + [n.score for n in self.edges.values()]:
            self.update_confidence(score)
        self.update_color()

    def update_confidence(self, score):
        self.confidence *= score*5 + 1
        self.confidence = min(self.confidence, 1)

    def update_color(self):
        self.color = (255-int(self.confidence*255), 0, int(self.confidence*255))

    def draw(self):
        pygame.draw.circle(main_s, self.color, self.loc, NODE_RADIUS)

class Scientist(Node):
    def __init__(self, x, loc):
        self.x = x
        self.color = "green"
        self.confidence = random.uniform(0,1)
        self.edges = {}
        self.loc = loc
        self.score = 1
        scientists.append(self)

    def get_sample(self):
        return button_b()

    def update_color(self):
        self.color = (255-int(self.confidence*255), 0, int(self.confidence*255))

    def low_confidence(self):
        if self.confidence > LOW_CONF_THRESHOLD:
            return False
        else:
            for n in self.edges.values():
                if n.confidence > LOW_CONF_THRESHOLD:
                    return False
        return True

    def high_confidence(self):
        if self.confidence < HIGH_CONF_THRESHOLD:
            return False
        else:
            for n in self.edges.values():
                if n.confidence < HIGH_CONF_THRESHOLD:
                    return False
        return True

    def not_testing(self):
        return self.low_confidence() or self.high_confidence()

    def perform_study(self):
        if self.not_testing():
            self.score = 0
            return
        samples = [self.get_sample() for _ in range(SAMPLES_PER_STUDY)]
        if np.mean(samples) == 0.5:
            samples += [self.get_sample() for _ in range(SAMPLES_PER_STUDY)]
        self.score = np.mean(DIST_A.pdf(samples)) - np.mean(DIST_B.pdf(samples))


class Politician(Node):
    def __init__(self, x, loc):
        self.x = x
        self.color = "green"
        self.edges = {}
        self.confidence = 0.5
        self.loc = loc
        self.studies = []
        self.score = 1
        politicians.append(self)

    def update(self):
        for n in self.edges.values():
            self.update_confidence(n.score)
        self.update_color()

class SpinDoctor(Node):
    def __init__(self, x, loc):
        self.x = x
        self.color = "grey"
        self.read_edges = {}
        self.write_edges = {}
        self.loc = loc
        self.studies = []
        self.score = 1
        spindoctors.append(self)

    def update(self):
        self.score = min([n.score for n in self.read_edges.values()])

class Edge:
    def draw(self):
        pygame.draw.line(main_s, self.color, *self.points, EDGE_THICKNESS)

class ScienceEdge(Edge):
    def __init__(self, a, b):
        self.a, self.b = a,b
        a.edges[self] = b
        b.edges[self] = a
        self.code = tuple(sorted([a.x, b.x]))
        self.points = [a.loc, b.loc]
        self.color = "green"
        edges.append(self)

class SpinReadEdge(Edge):
    def __init__(self, spinner, scientist):
        spinner.read_edges[self] = scientist
        self.points = [spinner.loc, scientist.loc]
        self.color = "yellow"
        edges.append(self)

class SpinWriteEdge(Edge):
    def __init__(self, spinner, pollie):
        spinner.write_edges[self] = pollie
        pollie.edges[self] = spinner
        self.points = [spinner.loc, pollie.loc]
        self.color = "cyan"
        edges.append(self)

class PolScienceEdge(Edge):
    def __init__(self, pollie, scientist):
        pollie.edges[self] = scientist
        self.points = [scientist.loc, pollie.loc]
        self.color = "cyan"
        edges.append(self)

def circle_point(radius, phi, center):
    (loc:=vec()).from_polar((radius, phi))
    return loc + vec(*center)

if __name__ == "__main__":
    for x in range(NUM_SCIENTISTS):
        loc = circle_point(WIDTH//5, (180//NUM_SCIENTISTS)*x + 90, (WIDTH//4,
            HEIGHT//2))
        Scientist(x, loc)

    for x in range(NUM_SPINDOCTORS):
        loc = circle_point(WIDTH//8, (90//NUM_SPINDOCTORS)*x + 270, (WIDTH*3//4,
            HEIGHT//4))
        SpinDoctor(x, loc)

    for x in range(NUM_POLITICIANS):
        loc = circle_point(WIDTH//8, (90//NUM_POLITICIANS)*x, (WIDTH*3//4,
            HEIGHT*3//4))
        Politician(x, loc)

    for a,b in itertools.combinations(scientists, 2):
        if random.uniform(0,1) < SCIENCE_EDGE_THRESHOLD:
            ScienceEdge(a,b)

    for spin, sci in itertools.product(spindoctors, scientists):
        if random.uniform(0,1) < SPIN_SCI_EDGE_THRESHOLD:
            SpinReadEdge(spin, sci)

    for spin, pol in itertools.product(spindoctors, politicians):
        if random.uniform(0,1) < POL_SPIN_EDGE_THRESHOLD:
            SpinWriteEdge(spin, pol)

    for pol, sci in itertools.product(politicians, scientists):
        if random.uniform(0,1) < POL_SCI_EDGE_THRESHOLD:
            PolScienceEdge(pol, sci)

    i = 0
    dir = 1
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN:
                k = pygame.key.name(event.key)
                if k == "escape":
                    exit()
        main_s.fill(bg_color)
        for edge in edges:
            edge.draw()
        for node in scientists:
            node.perform_study()
        for node in scientists + spindoctors + politicians:
            node.update()
            node.draw()
        if all([s.not_testing() for s in scientists]):
            bg_color = "darkgrey"
        pygame.display.flip()
