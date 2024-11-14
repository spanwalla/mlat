from pydantic import BaseModel, field_validator, Field
from geopy import Point
from config import ureg
from .aircraft import Aircraft
from pyairports.airports import Airports, Airport


class Flight(BaseModel):
    start_point: Point = Field(default=Point(0, 0))
    end_point: Point = Field(default=Point(0, 0))
    airport_from: Airport | str
    airport_to: Airport | str

    climb_rate: ureg.Quantity | int = ureg.Quantity(2000, 'foot/minute')
    descent_rate: ureg.Quantity | int = ureg.Quantity(1500, 'foot/minute')

    cruise_altitude: ureg.Quantity | int = ureg.Quantity(36000, 'foot')
    cruise_speed: ureg.Quantity | int = ureg.Quantity(840, 'km/h')

    aircraft: Aircraft
    initial_climb_speed: ureg.Quantity | int | None = None
    landing_speed: ureg.Quantity | int | None = None

    def __init__(self, /, **data):
        super().__init__(**data)
        if self.initial_climb_speed is None:
            self.initial_climb_speed = self.aircraft.takeoff_speed
        if self.landing_speed is None:
            self.landing_speed = self.aircraft.landing_speed

        self.start_point = Point(float(self.airport_from.lat), float(self.airport_from.lon))
        self.end_point = Point(float(self.airport_to.lat), float(self.airport_to.lon))

    @field_validator('airport_from', 'airport_to', mode='before')
    def convert_to_airport(cls, value: any):  # noqa
        if isinstance(value, str):
            airports = Airports()
            return airports.airport_iata(value)
        return value

    @field_validator('cruise_altitude')
    def convert_to_foot(cls, value: any):  # noqa
        if isinstance(value, ureg.Quantity):
            return value.to(ureg.foot)
        return value * ureg.foot

    @field_validator('climb_rate', 'descent_rate')
    def convert_to_foot_minute(cls, value: any):  # noqa
        if isinstance(value, ureg.Quantity):
            return value.to(ureg.foot / ureg.minute)
        return value * (ureg.foot / ureg.minute)

    @field_validator('cruise_speed')
    def convert_to_km_h(cls, value: any):  # noqa
        if isinstance(value, ureg.Quantity):
            return value.to(ureg.kilometer / ureg.hour)
        return value * (ureg.kilometer / ureg.hour)

    class Config:
        arbitrary_types_allowed = True
