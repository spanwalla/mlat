import numpy as np
from config import k_dim_state, k_space_dim

class KalmanFilter:
    def __init__(self):
        self._system_vector: np.ndarray = np.zeros(k_dim_state)                             # x, размерность состояния
        self._state_transition_matrix: np.ndarray = np.zeros([k_dim_state, k_dim_state])    # F
        self._error_covariance_matrix: np.ndarray = np.zeros([k_dim_state, k_dim_state])    # Q
        self._state_covariance_matrix: np.ndarray = np.zeros([k_dim_state, k_dim_state])    # P
        self._noise_covariance_matrix: np.ndarray = np.zeros([k_space_dim, k_space_dim])    # R, размерность наблюдения
        self._observation_matrix: np.ndarray = np.zeros([k_space_dim, k_dim_state])         # H
    
    def predict(self) -> None:
        self._system_vector = self._state_transition_matrix @ self._system_vector
        self._state_covariance_matrix = self._state_transition_matrix @ self._state_covariance_matrix @ self._state_transition_matrix.T + self._error_covariance_matrix
    
    def correct(self, state_vector: np.ndarray) -> np.ndarray:
        identity_matrix = np.identity(k_dim_state)
        S = self._observation_matrix @ self._state_covariance_matrix @ self._observation_matrix.T + self._noise_covariance_matrix
        K = self._state_covariance_matrix @ self._observation_matrix.T @ np.linalg.inv(S)
        Y = state_vector - (self._observation_matrix @ self._system_vector)
        self._system_vector = self._system_vector + (K @ Y)
        self._state_covariance_matrix = (identity_matrix - K @ self._observation_matrix) @ self._state_covariance_matrix
        return self._system_vector
    