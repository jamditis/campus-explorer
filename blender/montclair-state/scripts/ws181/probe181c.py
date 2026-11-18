import bpy, re
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
R=re.compile(r'tree|^T_|^TL|Lamp|light|pole|Bench|shrub|bleach|fence|sign|UTIL|hydrant|bollard',re.I)
with bpy.data.libraries.load(p) as (a,b):
    b.objects=[n for n in a.objects if R.search(n)]
print('LOADED',len(b.objects),flush=True)
for o in b.objects:
    if o is None: continue
    l=o.matrix_world.translation
    if -358<l.x<-312 and -241<l.y<-209: print('INLOT',o.name,o.type,'(%.1f,%.1f,%.2f)'%(l.x,l.y,l.z),flush=True)
