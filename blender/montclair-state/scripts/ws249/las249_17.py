# ws249 (2017 cross-check of las249.py): LiDAR class-2 ground, 1 m cell means, for the soccer field's WEST side x -340..-250, y -20..220 (local metres),
# from the 2023 J5D5 tile (x < -268) and the 2023 J5D6 tile (x >= -268). Writes scripts/ws249/g1m_w17.npy (box only; never committed).
# PYTHONPATH=/workspace/nj-scenes/pylib_las python3 scripts/ws249/las249.py
import laspy, numpy as np
OE, ON = 575880.0, 738340.0
F = 1200 / 3937
X0, X1, Y0, Y1 = -340.0, -250.0, -20.0, 220.0
nx, ny = int(X1 - X0), int(Y1 - Y0)
acc = np.zeros((ny, nx)); c = np.zeros((ny, nx))
for f in ("north/data/USGS_LPC_NJ_NW_New_Jersey_6_County_Lidar_2017_B17_J5D5.laz", "north/data/USGS_LPC_NJ_NW_New_Jersey_6_County_Lidar_2017_B17_J5D6.laz"):
    rd = laspy.open(f); n = 0
    for ch in rd.chunk_iterator(2_000_000):
        x = (np.asarray(ch.x) - OE) * F
        y = (np.asarray(ch.y) - ON) * F
        m = (x >= X0) & (x < X1) & (y >= Y0) & (y < Y1) & (np.asarray(ch.classification) == 2)
        if m.any():
            ix = (x[m] - X0).astype(int); iy = (y[m] - Y0).astype(int)
            np.add.at(acc, (iy, ix), np.asarray(ch.z)[m] * 0.3048006096); np.add.at(c, (iy, ix), 1); n += int(m.sum())
    print(f, n, flush=True)
G = np.where(c > 0, acc / np.maximum(c, 1), np.nan)
np.save("scripts/ws249/g1m_w17.npy", G)
print("finite", np.isfinite(G).mean())
