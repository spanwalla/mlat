from pint import UnitRegistry

# Реестр единиц измерения, для корректной работы должен использоваться единственный экземпляр на всю программу
ureg = UnitRegistry()
ureg.auto_reduce_dimensions = True  # Автоматически упрощать единицы измерения при вычислениях

# Минимальное количество приёмников, а также значение по умолчанию, если позиции приёмников не указаны
MIN_RECEIVERS: int = 4
DEFAULT_RECEIVERS: int = 4
RECEIVER_MAX_OFFSET: ureg.Quantity = ureg.Quantity(250, 'km')
EQUATIONS_COUNT: int = int((DEFAULT_RECEIVERS * (DEFAULT_RECEIVERS - 1)) / 2)
MAX_ITERATIONS_COUNT: int = 1

#array_dispersion = [1e4, 9000, 1e3, 10, 1e-6]
k_sample_rate = 42
k_duration_interval = 100
k_duration_overstatement = 0.05 * k_duration_interval
k_wave_speed = 300000.0
k_space_dim = 3
k_dim_state = 9
k_equations_count = 6
k_receivers_count = 4
k_noise_dispersion = 1e-6
k_light_speed = 3e5
# Пути к директориям по умолчанию (относительно корня)
DEFAULT_EXPORT_DIRECTORY = 'data/output'
DEFAULT_IMPORT_DIRECTORY = '../data/output/simulation'

# TODO: Хороший пакет для валидации https://pypi.org/project/pydantic-pint/
