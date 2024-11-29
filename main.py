import models
from simulation import Simulation
import export

from pyproj import Transformer


if __name__ == '__main__':
    # f = models.Flight(airport_from='UUD', airport_to='DME', aircraft=models.A320)
    # sim_params = models.SimulationParameters()
    # sim = Simulation(f, sim_params)

    # sim.simulate()
    # export.simulation.to_csv(sim)
    # export.kml.flight_data_point(sim.trajectory, metadata=f)

    receivers = [
        (52.626894214438046, 106.1702739036307),
        (52.854818330515926, 106.31218855330935),
        (55.44373199507711, 36.183865655935996),
        (55.19694693457447, 39.57074521103694)
    ]

    trajectory = [
        (51.809909136411875, 107.4324289866742),
        (51.812080769770716, 107.42714847667652)
    ]

    transformer = Transformer.from_crs("epsg:4326", "epsg:3857")

    receivers_m = [transformer.transform(rec[0], rec[1]) for rec in receivers]
    trajectory_m = [transformer.transform(t[0], t[1]) for t in trajectory]

    print(receivers_m)
    print(trajectory_m)

    print([
        (0.0006818019541237355, 0.0007590949481071445, 0.026553958195022456, 0.025287212416362843),
        (0.0006795070980143708, 0.0007569300669564947, 0.0265518928305674, 0.025285149411844357)
    ])


