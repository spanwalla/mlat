import models
from simulation import Simulation
from config import AIRPORTS
import export


if __name__ == '__main__':
    f = models.Flight(start_point=AIRPORTS['IKT'], end_point=AIRPORTS['LED'], aircraft=models.A320)
    sim_params = models.SimulationParameters()
    sim = Simulation(f, sim_params)

    sim.simulate()

    export.simulation_to_csv(sim)
