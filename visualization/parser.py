import csv

class Parser:
    def __init__(self):
        self.trajectory_file = ''
        self.toa_file = ''

    def parse_trajectory(self, trajectory_file):
        self.trajectory_file = trajectory_file
        """Парсит траектории из первого файла."""
        #trajectory_data = []
        with open(self.trajectory_file, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Пропускаем заголовок
            for row in reader:
                timestamp = int(row[0])
                position = list(map(float, row[1].strip('\"').split(',')))
                altitude = float(row[2])
                #trajectory_data.append((timestamp, position[0], position[1], altitude))
                yield (timestamp, position[0], position[1], altitude)
        #return trajectory_data

    def parse_toa(self, toa_file):
        self.toa_file = toa_file
        """Парсит данные TOA из второго файла."""
        #toa_data = []
        with open(self.toa_file, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Пропускаем заголовок
            for row in reader:
                timestamp = int(row[0])
                toa_values = list(map(float, row[1:5]))
                #toa_data.append((timestamp, *toa_values))
                yield (timestamp, *toa_values)
        #return toa_data
