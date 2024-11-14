from pydantic import BaseModel, field_validator
from config import ureg
from geopy import Point


class FlightDataPoint(BaseModel):
    timestamp: ureg.Quantity | int
    position: Point | tuple[float, float]
    altitude: ureg.Quantity | int
    heading: float

    @field_validator('timestamp')
    def convert_to_second(cls, value: any):  # noqa
        if isinstance(value, ureg.Quantity):
            return value.to(ureg.second)
        return value * ureg.second

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

    def __str__(self):
        return (f'{self.timestamp.magnitude},"{self.position.latitude},{self.position.longitude}",'
                f'{int(self.altitude.magnitude) if isinstance(self.altitude, ureg.Quantity) else self.altitude},'
                f'{int(self.heading)}')

    def to_dict(self) -> dict[str, any]:
        return {
            'timestamp': self.timestamp.magnitude,
            'position': f'{self.position.latitude},{self.position.longitude}',
            'altitude': int(self.altitude.magnitude),
            'heading': int(self.heading)
        }

    class Config:
        arbitrary_types_allowed = True
