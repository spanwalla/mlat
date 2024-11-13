import models
from simulation import Simulation


if __name__ == '__main__':
    f = models.Flight(start_point=(52.268383, 104.378967), end_point=(59.799225, 30.315948), aircraft=models.A320)
    sim_params = models.SimulationParameters()
    sim = Simulation(f, sim_params)

    print(*sim.simulate(), sep='\n')
