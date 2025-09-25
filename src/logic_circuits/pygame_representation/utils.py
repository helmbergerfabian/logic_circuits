import pygame
from .colors import GRID
import io, contextlib
import tkinter as tk
from .pygame_cfg import *


def draw_grid(surface, W, H, gap=24):
    for x in range(0, W, gap):
        pygame.draw.line(surface, GRID, (x, 0), (x, H))
    for y in range(0, H, gap):
        pygame.draw.line(surface, GRID, (0, y), (W, y))

def lerp(a, b, t):
    return a + (b - a) * t

def cubic_bezier(p0, p1, p2, p3, steps=30):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        a = lerp(p0, p1, t)
        b = lerp(p1, p2, t)
        c = lerp(p2, p3, t)
        d = lerp(a, b, t)
        e = lerp(b, c, t)
        f = lerp(d, e, t)
        pts.append((int(f.x), int(f.y)))
    return pts

def cut_wired(wires, gate):
    new_wires = [
        wire for wire in wires if wire.a.gate != gate and wire.b.gate != gate
    ]
    return new_wires

def all_ports(blocks):
    return [p for b in blocks for p in b.inputs + b.outputs]

def block_under_mouse(mouse, blocks) -> None:
    for b in blocks:
        if b.hover(mouse):
            return b
    return None

def port_under_mouse(mouse, blocks, kind=None):
    for p in all_ports(blocks):
        if (kind is None or p.kind == kind) and p.hover(mouse):
            return p
    return None


def find_wire_under_mouse(mouse, wires):
    for w in reversed(wires):
        if w.hit_test(mouse):
            return w
    return None
import itertools


from logic_circuits.gates.gates import GateBase,SysIN
import numpy as np
def truthtable(gate: GateBase, inputs: SysIN):
    cols = "  ".join([f"I{i}" for i in range(inputs.num_out)])

    print(f"{cols}   | {getattr(gate, 'name', gate.name)}")
    print("-" * (4*inputs.num_out + 10))

    for combo in itertools.product([False, True], repeat=inputs.num_out):
        inputs.set_state(np.arange(inputs.num_out), list(combo))

        out = np.array(gate.state, dtype=int)
        bits = "   ".join(str(int(b)) for b in combo)
        
        print(f"{bits}   |  {out}")



def truthtable_str(this_gate, sysin):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        truthtable(this_gate, sysin)
    return buf.getvalue().splitlines()

def truthtable_print(this_gate, sysin):
    lines = truthtable_str(this_gate, sysin)
    print("\n".join(lines))

def truthtable_window(this_gate, sysin, root=None):
    lines = truthtable_str(this_gate, sysin)

    if root is None:
        root = tk.Tk()
        owns_root = True
    else:
        owns_root = False

    win = tk.Toplevel(root) if not owns_root else root
    win.title("Truth Table")

    text = tk.Text(win, wrap="none")
    text.pack(expand=True, fill="both")

    for line in lines:
        text.insert("end", line + "\n")

    if owns_root:
        # only start the loop if we created the root ourselves
        root.mainloop()


from logic_circuits.pygame_representation.button import Button  # if in separate file
from logic_circuits.pygame_representation import fonts

play_button = Button(
    rect=(W - 140, 20, 120, 40),   # position + size
    text="Play",
    font=fonts.FONT,
    bg_color=(50, 180, 90),
    fg_color=(255, 255, 255),
    hover_color=(70, 200, 110),
)

