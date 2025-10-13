import pygame
from pygame.math import Vector2

from logic_circuits.pygame_representation import fonts
from logic_circuits.pygame_representation.colors import BG, TEXT, WIRE_HOT
from logic_circuits.pygame_representation.utils import (
    draw_grid, cubic_bezier,
    cut_wired, block_under_mouse,
    port_under_mouse, find_wire_under_mouse,
    truthtable_print
)
from logic_circuits.pygame_representation.gates_graphical import (
    GateGENERIC_graphical,
    GatePass_graphical,
    SysIN_graphical,
)
from logic_circuits.pygame_representation.wires import Wire
from logic_circuits.pygame_representation.button import Button
from logic_circuits.pygame_representation.library import (
    library_items,
    add_library_item,
)
from logic_circuits.pygame_representation.pygame_cfg import *
from logic_circuits.gates.gates import make_combined_gate_class
def main():
    # -------------------
    # INIT
    # -------------------
    pygame.init()
    fonts.init()

    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Wire Editor")
    clock = pygame.time.Clock()

    # -------------------
    # UI ELEMENTS
    # -------------------
    save_button = Button(
        rect=(W - 280, 20, 120, 40),
        text="Save",
        font=fonts.FONT,
        bg_color=(70, 70, 200),
        fg_color=(255, 255, 255),
        hover_color=(90, 90, 220),
    )

    play_button = Button(
        rect=(W - 140, 20, 120, 40),
        text="Play",
        font=fonts.FONT,
        bg_color=(50, 180, 90),
        fg_color=(255, 255, 255),
        hover_color=(70, 200, 110),
    )

    # -------------------
    # BLOCKS / STATE
    # -------------------
    sysin = SysIN_graphical(name="SysIN", num_in=2, num_out=2, x=50, y = (H-140)//2)
    sysout = GatePass_graphical(name="SysOUT", num_in=2, num_out=2, x=600, y = (H-140)//2)
    blocks = [sysin, sysout]

    # Interaction state
    wires = []
    connections = []

    dragging_library_item = None
    ghost_gate = None

    drag_stop_port_g = None
    drag_start_gate_g = None

    drag_start_port_g = None

    port_drag_pos = Vector2(0, 0)
    block_drag_offset = Vector2(0, 0)

    truth_lines = None
    custom_gate_count = 0
    running = True

    # -------------------
    # MAIN LOOP
    # -------------------
    while running:
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # -------------------
            # LEFT MOUSE DOWN
            # -------------------
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check if clicked on a library item
                for item in library_items:
                    if item.hover((mx, my)):
                        dragging_library_item = item
                        ghost_gate = item.gate_class("", x=mx-100/2, y=my-100/2, w=100, h=100)
                        break
                else:
                    # Normal port/gate drag logic
                    port_g = port_under_mouse((mx, my), blocks)
                    gate_g = block_under_mouse((mx, my), blocks)

                    if port_g and port_g.kind == "out":
                        drag_start_port_g = port_g
                        port_drag_pos = Vector2(mx, my)

                    elif gate_g and not port_g:
                        drag_start_gate_g = gate_g
                        block_drag_offset = Vector2(mx - gate_g.rect.x, my - gate_g.rect.y)
        
                for b in blocks:
                    if isinstance(b, (SysIN_graphical, GatePass_graphical)):
                        if b.hover_plus((mx, my)):
                            b.increase_ports()
                            wires = cut_wired(wires, b)

                        if b.hover_minus((mx, my)):
                            b.decrease_ports()
                            wires = cut_wired(wires, b)

            # -------------------
            # MOUSE MOVE
            # -------------------
            elif event.type == pygame.MOUSEMOTION:
                if ghost_gate:
                    ghost_gate.rect.center = (mx, my)
                    ghost_gate._make_ports()
                if drag_start_port_g:
                    port_drag_pos = Vector2(mx, my)
                if drag_start_gate_g:
                    block_drag_pos = Vector2(mx, my)

            # -------------------
            # LEFT MOUSE UP
            # -------------------
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if ghost_gate and dragging_library_item:
                    # Only drop if outside library area
                    if mx > LIBRARY_WIDTH:
                        new_gate = dragging_library_item.gate_class(
                            f"{dragging_library_item.text.lower()}",
                            x=mx-50,
                            y=my-50,
                            w=100, h=100
                        )
                        blocks.append(new_gate)
                    ghost_gate = None
                    dragging_library_item = None

                elif drag_start_port_g:
                    drag_stop_port_g = port_under_mouse((mx, my), blocks, kind="in")
                    if drag_stop_port_g and drag_stop_port_g != drag_start_port_g:
                        if drag_start_port_g.gate != drag_stop_port_g.gate:
                            wires.append(Wire(drag_start_port_g, drag_stop_port_g))
                            connections.append(
                                (
                                    drag_start_port_g.gate,
                                    drag_stop_port_g.gate,
                                    drag_start_port_g.index,
                                    drag_stop_port_g.index,
                                )
                            )
                    drag_start_port_g = None

                if drag_start_gate_g:
                    drag_start_gate_g = None

            # -------------------
            # RIGHT MOUSE DOWN
            # -------------------
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                if ghost_gate:
                    ghost_gate = None
                    dragging_library_item = None
                elif drag_start_port_g:
                    drag_start_port_g = None
                else:
                    # Try wire
                    w = find_wire_under_mouse((mx, my), wires)
                    if w:
                        wires.remove(w)
                        conn_tuple = (w.a.gate, w.b.gate, w.a.index, w.b.index)
                        if conn_tuple in connections:
                            connections.remove(conn_tuple)
                    else:
                        # Try block
                        g = block_under_mouse((mx, my), blocks)
                        if g and g in blocks:
                            wires = cut_wired(wires, g)
                            connections[:] = [
                                c for c in connections if c[0] != g and c[1] != g
                            ]
                            if not isinstance(g, (SysIN_graphical, GatePass_graphical)):
                                blocks.remove(g)

            # -------------------
            # ESC to cancel drags
            # -------------------
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                drag_start_port_g = None
                drag_start_gate_g = None
                ghost_gate = None
                dragging_library_item = None

            # -------------------
            # PLAY BUTTON
            # -------------------
            if save_button.handle_event(event):
                if len(connections) > 0:
                    custom_gate_count += 1
                    base_name = f"Custom{custom_gate_count}"
                    add_library_item(base_name.upper(), GateGENERIC_graphical)

            if play_button.handle_event(event):
                if len(connections) > 0:
                    new_gate = make_combined_gate_class(
                        "SysOut",
                        connections=connections,
                        end_gates=[sysout],
                        num_in=sysin.num_in,
                        num_out=sysout.num_out,
                        x=0, y=0
                    )
                    this_gate = new_gate("SysOUT")
                    # truthtable_window(this_gate, sysin)
                    truthtable_print(this_gate, sysin)

        # -------------------
        # Dragging gates around
        # -------------------
        if drag_start_gate_g:
            grid_size = 10
            snapped_x = (mx - block_drag_offset.x) // grid_size * grid_size
            snapped_y = (my - block_drag_offset.y) // grid_size * grid_size
            drag_start_gate_g.rect.topleft = (snapped_x, snapped_y)
            drag_start_gate_g._make_ports()
            if isinstance(drag_start_gate_g, (SysIN_graphical, GatePass_graphical)):
                drag_start_gate_g.plus.topleft = (
                    snapped_x + drag_start_gate_g._w // 2,
                    snapped_y,
                )
                drag_start_gate_g.minus.topleft = (
                    snapped_x + drag_start_gate_g._w // 2,
                    snapped_y + drag_start_gate_g._h - drag_start_gate_g._h // 10,
                )

        # -------------------
        # Drawing
        # -------------------
        screen.fill(BG)
        draw_grid(screen, W, H)

        # Draw library sidebar
        # pygame.draw.rect(screen, (30, 30, 30), (0, 200, LIBRARY_WIDTH, LIBRARY_HEIGHT))
        for item in library_items:
            item.draw(screen)

        # Blocks
        for b_ in blocks:
            b_.draw(screen)

        # Ghost gate being dragged
        if ghost_gate:
            ghost_gate.draw(screen)

        # Wires
        hot_wire = find_wire_under_mouse((mx, my), wires)
        for w in wires:
            w.draw(screen, hot=(w is hot_wire))

        # Live wire being dragged
        if drag_start_port_g:
            p0 = drag_start_port_g.screen_pos()
            p3 = port_drag_pos
            dx = max(40, abs(p3.x - p0.x) * 0.5)
            c1, c2 = Vector2(p0.x + dx, p0.y), Vector2(p3.x - dx, p3.y)
            pts = cubic_bezier(p0, c1, c2, p3, steps=36)
            pygame.draw.lines(screen, WIRE_HOT, False, pts, 3)

            drag_stop_port_g = port_under_mouse((mx, my), blocks, kind="in")
            if drag_stop_port_g:
                drag_stop_port_g.draw(screen, hot=True)

            hint = fonts.FONT.render(
                "Release on input to connect (RMB/ESC cancel)", True, TEXT
            )
            screen.blit(hint, (12, 10))

        else:
            hint = fonts.FONT.render(
                "LMB drag block | LMB drag from output→input | RMB delete wire/gate",
                True,
                TEXT,
            )
            screen.blit(hint, (12, 10))

        save_button.draw(screen)
        play_button.draw(screen)
        if truth_lines:
            x, y = LIBRARY_WIDTH + 20, H - 150   # position bottom right
            for i, line in enumerate(truth_lines):
                surf = fonts.FONT.render(line, True, (255, 255, 255))
                screen.blit(surf, (x, y + i * 20))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
