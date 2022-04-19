import pygame
from model import *

pygame.init()
WIDTH = HEIGHT = 800
main_s = pygame.display.set_mode((WIDTH, HEIGHT))
vec = pygame.math.Vector2
NODE_RADIUS = 10
EDGE_THICKNESS = 3
bg_color = "black"

# These lines define points on a circle where we can place our nodes.
# The first entry is how large the circle is, next two tell the start and end,
# of the angle. The final element is where on the screen to draw it.
SCI_LOCUS =  WIDTH//5, 90, 270, (WIDTH//4, HEIGHT//2)
SPIN_LOCUS = WIDTH//8, 270, 360, (WIDTH*3//4, HEIGHT//4)
POL_LOCUS = WIDTH//8, 0, 90, (WIDTH*3//4, HEIGHT*3//4)

class Canvas:
    def __init__(self, scenario):
        self.lookup = {}
        self.drawables = []
        self.edges = []

        # Each of the groups is drawn as though it forms a portion of a circle
        # around a certain point. This block of code maps nodes from the model
        # into their position in such a group.
        for (collection, radius, angle_start, angle_end, center, view_obj) in [
            (scenario.scientists, *SCI_LOCUS, ScientistView),
            (scenario.spindoctors, *SPIN_LOCUS, SpinDoctorView),
            (scenario.politicians, *POL_LOCUS, PoliticianView)
        ]:
            for x, entity in enumerate(collection):
                angle_interval = angle_end - angle_start
                loc = circle_point(radius, (angle_interval//len(collection))*x
                    + angle_start, center)
                view = view_obj(loc, entity)
                self.drawables.append(view)
                self.lookup[entity] = view

        for edge in scenario.edges:
            points = [self.lookup[v].loc for v in edge.vertices]
            for k,v in {
                ScienceEdge: ScienceEdgeView,
                SpinReadEdge: SpinReadEdgeView,
                SpinWriteEdge: SpinWriteEdgeView,
                PolScienceEdge: PolScienceEdgeView
            }.items():
                if isinstance(edge, k):
                    view = v(edge, points)
                    break
            self.edges.append(view)
            self.lookup[edge] = view
        self.scenario = scenario
        self.bg_color = "black"

    def update(self):
        main_s.fill(self.bg_color)
        for e in self.edges:
            e.draw()
        for d in self.drawables:
            d.update_color()
            d.draw()
        if all([s.not_testing() for s in self.scenario.scientists]):
            self.bg_color = "darkgrey"

class NodeView:
    def __init__(self, loc, model):
        self.loc = loc
        self.model = model
        self.color = "grey"

    def update_color(self):
        self.color = (255-int(self.model.confidence*255), 0,
            int(self.model.confidence*255))

    def draw(self):
        pygame.draw.circle(main_s, self.color, self.loc, NODE_RADIUS)

class ScientistView(NodeView):
    pass

class PoliticianView(NodeView):
    pass

class SpinDoctorView(NodeView):
    def update_color(self):
        pass

class EdgeView:
    def __init__(self, edge, color, points):
        self.edge = edge
        self.color = color
        self.points = points

    def draw(self):
        pygame.draw.line(main_s, self.color, *self.points, EDGE_THICKNESS)

class ScienceEdgeView(EdgeView):
    def __init__(self, edge, points):
        super().__init__(edge, "green", points)

class SpinReadEdgeView(EdgeView):
    def __init__(self, edge, points):
        super().__init__(edge, "yellow", points)

class SpinWriteEdgeView(EdgeView):
    def __init__(self, edge, points):
        super().__init__(edge, "cyan", points)

class PolScienceEdgeView(EdgeView):
    def __init__(self, edge, points):
        super().__init__(edge, "cyan", points)

def circle_point(radius, phi, center):
    (loc:=vec()).from_polar((radius, phi))
    return loc + vec(*center)

if __name__ == "__main__":
    scenario = Scenario()
    canvas = Canvas(scenario)

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
                if k == "r":
                    scenario = Scenario()
                    canvas = Canvas(scenario)
        scenario.update()
        canvas.update()
        pygame.display.flip()
