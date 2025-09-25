from typing import Protocol, Iterable, List, Union
from logic_circuits.gates.port import Port
import logic_circuits.gates.gates as gates
import numpy as np

Idxs = Union[int, Iterable[int]]

class HasState(Protocol):
    @property
    def state(self) -> np.ndarray: ...   # shape: (n,)


class GateBase(HasState):
    """Single node with k>=1 output wires; concrete gates implement _compute()."""
    def __init__(self, num_in: int = 1, num_out: int = 1, name: str = None):
        if num_in < 1 or num_out < 1:
            raise ValueError("number of I/O must be >= 1")

        self.num_in = num_in
        self.num_out = num_out
        self.name = name

        self._outs: List[Port] = [Port(self) for _ in range(self.num_out)]
        self.base_layer = False

        # buffer
        self.brigde = np.zeros(self.num_in, dtype=bool)

        # wiring
        self.from_gate: List["GateBase"] = []
        self.from_port: List[int] = []
        self.to_gate: List["GateBase"] = []
        self.to_port: List[int] = []
        
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
    
    def wire_up(self, from_gate, to_gate, from_port: int, to_port: int):
        assert from_gate != to_gate, "No self wiring is allowed"
        self.from_gate.append(from_gate)
        self.to_gate.append(to_gate)
        self.from_port.append(from_port)
        self.to_port.append(to_port)

    def _collect_inputs(self) -> List[np.ndarray]:
        if len(np.unique(self.to_port)) != self.num_in:
            raise Exception(f"Gate {self.name} not fully wired up. ports {np.unique(self.to_port)}")

        for g in self.from_gate:
            g._recompute()

        for _from_gate, _from_port, _to_port in zip(self.from_gate, self.from_port, self.to_port):
            self.brigde[_to_port] = gates._read(_from_gate, _from_port)

        return self.brigde