from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from typing import Callable, Dict, List, Tuple, Type

import numpy as np

from logic_circuits.gates.gates import GateAND, GateNOT, GatePASS, GateBase, SysIN
from .gates_graphical import (
    GateAND_graphical,
    GateNOT_graphical,
    GatePass_graphical,
    Gate_graphical,
    SysIN_graphical,
)


@dataclass(frozen=True)
class GateSpec:
    """Blueprint for instantiating a logical gate when recreating composites."""

    factory: Callable[[], GateBase]


@dataclass(frozen=True)
class Blueprint:
    gate_specs: Dict[str, GateSpec]
    connections: List[Tuple[str, str, int, int]]
    input_gate_id: str
    end_gate_ids: List[str]
    num_in: int
    num_out: int


def _factory_for_gate(gate: GateBase) -> Callable[[], GateBase]:
    """Return a callable that produces a fresh logical gate equivalent to *gate*."""

    if isinstance(gate, SysIN_graphical):
        return partial(SysIN, name=gate.name, num_in=gate.num_in, num_out=gate.num_out)
    if isinstance(gate, GatePass_graphical):
        return partial(GatePASS, name=gate.name, num_in=gate.num_in, num_out=gate.num_out)
    if isinstance(gate, GateAND_graphical):
        return partial(GateAND, name=gate.name)
    if isinstance(gate, GateNOT_graphical):
        return partial(GateNOT, name=gate.name)
    if hasattr(gate, "logical_cls"):
        logical_cls: Type[GateBase] = getattr(gate, "logical_cls")
        return partial(logical_cls, instance_name=gate.name)
    raise TypeError(f"Unsupported gate type for custom save: {type(gate)!r}")


def build_blueprint(
    sysin: SysIN_graphical,
    sysout: GatePass_graphical,
    connections: List[Tuple[GateBase, GateBase, int, int]],
) -> Blueprint:
    """Construct a reusable blueprint for the current workspace configuration."""

    involved: List[GateBase] = []
    seen = set()
    for from_gate, to_gate, *_ in connections:
        if from_gate not in seen:
            involved.append(from_gate)
            seen.add(from_gate)
        if to_gate not in seen:
            involved.append(to_gate)
            seen.add(to_gate)

    for anchor in (sysin, sysout):
        if anchor not in seen:
            involved.append(anchor)
            seen.add(anchor)

    gate_ids = {gate: f"g{idx}" for idx, gate in enumerate(involved)}
    gate_specs = {gid: GateSpec(factory=_factory_for_gate(gate)) for gate, gid in gate_ids.items()}

    connection_specs = [
        (gate_ids[from_gate], gate_ids[to_gate], from_port, to_port)
        for from_gate, to_gate, from_port, to_port in connections
    ]

    return Blueprint(
        gate_specs=gate_specs,
        connections=connection_specs,
        input_gate_id=gate_ids[sysin],
        end_gate_ids=[gate_ids[sysout]],
        num_in=sysin.num_out,
        num_out=sysout.num_out,
    )


def make_custom_gate_class(name: str, blueprint: Blueprint) -> Type[GateBase]:
    """Create a new logical gate class driven by *blueprint*."""

    class _CustomGate(GateBase):
        def __init__(self, instance_name: str | None = None):
            super().__init__(blueprint.num_in, blueprint.num_out, name=name)
            self.name = instance_name or name

            # Instantiate a fresh network for this gate instance.
            self._gate_instances: Dict[str, GateBase] = {
                gid: spec.factory() for gid, spec in blueprint.gate_specs.items()
            }

            for from_id, to_id, from_port, to_port in blueprint.connections:
                to_gate = self._gate_instances[to_id]
                from_gate = self._gate_instances[from_id]
                to_gate.wire_up(from_gate, to_gate, from_port, to_port)

            self._input_gate = self._gate_instances[blueprint.input_gate_id]
            self._end_gates = [self._gate_instances[idx] for idx in blueprint.end_gate_ids]

        def _compute(self) -> np.ndarray:
            inputs = self._collect_inputs()
            ports = list(range(self._input_gate.num_out))
            self._input_gate.set_state(ports, list(bool(v) for v in inputs))

            end_state: List[bool] = []
            for gate in self._end_gates:
                gate._recompute()
                end_state.extend(bool(v) for v in gate.state)
            return np.array(end_state, dtype=bool)

    _CustomGate.__name__ = name
    return _CustomGate


def make_custom_gate_graphical_class(
    name: str,
    logical_class: Type[GateBase],
    num_in: int,
    num_out: int,
) -> Type[Gate_graphical]:
    """Return a pygame-ready wrapper around the logical custom gate class."""

    class _CustomGateGraphical(Gate_graphical):
        logical_cls = logical_class

        def __init__(
            self,
            name: str,
            x: int,
            y: int,
            w: int = 220,
            h: int = 140,
            num_in: int = num_in,
            num_out: int = num_out,
        ) -> None:
            logical_gate = logical_class(instance_name=name)
            super().__init__(logical_gate, name, x, y, w, h, num_in=num_in, num_out=num_out)

    _CustomGateGraphical.__name__ = f"{name}Graphical"
    return _CustomGateGraphical
