# Why does W read blank while S shows eggcrate? Sample face attrs + shader inputs.
import bpy, json, math
from mathutils import Vector
o=bpy.data.objects['TL_Bohn_Hall_L4_0_rect_UNVERIFIED']
me=o.data; mw=o.matrix_world
AX=math.radians(70.5)
# classify faces
def clas(n):
    if abs(n.z)>0.7: return 'roof'
    # project onto building axes
    # S-ish: normal ~ (-sin?); building long axis (cos70.5,sin70.5); S normal points roughly -perp = (sin, -cos)? 
    # From data W normal ≈ (-0.94, 0.33)
    if n.x<-0.5 and abs(n.x)>=abs(n.y): return 'W'
    if n.x>0.5 and abs(n.x)>=abs(n.y): return 'E'
    if n.y<-0.5: return 'S'
    if n.y>0.5: return 'N'
    return 'other'
rows={'W':[],'E':[],'S':[],'N':[],'other':[],'roof':[]}
for pi,p in enumerate(me.polygons):
    n=(mw.to_3x3()@p.normal).normalized(); c=mw@p.center
    k=clas(n)
    z0=me.attributes['ti_z0'].data[pi].value
    z1=me.attributes['ti_z1'].data[pi].value
    d=me.attributes['ti_dir'].data[pi].vector
    fl=me.attributes['ti_floor'].data[pi].value
    blank=abs(z1-z0)<1.0
    # simulate shader at face center
    bay=2.2
    fu=math.fmod(c.dot(d)/bay, 1.0); 
    if fu<0: fu+=1
    zr=c.z-z0
    fz=math.fmod((zr-0.95)/fl, 1.0); 
    if fz<0: fz+=1
    inb = (zr>0.95) and (c.z < z1-0.9) and (abs(n.z)<0.5)
    win = inb and (0.10<fu<0.90) and (0.02<fz<0.63)
    rows[k].append(dict(pi=pi,area=round(p.area,1),c=[round(c.x,1),round(c.y,1),round(c.z,1)],
                        n=[round(n.x,2),round(n.y,2),round(n.z,2)],
                        dir=[round(d.x,3),round(d.y,3)], z0=round(z0,2),z1=round(z1,2),
                        blank=blank,fu=round(fu,3),fz=round(fz,3),inb=inb,win=win,fl=fl))
for k,v in rows.items():
    if not v: continue
    print(f'\n=== L4 {k} n={len(v)} blank={sum(1 for x in v if x["blank"])} win_at_center={sum(1 for x in v if x["win"])}')
    for x in sorted(v,key=lambda x:-x['area'])[:6]:
        print(x)

# Also: which face does the oblique cam see on the left of tall block?
cam=bpy.data.objects.get('TI_CAM_oblique_east_dorms_from_SW')
print('\nCAM', cam.location if cam else None)
# ray from cam toward approx tall W face center
if cam:
    target=Vector((204.7,384.4,162))
    origin=cam.matrix_world.translation
    direction=(target-origin).normalized()
    # ray cast all Bohn TL
    dg=bpy.context.evaluated_depsgraph_get()
    hit_any=None
    for name in sorted(bpy.data.objects.keys()):
        ob=bpy.data.objects[name]
        if ob.type!='MESH' or not (name.startswith('TL_Bohn') or name.startswith('TK_Bohn_Hall_232') or name.startswith('TP_Bohn_shaft')): continue
        if ob.hide_render: continue
        e=ob.evaluated_get(dg); iw=ob.matrix_world.inverted()
        r=e.ray_cast(iw@origin, (iw.to_3x3()@direction).normalized())
        if r[0]:
            hit=ob.matrix_world@r[1]; hn=(ob.matrix_world.to_3x3()@r[2]).normalized()
            dist=(hit-origin).length
            if hit_any is None or dist<hit_any[0]:
                hit_any=(dist, name, [round(x,2) for x in hit], [round(x,3) for x in hn])
    print('RAY_HIT', hit_any)

# Check S face widths on L4
print('\nL4 S-ish faces (ny<-0.5):')
for x in rows['S']:
    print(x)
# And faces with ny dominant negative even if classified other
print('\nAll non-roof by ny:')
for k,v in rows.items():
    if k=='roof': continue
    for x in v:
        if x['n'][1]<-0.5:
            print(k,x)
