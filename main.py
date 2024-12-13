import models
from simulation import Simulation
import export.kml
import export.simulation
import sys
sys.path.append('simulation')
import numpy as np
import processor #try .processor
import utm
from geopy.distance import geodesic
from config import ureg, k_sample_rate
from visualization import parser, trajectory_plotter


if __name__ == '__main__':
    # f = models.Flight(airport_from='SVX', airport_to='LED', aircraft=models.A320)
    # sim_params = models.SimulationParameters()
    # sim = Simulation(f, sim_params)

    # sim.simulate()
    # export.simulation.to_csv(sim)
    # export.kml.flight_data_point(sim.trajectory, metadata=f)
    
    # speed_of_light: ureg.Quantity = 1 * ureg.c
    # print(speed_of_light.to("m/s"))
    
    rec_coords = {
        0: np.array([-1500000.0,400000.0,1200000.0383999997]),
        1: np.array([2000000.0,-3000000.0,0.0]),
        2: np.array([-5000000.0,12000000.0,-900001.2479999999]),
        3: np.array([11000000.0,-4000000.0,2000000.0639999998])
    }
    noize = processor.NoiseGenerator()
    # plane_init = np.array([6767809.08368214,7708107.470994491,0.0])
    
    processor_ = processor.Processor()
    processor_.set_sample_rate(k_sample_rate)
    # processor_.add_toa(0, 0.037023746653454946)
    # processor_.add_toa(1, 0.03909898420442787)
    # processor_.add_toa(2, 0.04188745621201416)
    # processor_.add_toa(3, 0.04206144214077686)
    # processor_.init_solver(rec_coords, plane_init)
    # processor_.add_toa(0, 0)
    # processor_.add_toa(1, 0)
    # processor_.add_toa(2, 0)
    # processor_.add_toa(3, 0) 
    # processor_.process()
    
    trajectory_file = 'data/output/simulation/trajectory.csv'
    toa_file = 'data/output/simulation/toa.csv'

    parser_ = parser.Parser()
    # t_plt = trajectory_plotter.TrajectoryPlotter()
    i = 0
    for trajectory_data in parser_.parse_trajectory(trajectory_file):
        print(trajectory_data)
        processor_._plotter.add_point(trajectory_data[1], trajectory_data[2], trajectory_data[3])
        processor_._plotter.add_point_kalman(trajectory_data[1]+noize.generate(), trajectory_data[2]+noize.generate(), trajectory_data[3]+noize.generate())
        if i == 0:
            plane_init = np.array([trajectory_data[1], trajectory_data[2], trajectory_data[3]])
            i+=1
    #processor_._plotter.plot()        
    i = 0
        
    for toa_data in parser_.parse_toa(toa_file):
        print(toa_data)
        if i > 1:
            processor_.add_toa(0, toa_data[1])
            processor_.add_toa(1, toa_data[2])
            processor_.add_toa(2, toa_data[3])
            processor_.add_toa(3, toa_data[4])
            processor_.process()
        elif i == 1:
            processor_.add_toa(0, toa_data[1])
            processor_.add_toa(1, toa_data[2])
            processor_.add_toa(2, toa_data[3])
            processor_.add_toa(3, toa_data[4])
            processor_.init_solver(rec_coords, plane_init)
            i+=1   
        elif i == 0:
            i += 1 
    processor_._plotter.plot()
    #processor_._plotter.plot_kalman()
    #processor_._plotter.plot_mlat()           

    
    #for el in rec_coords.values():
    #    x = np.linalg.norm(el - plane_init) / speed_of_light.to('m/s').magnitude
    #    print(x)