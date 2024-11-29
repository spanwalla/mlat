from pydantic import BaseModel, field_validator
from numpy import format_float_positional
from config import ureg


class ToaDataPoint(BaseModel):
    timestamp: ureg.Quantity | int
    signal_time: dict[int, ureg.Quantity]

    @field_validator('timestamp')
    def convert_to_second(cls, value: any):  # noqa
        if isinstance(value, ureg.Quantity):
            return value.to(ureg.second)
        return value * ureg.second

    def __str__(self):
        return (f"{self.timestamp.to('second').magnitude},"
                f"[{','.join([f'{k}:{format_float_positional(v.to('second').magnitude)}' for k, v in
                              self.signal_time.items()])}]")

    def to_dict(self) -> dict[str, any]:
        d: dict[str | int, any] = {'timestamp': self.timestamp.to('second').magnitude}
        d.update({k: format_float_positional(v.to('second').magnitude) for k, v in self.signal_time.items()})
        return d

    class Config:
        arbitrary_types_allowed = True
