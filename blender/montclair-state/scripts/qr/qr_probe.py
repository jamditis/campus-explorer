import bpy
from mathutils import Vector
for n in ('QP_Richardson_white_corner_towers_UNVERIFIED','QP_Richardson_roof_penthouse_units_UNVERIFIED'):
    o=bpy.data.objects[n]; me=o.data
    print('OBJ',n,me.name,me.users,len(me.polygons),[m.name for m in me.materials],[s.link for s in o.material_slots])
    zs=sorted(set(round(v.co.z,2) for v in me.vertices)); print(' Z',zs)
m=bpy.data.materials['QP_Richardson_white_precast_UNVERIFIED']; print('white users',m.users)
# grass/scatter near Richardson SW walk
c=Vector((74,242,0))
for o in bpy.data.objects:
    if o.hide_render: continue
    nm=o.name.lower()
    if any(k in nm for k in ('grass','clump','tuft','lawn','meadow','scatter')):
        w=[o.matrix_world@Vector(b) for b in o.bound_box]; lo=Vector((min(p.x for p in w),min(p.y for p in w))); hi=Vector((max(p.x for p in w),max(p.y for p in w)))
        if lo.x<110 and hi.x>40 and lo.y<300 and hi.y>220:
            mods=[(md.type,md.name,getattr(md,'node_group',None) and md.node_group.name) for md in o.modifiers]
            print('GR',o.name,o.type,[round(x) for x in (lo.x,lo.y,hi.x,hi.y)],mods,[s.material.name for s in o.material_slots if s.material], len(o.particle_systems) if hasattr(o,'particle_systems') else 0)
for cn in [o.name for o in bpy.data.objects if o.type=='CAMERA' and ('QP_' in o.name or 'QQ_' in o.name)]: 
    o=bpy.data.objects[cn]; print('CAM',cn,[round(x,1) for x in o.location],o.data.lens)
