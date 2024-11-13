import geopy
from pint import UnitRegistry

# Реестр единиц измерения, для корректной работы должен использоваться единственный экземпляр на всю программу
ureg = UnitRegistry()
ureg.auto_reduce_dimensions = True  # Автоматически упрощать единицы измерения при вычислениях

# Минимальное количество приёмников, а также значение по умолчанию, если позиции приёмников не указаны
MIN_RECEIVERS: int = 4
DEFAULT_RECEIVERS: int = 4
RECEIVER_MAX_OFFSET: ureg.Quantity = ureg.Quantity(250, 'km')

# Координаты некоторых аэропортов, используется код IATA
AIRPORTS: dict[str, geopy.Point] = {
    'UUD': geopy.Point(51.812028, 107.456993),
    'IKT': geopy.Point(52.268383, 104.378967),
    'OVB': geopy.Point(55.012638, 82.652272),
    'LED': geopy.Point(59.799225, 30.315948),
    'SVX': geopy.Point(56.741274, 60.805229),
    'DME': geopy.Point(55.407356, 37.888242)
}

# Пути к директориям по умолчанию (относительно корня)
DEFAULT_EXPORT_DIRECTORY = 'data/output'

# TODO: Хороший пакет для валидации https://pypi.org/project/pydantic-pint/
