# qg details (Nov 2 2026): CCIS lighter reflective glass (photo: pale blue-green) as a CCIS-only material copy, and red
# downpipes with straps + shoes at the ends of the long CCIS runs (photo shows red downpipes; positions UNVERIFIED).
import bpy, bmesh, os, math, json
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'
CN='Center for Computing and Information Science'; QFW='QF_CCIS_windows_red_frames_spandrels_brackets_photo'
GM='QG_CCIS_glass_pale_reflective_photo'; DP='QG_CCIS_red_downpipes_photo_positions_UNVERIFIED'
for o in [o for o in bpy.data.objects if o.get('qgd')]:
    me=o.data; bpy.data.objects.remove(o,do_unlink=True); bpy.data.meshes.remove(me)
w=bpy.data.objects.get(QFW)
if w:
    for s in w.material_slots:
        if s.material and s.material.name==GM: s.material=bpy.data.materials['PS_slot_glass_tinted_UNVERIFIED']
if GM in bpy.data.materials and bpy.data.materials[GM].users==0: bpy.data.materials.remove(bpy.data.materials[GM])
if REV: print('QG details reverted')
else:
    g=bpy.data.materials['PS_slot_glass_tinted_UNVERIFIED'].copy(); g.name=GM
    b=next(n for n in g.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    print('GLASS was',tuple(round(c,3) for c in b.inputs['Base Color'].default_value),b.inputs['Roughness'].default_value,b.inputs['Transmission Weight'].default_value)
    b.inputs['Base Color'].default_value=(0.20,0.27,0.27,1); b.inputs['Roughness'].default_value=0.04
    b.inputs['Transmission Weight'].default_value=0.0; b.inputs['IOR'].default_value=1.52; b.inputs['Metallic'].default_value=0.0
    b.inputs['Specular IOR Level'].default_value=0.75
    n=0
    for s in w.material_slots:
        if s.material and s.material.name=='PS_slot_glass_tinted_UNVERIFIED': s.material=g; n+=1
    print('GLASS slots',n,[s.link for s in w.material_slots])
    poly=[Vector((x,y)) for x,y in json.load(open('north/data/day_heroes/day7_geom.json'))['buildings'][CN]['poly_m']][:-1]
    NP=len(poly); area=sum(poly[i].x*poly[(i+1)%NP].y-poly[(i+1)%NP].x*poly[i].y for i in range(NP))/2
    W=bpy.data.objects[CN+' walls']; segs=[]
    for p in W.data.polygons:
        if abs(p.normal.z)>0.2: continue
        vs=[W.matrix_world@W.data.vertices[i].co for i in p.vertices]
        segs.append((Vector((sum(v.x for v in vs)/len(vs),sum(v.y for v in vs)/len(vs))),min(v.z for v in vs),max(v.z for v in vs)))
    sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
    red=bpy.data.materials['QF_CCIS_red_frame_photo']
    bm=bmesh.new()
    def cyl(c,z0,z1,r,seg=12):
        bmesh.ops.create_cone(bm,cap_ends=True,segments=seg,radius1=r,radius2=r,depth=z1-z0,matrix=__import__('mathutils').Matrix.Translation((c.x,c.y,(z0+z1)/2)))
    def boxp(c,hx,hy,hz,ax):
        ay=Vector((-ax.y,ax.x,0))
        vs=[bm.verts.new(c+ax*sx*hx+ay*sy*hy+Vector((0,0,sz*hz))) for sx in(-1,1) for sy in(-1,1) for sz in(-1,1)]
        for f in [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]: bm.faces.new([vs[k] for k in f])
    placed=[]
    for ei,fr in ((0,('s','e')),(8,('s','e')),(12,('s','e'))):
        a,bb=poly[ei],poly[(ei+1)%NP]; e=bb-a; t=e.normalized(); nn=Vector((t.y,-t.x)) if area>0 else Vector((-t.y,t.x))
        for f in fr:
            p2=a+t*0.42 if f=='s' else bb-t*0.42; near=[s for s in segs if (s[0]-p2).length<3.0]
            if not near: continue
            ztop=max(s[2] for s in near)-0.25
            c=p2+nn*0.42
            ok,loc,*_=sc.ray_cast(dg,Vector((c.x,c.y,ztop-0.5)),Vector((0,0,-1)))
            import numpy as np
            G=np.load('north/data/grid_1m.npz')['dtm_filled']; zl=float(G[int(math.floor(c.y+260)),int(math.floor(c.x+600))])
            zg=loc.z if (ok and abs(loc.z-zl)<1.5) else zl
            if ztop-zg<4: continue
            c3=Vector((c.x,c.y,0)); cyl(c3,zg+0.30,ztop,0.055)
            # shoe kicking out at the bottom
            boxp(Vector((c.x,c.y,0))+nn.to_3d()*0.10+Vector((0,0,zg+0.22)),0.07,0.07,0.08,nn.to_3d())
            for k in range(1,4):
                zs=zg+(ztop-zg)*k/4; boxp(Vector((c.x,c.y,zs))-nn.to_3d()*0.10,0.10,0.09,0.02,nn.to_3d())
            placed.append((ei,f,round(zg,2),round(ztop,2)))
    me=bpy.data.meshes.new(DP); bm.to_mesh(me); bm.free(); me.materials.append(red)
    for p in me.polygons: p.use_smooth=True
    o=bpy.data.objects.new(DP,me); o['qgd']=1; bpy.data.collections[CN].objects.link(o)
    print('DOWNPIPES',placed)
for o in [o for o in bpy.data.objects if o.get('qgc')]:
    d=o.data; bpy.data.objects.remove(o,do_unlink=True); bpy.data.cameras.remove(d)
if not REV:
    import numpy as np
    G=np.load('north/data/grid_1m.npz')['dtm_filled']
    gl=lambda x,y: float(G[int(math.floor(y+260)),int(math.floor(x+600))])
    for nm in ('QE_CAM_eye_ccis_east','QE_CAM_eye_ccis_west','QE_CAM_closeup_ccis_entrance'):
        c=bpy.data.objects.get(nm)
        if not c or c.parent: continue
        gz_=gl(c.location.x,c.location.y)
        if c.location.z<gz_+1.2:
            dz=gz_+1.7-c.location.z; c.location.z+=dz; c['qg_dz']=c.get('qg_dz',0)+dz; print('CAMFIX',nm,round(dz,2))
    a,bb=poly[0],poly[1]; e=bb-a; t=e.normalized(); nn=Vector((t.y,-t.x)) if area>0 else Vector((-t.y,t.x))
    tgt=a+t*0.42; tz=gl(tgt.x,tgt.y)
    cp=tgt+nn*6.5+t*3.0
    cd=bpy.data.cameras.new('QG_CAM_closeup_ccis_west_base_downpipe'); cd.lens=32
    cam=bpy.data.objects.new('QG_CAM_closeup_ccis_west_base_downpipe',cd); cam['qgc']=1
    cam.location=(cp.x,cp.y,gl(cp.x,cp.y)+1.6)
    d=Vector((tgt.x,tgt.y,tz+3.2))-cam.location; cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
    bpy.data.collections[CN].objects.link(cam); print('QGCAM',tuple(round(v,2) for v in cam.location))
