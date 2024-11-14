from pint import UnitRegistry

# Реестр единиц измерения, для корректной работы должен использоваться единственный экземпляр на всю программу
ureg = UnitRegistry()
ureg.auto_reduce_dimensions = True  # Автоматически упрощать единицы измерения при вычислениях

# Минимальное количество приёмников, а также значение по умолчанию, если позиции приёмников не указаны
MIN_RECEIVERS: int = 4
DEFAULT_RECEIVERS: int = 4
RECEIVER_MAX_OFFSET: ureg.Quantity = ureg.Quantity(250, 'km')

# Пути к директориям по умолчанию (относительно корня)
DEFAULT_EXPORT_DIRECTORY = 'data/output'

# TODO: Хороший пакет для валидации https://pypi.org/project/pydantic-pint/
