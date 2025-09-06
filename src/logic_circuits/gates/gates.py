from typing import Protocol, Iterable, List, Tuple, Union
from logic_circuits.utils import GateBase, Idxs, HasState
from logic_circuits.gates.port import Port

import numpy as np
import itertools

def _read(src: HasState, idxs: Idxs) -> np.ndarray:
    s = src.state
    
    if isinstance(idxs, int):
        return np.array([bool(s[idxs])], dtype=bool)
    
    return np.array([bool(s[i]) for i in idxs], dtype=bool)

def truthtable(gate_class, n: int):
    inputs = SysIN(n, init_vals=[False]*n)
    wires = tuple((inputs, k) for k in range(n))
    gate: GateBase = gate_class(wires)
    cols = "  ".join([f"I{i}" for i in range(n)])

    print(f"{cols}   |  {getattr(gate, 'name', gate_class.__name__)}")
    print("-" * (4*n + 10))

    for combo in itertools.product([False, True], repeat=n):
        inputs.set_state((list(range(n)), list(combo)))

        gate.recompute()
        out = np.array(gate.state, dtype=int)
        bits = "   ".join(str(int(b)) for b in combo)
        
        print(f"{bits}   |  {out}")


class SysIN:
    """A block of N input wires."""
    def __init__(self, num: int, init_vals: Iterable[bool] | None=None):
        if init_vals is None:
            init_vals = [False]*num
        vals = list(init_vals)
            
        if len(vals) != num: raise ValueError("init_vals length must match num.")
        self._ports: List[Port] = [Port(self, v) for v in vals]

    @property
    def out_ports(self) -> List[Port]:
        return self._ports

    @property
    def state(self) -> np.ndarray:      # (N,)
        return np.concatenate([p.state for p in self._ports])

    def set_state(self, assignment: Tuple[List[int], List[Union[bool, np.ndarray]]]) -> None:
        idxs, vals = assignment
        if len(idxs) != len(vals):
            raise ValueError("idxs and vals length mismatch.")
        for i, v in zip(idxs, vals):
            self._ports[i].state = v