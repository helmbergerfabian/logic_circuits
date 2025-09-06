from typing import Union
import numpy as np

class Port:
    """Single boolean wire stored as (1,) ndarray."""

    def __init__(self, parent=None, init_val: bool=False):
        self.parent = parent
        self._state = np.array([init_val], dtype=bool)

    @property
    def state(self) -> np.ndarray:      # shape: (1,)
        return self._state

    @state.setter
    def state(self, v: Union[bool, np.ndarray]) -> None:
        if isinstance(v, np.ndarray):
            if v.size != 1:
                raise ValueError("Port expects a single boolean.")
            v = bool(v.reshape(-1)[0])
        self._state[:] = v

    # for a scalar bool
    @property
    def value(self) -> bool:
        return bool(self._state[0])

    @value.setter
    def value(self, v: Union[bool, np.ndarray]) -> None:
        self.state = v 