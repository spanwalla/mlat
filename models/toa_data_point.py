from pydantic import BaseModel, field_validator
from config import ureg


class ToaDataPoint(BaseModel):
    timestamp: ureg.Quantity | int
    signal_time: list[ureg.Quantity]

    @field_validator('timestamp')
    def convert_to_second(cls, value: any):  # noqa
        if isinstance(value, ureg.Quantity):
            return value.to(ureg.second)
        return value * ureg.second

    def __str__(self):
        return f"{self.timestamp.to('second').magnitude},[{','.join([str(s.to('second').magnitude) for s in self.signal_time])}]"

    class Config:
        arbitrary_types_allowed = True
