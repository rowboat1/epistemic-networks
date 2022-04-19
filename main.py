from grapher import *

if __name__ == "__main__":
    num_scientists = 10
    num_spindoctors = 3
    num_politicians = 1
    science_edge_threshold = 0.5
    spin_sci_edge_threshold = 0.7
    pol_spin_edge_threshold = 1
    pol_sci_edge_threshold = 0.7

    scenario = Scenario(
        num_scientists, num_spindoctors, num_politicians,
        science_edge_threshold, spin_sci_edge_threshold,
        pol_spin_edge_threshold, pol_sci_edge_threshold
    )
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
