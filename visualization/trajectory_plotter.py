import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class TrajectoryPlotter:
    def __init__(self):
        self.x_coords = []
        self.y_coords = []
        self.z_coords = []
        self.x_coords_kalman = []
        self.y_coords_kalman = []
        self.z_coords_kalman = []
        self.x_coords_mlat = []
        self.y_coords_mlat = []
        self.z_coords_mlat = []
        self.fig = plt.figure(figsize=(10, 8))
        # self.fig_mlat = plt.figure(figsize=(10, 8))
        # self.fig_kalman = plt.figure(figsize=(10, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')
        # self.ax_mlat = self.fig_mlat.add_subplot(111, projection='3d')
        # self.ax_kalman = self.fig_kalman.add_subplot(111, projection='3d')

    def add_point(self, x, y, z):
        self.x_coords.append(x)
        self.y_coords.append(y)
        self.z_coords.append(z)
        
    def add_point_mlat(self, x, y, z):
        self.x_coords_mlat.append(x)
        self.y_coords_mlat.append(y)
        self.z_coords_mlat.append(z)
        
    def add_point_kalman(self, x, y, z):
        self.x_coords_kalman.append(x)
        self.y_coords_kalman.append(y)
        self.z_coords_kalman.append(z)

    def plot(self, show=True, col = 'blue'):
        """
        Строит 3D график на основе добавленных точек.
        :param show: Если True, отображает график сразу.
        """
        self.ax.clear()  # Очистить график перед обновлением
        self.ax.plot(self.x_coords, self.y_coords, self.z_coords, label='Реальные значения', color=col)
        self.ax.plot(self.x_coords, self.y_coords, self.z_coords, label='MLAT', color='green')
        self.ax.plot(self.x_coords_kalman, self.y_coords_kalman, self.z_coords_kalman, label='Фильтр Калмана', color='red')
        # Устанавливаем метки осей и заголовок
        self.ax.set_xlabel('X (Координата)')
        self.ax.set_ylabel('Y (Координата)')
        self.ax.set_zlabel('Z (Координата)')
        self.ax.set_title('3D график траектории')
        self.ax.legend()

        if show:
            plt.show()
            
    def plot_mlat(self, show=True, col = 'green'):
        """
        Строит 3D график на основе добавленных точек.
        :param show: Если True, отображает график сразу.
        """
        #self.ax_mlat.clear()  # Очистить график перед обновлением
        self.ax.plot(self.x_coords_mlat, self.y_coords_mlat, self.z_coords_mlat, label='Траектория', color=col)
        print(len(self.x_coords_mlat))

        if show:
            plt.show()
            
    def plot_kalman(self, show=False, col = 'red'):
        """
        Строит 3D график на основе добавленных точек.
        :param show: Если True, отображает график сразу.
        """
        #self.ax_kalman.clear()  # Очистить график перед обновлением
        self.ax.plot(self.x_coords_kalman, self.y_coords_kalman, self.z_coords_kalman, label='Траектория', color=col)

        if show:
            plt.show()
