from typing import Protocol, Iterable, List, Union
from logic_circuits.gates.port import Port
import numpy as np

Idxs = Union[int, Iterable[int]]

class HasState(Protocol):
    @property
    def state(self) -> np.ndarray: ...   # shape: (n,)


class GateBase(HasState):
    """Single node with k>=1 output wires; concrete gates implement _compute()."""
    def __init__(self, n_outputs: int, name: str):
        self.num_in = 1
        self.num_out = 1

        self.base_layer = False
        self.name = name
        if n_outputs < 1:
            raise ValueError("n_outputs must be >= 1")
        self._outs: List[Port] = [Port(self) for _ in range(n_outputs)]

    @property
    def out_ports(self) -> List[Port]:
        return self._outs
    

    @property
    def state(self) -> np.ndarray:
        if not self.base_layer: self._recompute()
        return np.concatenate([p.state for p in self._outs])

    def _set_state_vec(self, vec: np.ndarray) -> None:
        vec = np.asarray(vec, dtype=bool).reshape(-1)
        
        if vec.size != len(self._outs):
            raise ValueError(f"Output length {vec.size} != {len(self._outs)}")
        
        for p, v in zip(self._outs, vec):
            p.value = bool(v)

    def _recompute(self) -> None:
        self._set_state_vec(self._compute())

    def _compute(self) -> np.ndarray:
        raise NotImplementedError