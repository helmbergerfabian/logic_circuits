from logic_circuits.utils import (
    GateBase, 
    Idxs, 
    HasState
)
from logic_circuits.gates.port import Port

from typing import (
    List, 
    Union, 
    Type
)
import numpy as np


def _read(src: GateBase, idxs: Idxs) -> np.ndarray:
    s = np.concatenate([p.state for p in src._outs])
    return np.array(s[idxs], dtype=bool, ndmin=1)


class GateNOT(GateBase):
    def __init__(self, name = "NOT", num_in=1, num_out=1):
        assert (num_in==1 and num_out==1), "Not gate must have one/one I/O"
        super().__init__(num_in, num_out, name=name)

    def _compute(self) -> np.ndarray:
        inputs = self._collect_inputs()
        return np.logical_not(inputs[0])
    

class GateAND(GateBase):
    """Elementwise AND. Both inputs must have the same width."""
    def __init__(self, name = "AND", num_in=2, num_out=1):
        assert (num_in==2 and num_out==1), "Not gate must have one/one I/O"
        super().__init__(num_in, num_out, name=name)
    def _compute(self) -> np.ndarray:
        inputs = self._collect_inputs()
        return np.logical_and(*inputs)


class GatePASS(GateBase):
    def __init__(self, name = "PASS", num_in=1, num_out = 1):
        super().__init__(num_in, num_out, name=name)

    def _compute(self) -> np.ndarray:
        for g in self.from_gate: 
            g._recompute()

        for _from_gate, _from_port, _to_port in zip(self.from_gate, self.from_port, self.to_port):
            self.brigde[_to_port] = _read(_from_gate, _from_port)

        return self.brigde


class SysIN(GatePASS):
    def __init__(self, name="SysIN", num_in=1, num_out=1):
        super().__init__(name, num_in, num_out)
        self.base_layer = True

    def set_state(self, port_nums = Union[int, List[int]], assign = Union[bool, List[bool]]) -> None:
        curr_state = self._compute()
        if isinstance(port_nums, int):
            port_nums = [port_nums]
            assign = [assign]

        if len(port_nums) != len(assign):
            raise ValueError("idxs and vals length mismatch.")

        curr_state[port_nums] = assign
        self._set_state_vec(curr_state)

    def _compute(self) -> np.ndarray:
        return _read(self, [idx for idx in range(self.num_out)])



def make_combined_gate_class(
    name: str,
    connections,
    end_gates: List[GateBase],
    num_in: int,
    num_out: int,
    *args, **kwargs
) -> Type[GateBase]:
    """
    Factory that creates a new composite gate class.
    """

    class _CombinedGate(GateBase):
        def __init__(self, instance_name=None):
            # call GateBase init
            super().__init__(num_in, num_out, name=name)
            self.wire_idx = 0
            self.name = instance_name or name

            for from_gate, to_gate, from_port, to_port in connections:
                self.wire_up(from_gate, to_gate, from_port, to_port)

            self.end_gates = end_gates

        def wire_up(self, from_gate: GateBase, to_gate: GateBase, from_port: int, to_port: int):
            to_gate.wire_up(from_gate, to_gate, from_port, to_port)
            self.wire_idx += 1

        def _compute(self) -> np.ndarray:
            end_state = []
            for eg in self.end_gates:
                end_state += list(eg.state)
            return np.array(end_state)

    _CombinedGate.__name__ = name
    return _CombinedGate
