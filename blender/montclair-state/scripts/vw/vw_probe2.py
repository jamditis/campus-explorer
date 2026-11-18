import bpy, json
OUT='/workspace/nj-scenes/montclair-state/data/vw'
# material slots on visible Bohn
for o in sorted(bpy.data.objects, key=lambda o:o.name):
    if o.type!='MESH': continue
    if not (o.name.startswith('TL_Bohn') or o.name.startswith('TK_Bohn_Hall_232') or o.name.startswith('TP_Bohn_shaft')): continue
    if o.hide_render: continue
    mats=[(i, m.name if m else None) for i,m in enumerate(o.data.materials)]
    print(o.name, 'mats', mats, 'npoly', len(o.data.polygons))
# eggcrate / TM shader: find Math bay + glass mix
for mn in ('TK_Bohn_wall_eggcrate_UNVERIFIED','TM_Bohn_wall_v2_UNVERIFIED'):
    m=bpy.data.materials.get(mn)
    if not m: print('missing',mn); continue
    print('\nMAT', mn, 'users', m.users)
    for n in m.node_tree.nodes:
        if n.type=='MATH' and not n.inputs[0].is_linked:
            print(' ', n.name, n.operation, 'in0', n.inputs[0].default_value)
        if n.type=='MATH' and not n.inputs[1].is_linked and n.inputs[0].is_linked:
            print(' ', n.name, n.operation, 'in1', n.inputs[1].default_value)
# measure the tall W tower face carefully: L4 west face verts
o=bpy.data.objects['TL_Bohn_Hall_L4_0_rect_UNVERIFIED']
me=o.data; mw=o.matrix_world
from mathutils import Vector
import math
faces=[]
for pi,p in enumerate(me.polygons):
    n=(mw.to_3x3()@p.normal).normalized(); c=mw@p.center
    if abs(n.z)>0.5: continue
    if n.x>-0.7: continue
    z1=me.attributes['ti_z1'].data[pi].value
    z0=me.attributes['ti_z0'].data[pi].value
    # edge lengths of face
    verts=[mw@me.vertices[i].co for i in p.vertices]
    # along-wall extent: project onto ti_dir
    d=me.attributes['ti_dir'].data[pi].vector
    ts=[v.x*d.x+v.y*d.y for v in verts]
    zs=[v.z for v in verts]
    faces.append(dict(pi=pi,cx=c.x,cy=c.y,cz=c.z,nx=n.x,ny=n.y,area=p.area,
                      t0=min(ts),t1=max(ts),tw=max(ts)-min(ts),z0v=min(zs),z1v=max(zs),zh=max(zs)-min(zs),
                      blank=abs(z1-z0)<0.5, z1attr=z1))
faces=sorted(faces, key=lambda f:-f['area'])
print('\nL4 W faces:')
for f in faces: print({k:round(v,2) if isinstance(v,float) else v for k,v in f.items()})
# same for L2 largest W at 204 and 231
for on in ('TL_Bohn_Hall_L2_0_rect_UNVERIFIED','TL_Bohn_Hall_L3_0_rect_UNVERIFIED','TK_Bohn_Hall_232853538_base_UNVERIFIED'):
    o=bpy.data.objects[on]; me=o.data; mw=o.matrix_world
    faces=[]
    for pi,p in enumerate(me.polygons):
        n=(mw.to_3x3()@p.normal).normalized(); c=mw@p.center
        if abs(n.z)>0.5 or n.x>-0.7: continue
        d=me.attributes['ti_dir'].data[pi].vector
        verts=[mw@me.vertices[i].co for i in p.vertices]
        ts=[v.x*d.x+v.y*d.y for v in verts]; zs=[v.z for v in verts]
        z1=me.attributes['ti_z1'].data[pi].value; z0=me.attributes['ti_z0'].data[pi].value
        faces.append((p.area,c.x,c.y,max(ts)-min(ts),max(zs)-min(zs),abs(z1-z0)<0.5,z1))
    faces=sorted(faces, reverse=True)[:5]
    print('\n',on,'top W:')
    for f in faces: print(' ', [round(x,2) if isinstance(x,float) else x for x in f])
json.dump({'ok':1}, open(OUT+'/probe2_meta.json','w'))
