# ws254d: acorn lamp bases re-seated on the evaluated walk/ground (lamp254.out): Lamp_acorn_031 sat 0.36 m into the ws250-raised lawn
# (walk 138.81), Lamp_acorn_030 0.09 m under its walk (138.17), the ws252 plaza lamp 0.05 m under the ground -> base = surface - 0.02.
import bpy
for n,zt in (('Lamp_acorn_031',138.79),('Lamp_acorn_030',138.15),('WS252_W63c_Lamp_acorn_ortho2020_UNVERIFIED',136.24)):
    o=bpy.data.objects.get(n)
    if not o: print('F254D missing',n,flush=True); continue
    d=zt-o.matrix_world.translation.z; o.location.z+=d; print('F254D',n,'dz %+.3f'%d,flush=True)
