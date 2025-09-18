from typing import Protocol, Iterable, List, Tuple, Union
from logic_circuits.utils import GateBase, Idxs, HasState
from logic_circuits.gates.port import Port

import numpy as np
import itertools

def _read(src: GateBase, idxs: Idxs) -> np.ndarray:
    s = np.concatenate([p.state for p in src._outs])
    
    if isinstance(idxs, int):
        return np.array([bool(s[idxs])], dtype=bool)
    
    return np.array([bool(s[i]) for i in idxs], dtype=bool)




class SysIN(GateBase):
    """A block of N input wires."""
    def __init__(self, num_out: int, init_vals: Iterable[bool] | None=None, name = "SYSIN"):
        self.name = name
        self.num_out = num_out
        super().__init__(n_outputs=self.num_out, name=self.name)
        
        if init_vals is None:
            init_vals = [False]*self.num_out

        vals = list(init_vals)
        if len(vals) != self.num_out: raise ValueError("init_vals length must match num.")
        
        self._ports = [Port(self, v) for v in vals]
        self.num_out = num_out
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





class GateNOT(GateBase):
    def __init__(self, input_gates: Union[GateBase, List[GateBase]], input_ports: List[int], name = "NOT"):

        self.name = name 
        self._src_gates, self._src_gates_ports = input_gates, input_ports

        if isinstance(input_gates, GateBase):
            self.a_src_gate = self._src_gates
        elif isinstance(input_gates, List) and len(input_gates) == 1:
            self.a_src_gate = self._src_gates[0]
        else: raise TypeError("Pass a single src gate as object or list of len 1 as well as a port index as int or list of len 1")
        
        a = _read(self.a_src_gate, self._src_gates_ports[0])

        if a.size != 1:
            raise ValueError("NOT inputs must have length 1.")
        super().__init__(n_outputs=a.size, name="NOT")

        self.num_in = 1
        self.num_out = 1

        self._recompute()

    def _compute(self) -> np.ndarray:
        self.a_src_gate._recompute()

        x = _read(self.a_src_gate, self._src_gates_ports)
        return np.logical_not(x)


class GateAND(GateBase):
    """Elementwise AND. Both inputs must have the same width."""
    # def __init__(self, inputs: Tuple[Tuple[HasState, Idxs], Tuple[HasState, Idxs]]):
    def __init__(self, input_gates: Union[GateBase, List[GateBase]], input_ports: List[int], name = "AND"):
        
        self.name = name

        self._src_gates, self._src_gates_ports = input_gates, input_ports

        if isinstance(input_gates, GateBase):
            # connected to only one gate
            self.a_src_gate, self.b_src_gate = self._src_gates, self._src_gates
        elif isinstance(input_gates, List) and len(input_gates) == 2:
            # connected to mulitple gates
            self.a_src_gate, self.b_src_gate = self._src_gates
        else: raise TypeError("Pass a src gates as a single object or as a list of len 2 as well as a index port as a list of len 2")

        a = _read(self.a_src_gate, self._src_gates_ports[0])
        b = _read(self.b_src_gate, self._src_gates_ports[1])

        if a.size != b.size:
            raise ValueError("AND inputs must have the same width.")
        super().__init__(n_outputs=a.size, name="AND")

        self.num_in = 2
        self.num_out = 1

        self._recompute()

    # def wire_up(self, con):
    #     s_gate, s_port, e_gate, e_port = con
    #     self.a_src_gate = s_gate
    #     self.b_src_gate =

    def _compute(self) -> np.ndarray:
        for gate in [self.a_src_gate, self.b_src_gate]:
            gate._recompute()

        a = _read(self.a_src_gate, self._src_gates_ports[0])
        b = _read(self.b_src_gate, self._src_gates_ports[1])

        return np.logical_and(a, b)
    


def truthtable(gate: GateBase, inputs: SysIN):
    cols = "  ".join([f"I{i}" for i in range(inputs.num_out)])

    print(f"{cols}   |  {getattr(gate, 'name', gate.name)}")
    print("-" * (4*inputs.num_out + 10))

    for combo in itertools.product([False, True], repeat=inputs.num_out):
        inputs.set_state(np.arange(inputs.num_out), list(combo))

        out = np.array(gate.state, dtype=int)
        bits = "   ".join(str(int(b)) for b in combo)
        
        print(f"{bits}   |  {out}")


class generic_gate(GateBase):

    def __init__(self, out_gates: List[GateBase], name):
        
        self.name = name
        self.out_gates = out_gates
        super().__init__(n_outputs=len(out_gates), name=self.name)


    def _compute(self) -> np.ndarray:
        for gate in self.out_gates:
            gate._recompute()

        return np.concatenate([g.state for g in self.out_gates])
    

# class generic_gate(GateBase):

#     def __init__(self, input_gates: List[List[GateBase]], input_ports: List[List[int]], name = "AND"):
        
#         self.name = name
#         self._src_gates, self._src_gates_ports = input_gates, input_ports
#         n_outputs = 
#         super().__init__(n_outputs=, name="AND")

#     def _compute(self) -> np.ndarray:
#         for gate in self.out_gates:
#             gate._recompute()

#         return np.concatenate([g.state for g in self.out_gates])
    
