from pydantic import BaseModel, field_validator
from config import ureg


class Aircraft(BaseModel):
    max_altitude: ureg.Quantity | int
    max_climb_rate: ureg.Quantity | int
    max_descent_rate: ureg.Quantity | int
    max_speed: ureg.Quantity | int
    takeoff_speed: ureg.Quantity | int
    landing_speed: ureg.Quantity | int

    @field_validator('max_altitude')
    def convert_to_foot(cls, value: any):  # noqa
        if isinstance(value, ureg.Quantity):
            return value.to(ureg.foot)
        return value * ureg.foot

    @field_validator('max_climb_rate', 'max_descent_rate')
    def convert_to_foot_minute(cls, value: any):  # noqa
        if isinstance(value, ureg.Quantity):
            return value.to(ureg.foot / ureg.minute)
        return value * (ureg.foot / ureg.minute)

    @field_validator('max_speed', 'takeoff_speed', 'landing_speed')
    def convert_to_km_h(cls, value: any):  # noqa
        if isinstance(value, ureg.Quantity):
            return value.to(ureg.kilometer / ureg.hour)
        return value * (ureg.kilometer / ureg.hour)

    class Config:
        arbitrary_types_allowed = True


A320 = Aircraft(
    max_altitude=39000,
    max_climb_rate=2500,
    max_descent_rate=2000,
    max_speed=952,
    takeoff_speed=259,
    landing_speed=219
)
