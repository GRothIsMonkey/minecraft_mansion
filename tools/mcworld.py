"""Minimal reader for Minecraft 1.8 (Anvil, pre-flattening) world saves.

Only what the validator needs: blocks (id + metadata), tile entities and
entities inside a bounding box.
"""
import gzip
import io
import os
import struct
import zlib

import numpy as np


# ---------------------------------------------------------------- NBT -------
def _read_payload(f, tag):
    if tag == 1:
        return struct.unpack('>b', f.read(1))[0]
    if tag == 2:
        return struct.unpack('>h', f.read(2))[0]
    if tag == 3:
        return struct.unpack('>i', f.read(4))[0]
    if tag == 4:
        return struct.unpack('>q', f.read(8))[0]
    if tag == 5:
        return struct.unpack('>f', f.read(4))[0]
    if tag == 6:
        return struct.unpack('>d', f.read(8))[0]
    if tag == 7:
        n = struct.unpack('>i', f.read(4))[0]
        return f.read(n)
    if tag == 8:
        n = struct.unpack('>H', f.read(2))[0]
        return f.read(n).decode('utf-8', 'replace')
    if tag == 9:
        et = f.read(1)[0]
        n = struct.unpack('>i', f.read(4))[0]
        return [_read_payload(f, et) for _ in range(n)]
    if tag == 10:
        d = {}
        while True:
            t = f.read(1)[0]
            if t == 0:
                return d
            n = struct.unpack('>H', f.read(2))[0]
            name = f.read(n).decode('utf-8', 'replace')
            d[name] = _read_payload(f, t)
    if tag == 11:
        n = struct.unpack('>i', f.read(4))[0]
        return list(struct.unpack('>%di' % n, f.read(4 * n)))
    raise ValueError('bad tag %d' % tag)


def read_nbt(data):
    f = io.BytesIO(data)
    t = f.read(1)[0]
    n = struct.unpack('>H', f.read(2))[0]
    f.read(n)
    return _read_payload(f, t)


def read_nbt_file(path):
    with open(path, 'rb') as fh:
        raw = fh.read()
    try:
        raw = gzip.decompress(raw)
    except OSError:
        pass
    return read_nbt(raw)


# ------------------------------------------------------------- regions ------
class World:
    def __init__(self, world_dir):
        self.dir = world_dir
        self._chunks = {}

    def chunk(self, cx, cz):
        key = (cx, cz)
        if key in self._chunks:
            return self._chunks[key]
        rx, rz = cx >> 5, cz >> 5
        path = os.path.join(self.dir, 'region', 'r.%d.%d.mca' % (rx, rz))
        result = None
        if os.path.exists(path):
            with open(path, 'rb') as fh:
                data = fh.read()
            idx = 4 * ((cx & 31) + (cz & 31) * 32)
            off = (data[idx] << 16 | data[idx + 1] << 8 | data[idx + 2])
            if off:
                start = off * 4096
                length = struct.unpack('>i', data[start:start + 4])[0]
                comp = data[start + 4]
                payload = data[start + 5:start + 4 + length]
                raw = zlib.decompress(payload) if comp == 2 else gzip.decompress(payload)
                result = read_nbt(raw)['Level']
        self._chunks[key] = result
        return result

    def box(self, x1, y1, z1, x2, y2, z2):
        """Return (ids, metas) numpy arrays indexed [x-x1, y-y1, z-z1]."""
        sx, sy, sz = x2 - x1 + 1, y2 - y1 + 1, z2 - z1 + 1
        ids = np.zeros((sx, sy, sz), dtype=np.int32)
        metas = np.zeros((sx, sy, sz), dtype=np.int32)
        for cx in range(x1 >> 4, (x2 >> 4) + 1):
            for cz in range(z1 >> 4, (z2 >> 4) + 1):
                ch = self.chunk(cx, cz)
                if ch is None:
                    continue
                for sec in ch.get('Sections', []):
                    sy0 = sec['Y'] * 16
                    if sy0 + 15 < y1 or sy0 > y2:
                        continue
                    blocks = np.frombuffer(sec['Blocks'], dtype=np.uint8).astype(np.int32)
                    blocks = blocks.reshape(16, 16, 16)  # [y][z][x]
                    if 'Add' in sec:
                        add = np.frombuffer(sec['Add'], dtype=np.uint8)
                        addn = np.empty(4096, dtype=np.int32)
                        addn[0::2] = add & 15
                        addn[1::2] = add >> 4
                        blocks = blocks + (addn.reshape(16, 16, 16) << 8)
                    dat = np.frombuffer(sec['Data'], dtype=np.uint8)
                    datn = np.empty(4096, dtype=np.int32)
                    datn[0::2] = dat & 15
                    datn[1::2] = dat >> 4
                    datn = datn.reshape(16, 16, 16)
                    for ly in range(16):
                        wy = sy0 + ly
                        if wy < y1 or wy > y2:
                            continue
                        for lz in range(16):
                            wz = cz * 16 + lz
                            if wz < z1 or wz > z2:
                                continue
                            xa = max(x1, cx * 16)
                            xb = min(x2, cx * 16 + 15)
                            if xa > xb:
                                continue
                            ids[xa - x1:xb - x1 + 1, wy - y1, wz - z1] = \
                                blocks[ly, lz, xa - cx * 16:xb - cx * 16 + 1]
                            metas[xa - x1:xb - x1 + 1, wy - y1, wz - z1] = \
                                datn[ly, lz, xa - cx * 16:xb - cx * 16 + 1]
        return ids, metas

    def tile_entities(self, x1, y1, z1, x2, y2, z2):
        out = []
        for cx in range(x1 >> 4, (x2 >> 4) + 1):
            for cz in range(z1 >> 4, (z2 >> 4) + 1):
                ch = self.chunk(cx, cz)
                if ch is None:
                    continue
                for te in ch.get('TileEntities', []):
                    if x1 <= te['x'] <= x2 and y1 <= te['y'] <= y2 and z1 <= te['z'] <= z2:
                        out.append(te)
        return out

    def entities(self, x1, y1, z1, x2, y2, z2):
        out = []
        for cx in range(x1 >> 4, (x2 >> 4) + 1):
            for cz in range(z1 >> 4, (z2 >> 4) + 1):
                ch = self.chunk(cx, cz)
                if ch is None:
                    continue
                for e in ch.get('Entities', []):
                    x, y, z = e['Pos']
                    if x1 <= x < x2 + 1 and y1 <= y < y2 + 1 and z1 <= z < z2 + 1:
                        out.append(e)
        return out
