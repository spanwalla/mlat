import numpy as np


class KalmanFilter():
    __slots__ = [
        '_system_vector',               # x, размерность состояния
        '_state_transition_matrix',     # F
        '_error_covariance_matrix',     # Q
        '_state_covariance_matrix',     # P
        '_noise_covariance_matrix',     # R, размерность наблюдения
        '_observation_matrix'           # H
    ]
    _state_transition_matrix: np.ndarray    # указание типов для всех полей, валидация размерностей
    _observation_matrix: np.ndarray
    
    def predict(self) -> None:
        self._system_vector = self._state_transition_matrix @ self._system_vector
        self._state_covariance_matrix = self._state_transition_matrix @ self._state_covariance_matrix @ self._state_transition_matrix.T + self._error_covariance_matrix
    
    def correct(self, state_vector: np.ndarray) -> np.ndarray:
        identity_matrix = np.identity(self._system_vector.shape[0])
        S = self._observation_matrix @ self._state_covariance_matrix @ self._observation_matrix.T + self._noise_covariance_matrix
        K = self._state_covariance_matrix @ self._observation_matrix.T @ np.linalg.inv(S)
        Y = state_vector - (self._observation_matrix @ self._system_vector)
        self._system_vector = self._system_vector + (K @ Y)
        self._state_covariance_matrix = (identity_matrix - K @ self._observation_matrix) @ self._state_covariance_matrix
        return self._system_vector
    