from pydantic import BaseModel
from config import ureg


class SimulationParameters(BaseModel):
    sampling_intervals: dict[str, ureg.Quantity] = {
        'climb': 6 * ureg.second,
        'cruise': 1 * ureg.minute,
        'descent': 6 * ureg.second
    }

    class Config:
        arbitrary_types_allowed = True
