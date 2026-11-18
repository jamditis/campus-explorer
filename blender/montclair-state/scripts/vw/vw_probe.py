# vw_probe: identify Bohn W-face meshes/faces in scene coords; why blank
import bpy, json, math, os
from mathutils import Vector
OUT='/workspace/nj-scenes/montclair-state/data/vw'
os.makedirs(OUT, exist_ok=True)
sc=bpy.context.scene
rows=[]
# collect all TK/TL Bohn Hall massing meshes
objs=[o for o in bpy.data.objects if o.type=='MESH' and (
    o.name.startswith('TK_Bohn_Hall') or o.name.startswith('TL_Bohn_Hall'))]
objs=sorted(objs, key=lambda o:o.name)
print('BOHN_MESHES', len(objs))
for o in objs:
    me=o.data; mw=o.matrix_world
    hide=(o.hide_render, o.hide_viewport, o.hide_get())
    n_faces=len(me.polygons)
    has={k: (k in me.attributes) for k in ('ti_dir','ti_floor','ti_z0','ti_z1')}
    # world bbox
    bb=[mw@Vector(c) for c in o.bound_box]
    xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    # wall faces: classify by world normal
    west=[]; east=[]; south=[]; north=[]; other_wall=[]; roof=[]; blank_w=[]
    z0g=None; z1vals=set()
    if 'ti_z0' in me.attributes:
        z0g=me.attributes['ti_z0'].data[0].value
    for pi,p in enumerate(me.polygons):
        n=(mw.to_3x3()@p.normal).normalized()
        c=mw@p.center
        z1=me.attributes['ti_z1'].data[pi].value if 'ti_z1' in me.attributes else None
        fl=me.attributes['ti_floor'].data[pi].value if 'ti_floor' in me.attributes else None
        d=None
        if 'ti_dir' in me.attributes:
            dv=me.attributes['ti_dir'].data[pi].vector; d=(round(dv.x,4),round(dv.y,4),round(dv.z,4))
        info=dict(pi=pi, cx=round(c.x,2), cy=round(c.y,2), cz=round(c.z,2),
                  nx=round(n.x,3), ny=round(n.y,3), nz=round(n.z,3),
                  area=round(p.area,2), z1=None if z1 is None else round(z1,3),
                  floor=fl, ti_dir=d, mat=p.material_index)
        if abs(n.z)>0.7:
            roof.append(info); continue
        # scene W ≈ -X (Montclair local: +X east-ish). Confirm via footprint.
        if n.x < -0.7:
            west.append(info)
            # blank if z1 ≈ z0g (shader blanks)
            if z0g is not None and z1 is not None and abs(z1-z0g)<0.5:
                blank_w.append(info)
        elif n.x > 0.7:
            east.append(info)
        elif n.y < -0.7:
            south.append(info)
        elif n.y > 0.7:
            north.append(info)
        else:
            # angled walls — classify by dominant
            if abs(n.x)>=abs(n.y):
                (west if n.x<0 else east).append(info)
                if n.x<0 and z0g is not None and z1 is not None and abs(z1-z0g)<0.5:
                    blank_w.append(info)
            else:
                (south if n.y<0 else north).append(info)
        if z1 is not None: z1vals.add(round(z1,2))
    row=dict(name=o.name, hide=hide, n_faces=n_faces, attrs=has,
             bbox=[round(min(xs),2),round(max(xs),2),round(min(ys),2),round(max(ys),2),round(min(zs),2),round(max(zs),2)],
             n_west=len(west), n_east=len(east), n_south=len(south), n_north=len(north),
             n_blank_west=len(blank_w), z0g=z0g, z1_unique=sorted(z1vals)[:12],
             west_faces=west[:40], blank_west=blank_w[:40],
             mats=[(i,m.name if m else None) for i,m in enumerate(me.materials)])
    rows.append(row)
    print(f"{o.name} hide={hide} faces={n_faces} W={len(west)} blankW={len(blank_w)} E={len(east)} S={len(south)} N={len(north)} bbox={row['bbox']}")
# also list cameras useful for Bohn
cams=[o.name for o in bpy.data.objects if o.type=='CAMERA' and ('Bohn' in o.name or 'east_dorm' in o.name.lower() or 'oblique_east' in o.name)]
print('CAMS', cams)
# materials
mats=[m.name for m in bpy.data.materials if 'Bohn' in m.name or 'eggcrate' in m.name.lower()]
print('MATS', mats)
# footprint westmost edge from base
base=bpy.data.objects.get('TK_Bohn_Hall_232853538_base_UNVERIFIED')
west_edge=None
if base:
    me=base.data; mw=base.matrix_world
    # collect wall face centers with nx<-0.5
    wes=[]
    for p in me.polygons:
        n=(mw.to_3x3()@p.normal).normalized(); c=mw@p.center
        if abs(n.z)<0.5 and n.x<-0.5:
            wes.append((c.x,c.y,c.z,n.x,n.y,p.area))
    wes=sorted(wes)
    print('BASE_WEST_FACES', len(wes), 'sample', wes[:8])
    west_edge=wes
out=dict(n_objs=len(bpy.data.objects), meshes=rows, cams=cams, mats=mats,
         base_west_faces=[{'x':a[0],'y':a[1],'z':a[2],'nx':a[3],'ny':a[4],'area':a[5]} for a in (west_edge or [])])
json.dump(out, open(OUT+'/probe.json','w'), indent=2)
print('WROTE', OUT+'/probe.json', 'objs', len(bpy.data.objects))
