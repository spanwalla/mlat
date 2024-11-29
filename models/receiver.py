from geopy import Point
from pydantic import BaseModel, field_validator
import numpy as np
from pyproj import Transformer
from config import ureg, geo_to_proj


class Receiver(BaseModel):
    position: Point | tuple[float, float]
    altitude: ureg.Quantity | int = 0 * ureg.foot

    @field_validator('position')
    def convert_to_point(cls, value: any):  # noqa
        if isinstance(value, tuple):
            return Point(value[0], value[1])
        return value

    @field_validator('altitude')
    def convert_to_foot(cls, value: any):  # noqa
        if isinstance(value, ureg.Quantity):
            return value.to(ureg.foot)
        return value * ureg.foot

    def get_time_of_arrival(self, source_point: Point, source_altitude: ureg.Quantity) -> ureg.Quantity:
        speed_of_light: ureg.Quantity = 1 * ureg.c

        receiver = geo_to_proj.transform(self.position.latitude, self.position.longitude)
        source = geo_to_proj.transform(source_point.latitude, source_point.longitude)

        return (np.linalg.norm(np.array([receiver[0], receiver[1], self.altitude.to('m').magnitude]) -
                               np.array([source[0], source[1], source_altitude.to('m').magnitude]))
                * ureg.m / speed_of_light.to('m/s'))

        # return (sqrt((geodesic(self.position, source_point).km * ureg.km) ** 2 + source_altitude.to('km') ** 2)
        #         / speed_of_light.to('km/s'))

    def __str__(self):
        return f'"{self.position.latitude},{self.position.longitude}",{self.altitude.magnitude}'

    def to_dict(self) -> dict[str, any]:
        return {
            'position': f'{self.position.latitude},{self.position.longitude}',
            'altitude': self.altitude.magnitude
        }

    class Config:
        arbitrary_types_allowed = True
