import bpy
F='/workspace/nj-scenes/montclair-state/montclair_state_ws218a.blend'
with bpy.data.libraries.load(F) as (a,b): b.objects=['Terrain_LiDAR_DTM_1m']
o=b.objects[0]; M=o.matrix_world
pts=[(-160,215),(-160,221),(-150,205),(-140,230),(-170,240),(-120,250),(-130,215)]
vs=[M@v.co for v in o.data.vertices]
for px,py in pts:
    near=[v.z for v in vs if abs(v.x-px)<0.8 and abs(v.y-py)<0.8]
    print('P218C',px,py,round(min(near),2) if near else None, round(max(near),2) if near else None, flush=True)
