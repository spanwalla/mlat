from .common import from_dict_to_csv
from simulation import Simulation


def to_csv(simulation: Simulation):
    """ Выполняем некоторые преобразования, чтобы записать данные в файл .csv """
    __extra_dir__: str = 'simulation'

    trajectory_dict: list[dict[str, any]] = [i.to_dict() for i in simulation.trajectory]
    from_dict_to_csv(trajectory_dict, 'trajectory.csv', __extra_dir__)

    receivers_dict: list[dict[str, any]] = []
    for k, v in simulation.receivers.items():
        d = {'id': k}
        v = v.to_dict()
        d.update(v)
        receivers_dict.append(d)
    from_dict_to_csv(receivers_dict, 'receivers.csv', __extra_dir__)

    time_of_arrival_dict: list[dict[str, any]] = [i.to_dict() for i in simulation.time_of_arrival]
    from_dict_to_csv(time_of_arrival_dict, 'toa.csv', __extra_dir__)
