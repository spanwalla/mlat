from random import random, choice
from copy import deepcopy
import models


def standard_noise(toa_points: list[models.ToaDataPoint], max_error: float) -> list[models.ToaDataPoint]:
    if not (0 < max_error <= 1):
        raise ValueError("max_error must be in (0, 1].")

    new_toa_points = deepcopy(toa_points)
    for point in new_toa_points:
        new_signal_time = {k: v * (1 + choice([-1, 1]) * max_error * random()) for k, v in point.signal_time.items()}
        point.signal_time = new_signal_time
    return new_toa_points
