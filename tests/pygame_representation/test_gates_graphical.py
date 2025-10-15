import math

import numpy as np
import pygame
import pytest

from logic_circuits.pygame_representation.gates_graphical import (
    GateAND_graphical,
    GateNOT_graphical,
    GatePass_graphical,
    SysIN_graphical,
)
from logic_circuits.pygame_representation.ports import Port_graphical


@pytest.fixture
def surface():
    return pygame.Surface((600, 400))


def assert_ports_aligned(ports, gate_rect, pad, expected_count):
    assert len(ports) == expected_count
    for port in ports:
        assert isinstance(port, Port_graphical)
        # ports are anchored relative to the gate rectangle
        assert gate_rect.collidepoint(tuple(port.screen_pos()))
        if port.kind == "in":
            assert math.isclose(port.screen_pos().x, gate_rect.left + pad, abs_tol=1e-6)
        else:
            assert math.isclose(port.screen_pos().x, gate_rect.right - pad, abs_tol=1e-6)


def test_pass_graphical_initial_layout():
    gate = GatePass_graphical("pass", x=20, y=25, w=180, h=120, num_in=3, num_out=3)

    assert gate.rect.topleft == (20, 25)
    assert gate.rect.size == (180, 120)
    assert gate.num_in == 3 and gate.num_out == 3

    assert_ports_aligned(gate.inputs, gate.rect, gate.PAD, 3)
    assert_ports_aligned(gate.outputs, gate.rect, gate.PAD, 3)

    # control rectangles are anchored to the top/bottom centre
    assert gate.plus.midtop == (gate.rect.centerx, gate.rect.top)
    assert gate.minus.midbottom == (gate.rect.centerx, gate.rect.bottom)

    # logical state mirrors the graphical configuration
    assert gate.brigde.shape == (gate.num_in,)
    assert len(gate.out_ports) == gate.num_out


def test_increase_and_decrease_ports_updates_geometry_and_logic():
    gate = GatePass_graphical("pass", x=0, y=0, w=200, h=150, num_in=1, num_out=1)

    gate.increase_ports()
    assert gate.num_in == gate.num_out == 2
    assert_ports_aligned(gate.inputs, gate.rect, gate.PAD, 2)
    assert_ports_aligned(gate.outputs, gate.rect, gate.PAD, 2)
    assert gate.brigde.shape == (2,)
    assert len(gate.out_ports) == 2

    gate.increase_ports()
    assert gate.num_in == gate.num_out == 3
    assert gate.brigde.shape == (3,)

    # decrease down to one and ensure it does not go below
    gate.decrease_ports()
    assert gate.num_in == gate.num_out == 2
    gate.decrease_ports()
    assert gate.num_in == gate.num_out == 1
    gate.decrease_ports()
    assert gate.num_in == gate.num_out == 1


def test_move_by_keeps_controls_and_ports_synced():
    gate = GatePass_graphical("pass", x=10, y=10, w=160, h=90, num_in=2, num_out=2)
    original_inputs = [p.offset.copy() for p in gate.inputs]
    original_outputs = [p.offset.copy() for p in gate.outputs]

    gate.move_by(15, 20)

    assert gate.rect.topleft == (25, 30)
    assert gate.plus.midtop == (gate.rect.centerx, gate.rect.top)
    assert gate.minus.midbottom == (gate.rect.centerx, gate.rect.bottom)

    # port offsets are relative and should be unchanged
    for port, offset in zip(gate.inputs, original_inputs):
        assert port.offset == offset
    for port, offset in zip(gate.outputs, original_outputs):
        assert port.offset == offset


def test_draw_realigns_controls(surface):
    gate = GatePass_graphical("pass", x=0, y=0, w=210, h=110, num_in=2, num_out=2)

    # perturb the control rectangles intentionally
    gate.plus.topleft = (5, 5)
    gate.minus.topleft = (5, 5)

    gate.draw(surface)

    assert gate.plus.midtop == (gate.rect.centerx, gate.rect.top)
    assert gate.minus.midbottom == (gate.rect.centerx, gate.rect.bottom)


def test_hover_detection_for_controls_and_body():
    gate = GatePass_graphical("pass", x=40, y=60, w=120, h=100, num_in=1, num_out=1)

    assert gate.hover(gate.rect.center)
    assert gate.hover_plus(gate.plus.center)
    assert gate.hover_minus(gate.minus.center)

    assert not gate.hover((gate.rect.right + 5, gate.rect.bottom + 5))


def test_sysin_resize_preserves_base_layer_and_state_semantics():
    gate = SysIN_graphical("sys", x=0, y=0, w=200, h=120, num_in=2, num_out=2)

    assert gate.base_layer is True
    gate.set_state([0, 1], [True, False])
    np.testing.assert_array_equal(gate.state, np.array([True, False], dtype=bool))

    gate.increase_ports()  # -> 3 inputs/outputs
    assert gate.base_layer is True
    assert gate.num_in == gate.num_out == 3
    assert gate.brigde.shape == (3,)
    assert len(gate.out_ports) == 3

    gate.set_state(2, True)
    np.testing.assert_array_equal(gate.state, np.array([False, False, True], dtype=bool))

    gate.decrease_ports()  # -> 2
    gate.decrease_ports()  # -> 1
    gate.set_state(0, False)
    np.testing.assert_array_equal(gate.state, np.array([False], dtype=bool))


def test_gate_and_and_not_graphical_create_ports_and_hover(surface):
    and_gate = GateAND_graphical("and", x=5, y=5, w=180, h=120, num_in=2, num_out=1)
    not_gate = GateNOT_graphical("not", x=10, y=15, w=150, h=90, num_in=1, num_out=1)

    assert_ports_aligned(and_gate.inputs, and_gate.rect, and_gate.PAD, 2)
    assert_ports_aligned(and_gate.outputs, and_gate.rect, and_gate.PAD, 1)
    assert_ports_aligned(not_gate.inputs, not_gate.rect, not_gate.PAD, 1)
    assert_ports_aligned(not_gate.outputs, not_gate.rect, not_gate.PAD, 1)

    # draw should not raise and should render ports in hover/no-hover states
    and_gate.draw(surface)
    not_gate.draw(surface)

    assert and_gate.hover(and_gate.rect.center)
    assert not not_gate.hover((not_gate.rect.right + 10, not_gate.rect.bottom + 10))
