from geopy import Point
from geopy.distance import geodesic
from pydantic import BaseModel, field_validator
from numpy import sqrt
from config import ureg


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
        return (sqrt((geodesic(self.position, source_point).km * ureg.km) ** 2 + source_altitude.to('km') ** 2)
                / speed_of_light.to('km/s'))

    def __str__(self):
        return f'"{self.position.latitude},{self.position.longitude}",{self.altitude.magnitude}'

    class Config:
        arbitrary_types_allowed = True
