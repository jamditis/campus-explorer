import numpy as np, laspy, json
FT = 1200/3937
d = json.load(open('data/scene_data.json')); E0, N0, H = d['E0_ftUS'], d['N0_ftUS'], d['half_m']
las = laspy.read('data/lpc_2023_J5D6.laz')
X = (np.asarray(las.x) - E0)*FT; Y = (np.asarray(las.y) - N0)*FT
m = (abs(X) < H) & (abs(Y) < H)
np.savez('data/pts_crop.npz', x=X[m].astype(np.float32), y=Y[m].astype(np.float32), z=(np.asarray(las.z)[m]*FT).astype(np.float32),
         c=np.asarray(las.classification)[m], rn=np.asarray(las.return_number)[m], nr=np.asarray(las.number_of_returns)[m])
print('saved', m.sum())
