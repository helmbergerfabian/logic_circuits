import os
import sys
from pathlib import Path
import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture(scope="session", autouse=True)
def init_pygame():
    import pygame

    pygame.display.init()
    pygame.font.init()
    yield
    pygame.font.quit()
    pygame.display.quit()
