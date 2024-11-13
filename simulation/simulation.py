import numpy as np
from geopy.distance import geodesic, distance
from geopy import Point
from config import ureg
from models import FlightDataPoint, Flight, SimulationParameters


def calculate_azimuth(first: Point, second: Point) -> float:
    f_lat, f_lon = np.radians(first.latitude), np.radians(first.longitude)
    s_lat, s_lon = np.radians(second.latitude), np.radians(second.longitude)

    d_lon = s_lon - f_lon

    x = np.sin(d_lon) * np.cos(s_lat)
    y = np.cos(f_lat) * np.sin(s_lat) - np.sin(f_lat) * np.cos(s_lat) * np.cos(d_lon)
    return (np.degrees(np.atan2(x, y)) + 360) % 360


class Simulation:
    def __init__(self, flight: Flight, simulation_parameters: SimulationParameters):
        self.flight = flight
        self.simulation_parameters = simulation_parameters

    def simulate(self) -> list[FlightDataPoint]:
        total_distance: ureg.Quantity = geodesic(self.flight.start_point, self.flight.end_point).km * ureg.km

        # Время набора и снижения высоты
        climb_time: ureg.Quantity = self.flight.cruise_altitude / self.flight.climb_rate
        descent_time: ureg.Quantity = self.flight.cruise_altitude / self.flight.descent_rate

        trajectory: list[FlightDataPoint] = []

        climb, climb_dist = self._calculate_trajectory_segment(climb_time, self.flight.start_point,
                                                               self.flight.end_point,
                                                               self.flight.initial_climb_speed,
                                                               self.flight.cruise_speed,
                                                               self.flight.climb_rate,
                                                               self.simulation_parameters.sampling_intervals[
                                                                  'climb'])

        descent, descent_dist = self._calculate_trajectory_segment(descent_time, self.flight.end_point,
                                                                   self.flight.start_point,
                                                                   self.flight.landing_speed,
                                                                   self.flight.cruise_speed,
                                                                   self.flight.descent_rate,
                                                                   self.simulation_parameters.sampling_intervals[
                                                                      'descent'])

        cruise_time = (total_distance - climb_dist - descent_dist) / self.flight.cruise_speed
        cruise, cruise_dist = self._calculate_trajectory_segment(cruise_time, climb[-1].position, descent[-1].position,
                                                                 self.flight.cruise_speed, self.flight.cruise_speed, 0,
                                                                 self.simulation_parameters.sampling_intervals[
                                                                     'cruise'])

        return self._reorder_timestamps(climb, cruise, descent)

    def _reorder_timestamps(self, climb: list[FlightDataPoint], cruise: list[FlightDataPoint],
                            descent: list[FlightDataPoint]) -> list[FlightDataPoint]:
        trajectory = climb
        current_timestamp = climb[-1].timestamp + self.simulation_parameters.sampling_intervals['cruise']
        for point in cruise:
            point.timestamp += current_timestamp
            trajectory.append(point)

        for i in range(len(descent) // 2):
            descent[i].timestamp, descent[-(i + 1)].timestamp = descent[-(i + 1)].timestamp, descent[i].timestamp

        descent = descent[::-1]
        current_timestamp = trajectory[-1].timestamp + self.simulation_parameters.sampling_intervals['descent']
        for point in descent:
            point.timestamp += current_timestamp
            trajectory.append(point)

        return trajectory

    def _calculate_trajectory_segment(self, segment_time: ureg.Quantity, start_position: Point, end_position: Point,
                                      start_speed: ureg.Quantity, target_speed: ureg.Quantity,
                                      vertical_speed: ureg.Quantity,
                                      sampling_interval: ureg.Quantity) -> (list[FlightDataPoint], ureg.Quantity):
        trajectory: list[FlightDataPoint] = []
        current_time: ureg.Quantity = 0 * ureg.second
        current_position: ureg.Quantity = start_position
        total_distance = 0 * ureg.km

        while current_time <= segment_time:
            azimuth = calculate_azimuth(current_position, end_position)
            current_altitude = min(vertical_speed * current_time,
                                   self.flight.cruise_altitude) if vertical_speed > 0 else self.flight.cruise_altitude

            # Линейно увеличиваем горизонтальную скорость самолёта
            current_speed: ureg.Quantity = (start_speed +
                                            (target_speed - start_speed) * (
                                                        current_altitude / self.flight.cruise_altitude))
            move_distance: ureg.Quantity = current_speed * sampling_interval
            total_distance += move_distance

            current_position: Point = geodesic(kilometers=move_distance.to(ureg.km).magnitude).destination(
                current_position, bearing=azimuth)
            trajectory.append(FlightDataPoint(
                timestamp=current_time,
                position=current_position,
                altitude=current_altitude
            ))

            current_time += sampling_interval

        return trajectory, total_distance
