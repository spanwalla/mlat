import models
from simulation import Simulation
import export
import noise

if __name__ == '__main__':
    f = models.Flight(airport_from='UUD', airport_to='DME', aircraft=models.A320)
    sim_params = models.SimulationParameters()
    sim = Simulation(f, sim_params)

    sim.simulate()
    export.simulation.to_csv(sim)
    export.simulation.toa_to_csv(noise.toa.standard_noise(sim.time_of_arrival, 0.05), 'toa_noise.csv')
    # export.kml.flight_data_point(sim.trajectory, metadata=f)
