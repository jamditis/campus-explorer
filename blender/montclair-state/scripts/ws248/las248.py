# ws248: LiDAR class-2 ground to 1 m cell means for x -320..-140, y -20..220 (local metres), 2023 and 2017 J5D6 tiles.
# Writes g1m_23.npy / g1m_17.npy (box only; rasters are never committed). Run from montclair-state/ with
# PYTHONPATH=/workspace/nj-scenes/pylib_las:/workspace/nj-scenes/blender_pylib_proj python3 scripts/ws248/las248.py
import laspy, numpy as np
OE, ON = 575880.0, 738340.0
F = 1200 / 3937
X0, X1, Y0, Y1 = -320.0, -140.0, -20.0, 220.0
for tag, f in (("23", "data/lpc_2023_J5D6.laz"), ("17", "north/data/USGS_LPC_NJ_NW_New_Jersey_6_County_Lidar_2017_B17_J5D6.laz")):
    rd = laspy.open(f)
    P = []
    for ch in rd.chunk_iterator(3_000_000):
        x = (np.asarray(ch.x) - OE) * F
        y = (np.asarray(ch.y) - ON) * F
        m = (x >= X0) & (x < X1) & (y >= Y0) & (y < Y1) & (np.asarray(ch.classification) == 2)
        if m.any():
            P.append(np.c_[x[m], y[m], np.asarray(ch.z)[m] * 0.3048006096])
    P = np.vstack(P)
    nx, ny = int(X1 - X0), int(Y1 - Y0)
    ix = (P[:, 0] - X0).astype(int)
    iy = (P[:, 1] - Y0).astype(int)
    acc = np.zeros((ny, nx))
    c = np.zeros((ny, nx))
    np.add.at(acc, (iy, ix), P[:, 2])
    np.add.at(c, (iy, ix), 1)
    np.save("scripts/ws248/g1m_%s.npy" % tag, np.where(c > 0, acc / np.maximum(c, 1), np.nan))
    print(tag, len(P))
