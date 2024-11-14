import models
from simulation import Simulation
import export.kml


if __name__ == '__main__':
    f = models.Flight(airport_from='UUD', airport_to='DME', aircraft=models.A320)
    sim_params = models.SimulationParameters()
    sim = Simulation(f, sim_params)

    sim.simulate()
    export.kml.flight_data_point(sim.trajectory, metadata=f)
