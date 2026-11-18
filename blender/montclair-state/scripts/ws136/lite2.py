import bpy
from mathutils import Vector
allr=open('/workspace/nj-scenes/montclair-state/scripts/ws136/names.txt').read().split('\n')
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend') as (df,dt):
    dt.meshes=list(df.meshes)
print(len(dt.meshes))
b=(-82,-66,-242,-208)
for me in dt.meshes:
    if me is None or len(me.polygons)>300000: continue
    n=0; zs=[]
    for v in me.vertices:
        if b[0]<=v.co.x<=b[1] and b[2]<=v.co.y<=b[3]: n+=1; zs.append(v.co.z)
    if n: print(me.name,len(me.polygons),n,round(min(zs),2),round(max(zs),2))
