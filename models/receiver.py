from geopy import Point
from pydantic import BaseModel, field_validator
import numpy as np
from pyproj import Transformer
from config import ureg


class Receiver(BaseModel):
    position: Point | tuple[float, float]
    altitude: ureg.Quantity | float = 0 * ureg.foot

    # @field_validator('position')
    # def convert_to_point(cls, value: any):  # noqa
    #     if isinstance(value, tuple):
    #         return Point(value[0], value[1])
    #     return value

    @field_validator('altitude')
    def convert_to_foot(cls, value: any):  # noqa
        if isinstance(value, ureg.Quantity):
            return value.to(ureg.foot)
        return value * ureg.foot

    def get_time_of_arrival(self, source_point: Point, source_altitude: ureg.Quantity) -> ureg.Quantity:
        speed_of_light: ureg.Quantity = 1 * ureg.c
        transformer = Transformer.from_crs("epsg:4326", "epsg:3857")

        #receiver = transformer.transform(self.position.latitude, self.position.longitude)
        source = transformer.transform(source_point.latitude, source_point.longitude)

        # return (np.linalg.norm(np.array([receiver[0], receiver[1], self.altitude.to('m').magnitude]) -
        #                        np.array([source[0], source[1], source_altitude.to('m').magnitude]))
        #         * ureg.m / speed_of_light.to('m/s'))
        return (np.linalg.norm(np.array([self.position[0], self.position[1], self.altitude.to('m').magnitude]) -
                               np.array([source[0], source[1], source_altitude.to('m').magnitude]))
                * ureg.m / speed_of_light.to('m/s'))

    def __str__(self):
        transformer = Transformer.from_crs("epsg:4326", "epsg:3857")
        #receiver = transformer.transform(self.position.latitude, self.position.longitude)
        return f'"{receiver[0]},{receiver[1]}",{self.altitude.to("m").magnitude}'

    def to_dict(self) -> dict[str, any]:
        transformer = Transformer.from_crs("epsg:4326", "epsg:3857")
        #receiver = transformer.transform(self.position.latitude, self.position.longitude)
        return {
            #'position': f'{receiver[0]},{receiver[1]}',
            'position': f'{self.position[0]},{self.position[1]}',
            'altitude': self.altitude.to('m').magnitude 
        }

    class Config:
        arbitrary_types_allowed = True
