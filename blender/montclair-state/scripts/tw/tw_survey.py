"""Survey Cole/College Hall / cupola objects in MAIN."""
import bpy, os
out=[]
keys=('cole','college','cupola','bell','bq','br','bu','susan')
for o in sorted(bpy.data.objects, key=lambda x:x.name):
    n=o.name.lower()
    if any(k in n for k in keys):
        cols=[c.name for c in o.users_collection]
        mats=[s.material.name if s.material else '' for s in o.material_slots]
        bb=[o.matrix_world@__import__('mathutils').Vector(c) for c in o.bound_box] if o.type=='MESH' else []
        if bb:
            lo=(min(p.x for p in bb),min(p.y for p in bb),min(p.z for p in bb))
            hi=(max(p.x for p in bb),max(p.y for p in bb),max(p.z for p in bb))
        else:
            lo=hi=None
        out.append(f"OBJ {o.name!r} type={o.type} hide={o.hide_get()}/{o.hide_render} cols={cols} mats={mats[:6]} bbox={lo}->{hi} loc={tuple(round(x,3) for x in o.location)}")
for c in sorted(bpy.data.collections, key=lambda x:x.name):
    if any(k in c.name.lower() for k in keys):
        out.append(f"COL {c.name!r} nobj={len(c.objects)} kids={[k.name for k in c.children]}")
for m in sorted(bpy.data.materials, key=lambda x:x.name):
    if any(k in m.name.lower() for k in ('cole','college','cupola','bq','oxblood','verdigris','wall_stucco_mission')):
        out.append(f"MAT {m.name!r}")
# cameras near Cole
for o in bpy.data.objects:
    if o.type!='CAMERA': continue
    if 'cole' in o.name.lower() or 'college' in o.name.lower():
        out.append(f"CAM {o.name} loc={tuple(round(x,2) for x in o.matrix_world.translation)}")
print('NOBJ',len(bpy.data.objects))
path='/workspace/nj-scenes/montclair-state/data/tw/survey.txt'
open(path,'w').write('\n'.join(out)+'\n')
print('WROTE',path,'lines',len(out))
for line in out[:80]: print(line)
