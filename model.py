from scipy.stats import norm

NUM_SCIENTISTS = 5
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

class Scenario:
    def __init__():
        self.scientists = []
        self.politicians = []
        self.spindoctors = []
        self.edges = []
