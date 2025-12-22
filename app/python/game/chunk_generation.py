import ctypes
from PIL import Image
from pathlib import Path
import numpy as np

class Chunk:
    lib = ctypes.CDLL("app/build/chunk.dll")

    SPRITE_W = 32
    SPRITE_H = 15

    @classmethod
    def load_sprite(cls, path):
        img = Image.open(path).convert("RGBA")
        arr = np.array(img, dtype=np.uint8)
        return arr.view(np.uint32).reshape(cls.SPRITE_H, cls.SPRITE_W)

    sprite_paths = [
        "grass0.png",
        "grass1.png",
        "sand.png",
        "water0.png",
    ]

    lib.generate_chunk.argtypes = [
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_int, ctypes.c_int,
        ctypes.c_int, ctypes.c_int,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int, ctypes.c_int
    ]

    lib.generate_chunk.restype = None

    @classmethod
    def generate_chunk(cls, seed, chunk_x, chunk_y, chunk_s):

        CHUNK_W = cls.SPRITE_W * chunk_s
        CHUNK_H = (cls.SPRITE_H + 1) * chunk_s - 1

        chunk = np.zeros((CHUNK_H, CHUNK_W), dtype=np.uint32)

        cls.lib.generate_chunk(
            chunk.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
            CHUNK_W, CHUNK_H,
            chunk_x, chunk_y,
            cls.atlas.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
            seed,
            cls.SPRITE_COUNT,
            chunk_s, chunk_s
        )

        image = Image.frombuffer(
            "RGBA",
            (CHUNK_W, CHUNK_H),
            chunk,
            "raw",
            "RGBA",
            0,
            1
        )

        return image
    
CWD = Path.cwd()
SOURCES = CWD / "app" / "sources"

Chunk.sprites = [Chunk.load_sprite(SOURCES / p) for p in Chunk.sprite_paths]
Chunk.atlas = np.stack(Chunk.sprites, axis=0)
Chunk.SPRITE_COUNT = Chunk.atlas.shape[0]