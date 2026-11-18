# Session eg (Oct 21 2026 ~8:40 PM ET): ef self-review said the tower-bed shrubs' white flowers read as tiny dots, while the
# Commons photo (School of Communications.jpg, 2021, CC BY-SA 4.0) shows larger white flower heads on top of the rounded shrubs.
# Adds collection CCOM_tower_bed_flowers_20261021eg: linked copies of one generated white flower-head cluster mesh
# (7-11 small lumpy spheres, ~16-24 cm across), seated by ray-casting the evaluated scene onto the 9 ef Shrub_Azalea instances
# (hits must belong to those instances). Species UNVERIFIED. SAVE=1 saves; REVERT=1 removes (idempotent).
import bpy, bmesh, os, random, math
from mathutils import Vector, noise
C='CCOM_tower_bed_flowers_20261021eg'
if C in bpy.data.collections:
    col=bpy.data.collections[C]
    for o in list(col.objects): bpy.data.objects.remove(o)
    bpy.data.collections.remove(col)
for m in [m for m in bpy.data.meshes if m.name.startswith('eg flowerhead') and m.users==0]: bpy.data.meshes.remove(m)
if os.environ.get('REVERT')!='1':
    random.seed(20261021)
    col=bpy.data.collections.new(C); bpy.context.scene.collection.children.link(col)
    mat=bpy.data.materials.get('eg_flowerhead_white') or bpy.data.materials.new('eg_flowerhead_white')
    mat.use_nodes=True; b=mat.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(0.86,0.86,0.80,1); b.inputs['Roughness'].default_value=0.75
    b.inputs['Subsurface Weight'].default_value=0.15
    meshes=[]
    for v in range(3):
        bm=bmesh.new()
        for i in range(7+2*v):
            r=random.uniform(0.035,0.055); c=Vector((random.gauss(0,0.05),random.gauss(0,0.05),random.uniform(0,0.06)))
            ret=bmesh.ops.create_icosphere(bm,subdivisions=2,radius=r)
            for vv in ret['verts']:
                d=vv.co.normalized(); vv.co=c+vv.co*(1+0.35*noise.noise(vv.co*60+c*10))
        me=bpy.data.meshes.new(f'eg flowerhead {v}'); bm.to_mesh(me); bm.free(); me.materials.append(mat)
        for p in me.polygons: p.use_smooth=True
        meshes.append(me)
    dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
    shr=[o for o in bpy.data.objects if o.name.startswith('ef tower bed shrub')]
    n=0
    for k,e in enumerate(shr):
        # footprint from evaluated instance bbox
        pts=[]
        for inst in dg.object_instances:
            if inst.is_instance and inst.parent and inst.parent.original==e:
                mw=inst.matrix_world; pts+= [mw@Vector(c) for c in inst.object.bound_box]
        if not pts: continue
        x0=min(p.x for p in pts); x1=max(p.x for p in pts); y0=min(p.y for p in pts); y1=max(p.y for p in pts); z1=max(p.z for p in pts)
        cx,cy=(x0+x1)/2,(y0+y1)/2; rx,ry=(x1-x0)/2*0.75,(y1-y0)/2*0.75
        want=random.randint(4,7); tries=0; got=0
        while got<want and tries<60:
            tries+=1; a=random.uniform(0,2*math.pi); rr=math.sqrt(random.uniform(0,1))
            q=Vector((cx+rx*rr*math.cos(a),cy+ry*rr*math.sin(a),z1+2))
            hit,loc,nor,idx,ob,mx=sc.ray_cast(dg,q,Vector((0,0,-1)))
            if not hit or loc.z<z1-0.6: continue
            # accept only shrub geometry (not mulch/grass/buildings)
            if not (ob and ('Azalea' in ob.name or 'Shrub' in ob.name or 'leaf' in ob.name.lower())): continue
            o=bpy.data.objects.new(f'eg tower bed flowerhead {n:03d} (photo; species UNVERIFIED)',meshes[n%3])
            s=random.uniform(0.85,1.25); o.scale=(s,s,s*0.8); o.rotation_euler=(random.uniform(-.3,.3),random.uniform(-.3,.3),random.uniform(0,6.3))
            o.location=loc+Vector((0,0,-0.03)); col.objects.link(o); n+=1; got+=1
    print('EG_FLOWERS shrubs',len(shr),'heads',n)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('EG_FL_SAVED')
