from scipy.stats import norm
import itertools
import random
import numpy as np

NUM_SCIENTISTS = 10
NUM_POLITICIANS = 1
NUM_SPINDOCTORS = 3
EPSILON = 0.005
MU = 1 << 5
SIGMA = MU >> 2
SAMPLES_PER_STUDY = 10
DIST_A = norm(loc = MU + EPSILON, scale = SIGMA)
DIST_B = norm(loc = MU - EPSILON, scale = SIGMA)
HIGH_CONF_THRESHOLD = 0.99
LOW_CONF_THRESHOLD = 0.48
SCIENCE_EDGE_THRESHOLD = 0.5
POL_SCI_EDGE_THRESHOLD = 0.7
POL_SPIN_EDGE_THRESHOLD = 1
SPIN_SCI_EDGE_THRESHOLD = 0.7


def button_a():
    return random.gauss(MU, SIGMA)

def button_b():
    return random.gauss(MU+1, SIGMA)

class Scenario:
    def __init__(self):
        self.scientists = [Scientist(x) for x in range(NUM_SCIENTISTS)]
        self.politicians = [Politician(x) for x in range(NUM_POLITICIANS)]
        self.spindoctors = [SpinDoctor(x) for x in range(NUM_SPINDOCTORS)]
        self.updateables = self.scientists + self.politicians + self.spindoctors
        self.edges = []
        for a,b in itertools.combinations(self.scientists, 2):
            if random.uniform(0,1) < SCIENCE_EDGE_THRESHOLD:
                self.edges.append(ScienceEdge(a,b))

        for spin, sci in itertools.product(self.spindoctors, self.scientists):
            if random.uniform(0,1) < SPIN_SCI_EDGE_THRESHOLD:
                self.edges.append(SpinReadEdge(spin, sci))

        for spin, pol in itertools.product(self.spindoctors, self.politicians):
            if random.uniform(0,1) < POL_SPIN_EDGE_THRESHOLD:
                self.edges.append(SpinWriteEdge(spin, pol))

        for pol, sci in itertools.product(self.politicians, self.scientists):
            if random.uniform(0,1) < POL_SCI_EDGE_THRESHOLD:
                self.edges.append(PolScienceEdge(pol, sci))

    def update(self):
        for scientist in self.scientists:
            scientist.perform_study()
        for node in self.updateables:
            node.update()

class Node:
    def update(self):
        for score in [self.score] + [n.score for n in self.edges.values()]:
            self.update_confidence(score)
        # self.update_color()

    def update_confidence(self, score):
        self.confidence *= score*5 + 1
        self.confidence = min(self.confidence, 1)

class Scientist(Node):
    def __init__(self, x):
        self.x = x
        self.confidence = random.uniform(0,1)
        self.score = 1
        self.edges = {}

    def get_sample(self):
        return button_b()

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
    def __init__(self, x):
        self.x = x
        self.edges = {}
        self.confidence = 0.5
        self.score = 0

class SpinDoctor(Node):
    def __init__(self, x):
        self.x = x
        self.read_edges = {}
        self.write_edges = {}
        self.score = 0

    def update(self):
        self.score = min([n.score for n in self.read_edges.values()])

class Edge:
    pass

class ScienceEdge(Edge):
    def __init__(self, a, b):
        self.a, self.b = a,b
        a.edges[self] = b
        b.edges[self] = a
        self.vertices = [a,b]

class SpinReadEdge(Edge):
    def __init__(self, spinner, scientist):
        spinner.read_edges[self] = scientist
        self.vertices = [spinner, scientist]

class SpinWriteEdge(Edge):
    def __init__(self, spinner, pollie):
        spinner.write_edges[self] = pollie
        pollie.edges[self] = spinner
        self.vertices = [spinner, pollie]

class PolScienceEdge(Edge):
    def __init__(self, pollie, scientist):
        pollie.edges[self] = scientist
        self.vertices = [pollie, scientist]
