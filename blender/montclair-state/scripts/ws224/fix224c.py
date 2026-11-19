# ws224c: 1.6-3.4 cm sideways step in the College Ave curb face where the WS220 return ends (ring k29) and WS27
# curb_left starts (ring 0): k29 sits north of curb_left ring 0 (front y -53.032 vs -53.048), so the faces don't line up
# (vertical seam + step in the close-up). Horizontal-only move (no z change): WS220 ring k29 shifted by the front-vertex
# delta to curb_left ring 0, ring k28 by half of it, so the faces meet flush. Landing/road untouched.
import bpy
from mathutils import Vector
A=bpy.data.objects['WS220_CollegeAve_curb_jog_return_UNVERIFIED']; B=bpy.data.objects['WS27_CollegeAve_curb_left_UNVERIFIED']
MA=A.matrix_world; MAI=MA.inverted(); MB=B.matrix_world
d=(MB@B.data.vertices[6*0+1].co)-(MA@A.data.vertices[5*29+1].co); d.z=0
print('F224C delta %.3f %.3f'%(d.x,d.y),flush=True)
assert d.length<0.05
for k,s in ((29,1.0),(28,0.5)):
    for j in range(5):
        v=A.data.vertices[5*k+j]; w=MA@v.co; w+=d*s; v.co=MAI@w
A.data.update()
print('F224C k29 front now',tuple(round(c,3) for c in MA@A.data.vertices[5*29+1].co),flush=True)
