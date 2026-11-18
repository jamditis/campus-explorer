# po: box gutters on the outer eave edges + downpipes (gooseneck, pipe to the lower roof/grade by ray-cast, shoe) for the
# re-massed Feliciano tiers. Dark bronze like the fascia. ALL UNVERIFIED (no photo of Feliciano's rainwater goods). REVERT=1 removes.
import bpy, bmesh, os, sys, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'; ON='PO_Feliciano_gutters_downpipes_UNVERIFIED'
if ON in bpy.data.objects:
    o=bpy.data.objects[ON]; me=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(me); print('REVERTED_PO_GUT')
CAMN='PO_CAM_closeup_feliciano_gutter_downpipe'
if CAMN in bpy.data.objects:
    c=bpy.data.objects[CAMN]; cd=c.data; bpy.data.objects.remove(c); bpy.data.cameras.remove(cd)
if not REV:
    J=json.load(open('data/po/gutters.json')); col=bpy.data.collections['PN_Feliciano_remass_20261101pn_UNVERIFIED']
    V=[];F=[]
    occ=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and o.visible_get() and ('Feliciano' in o.name or o.name.startswith(('PN_','PK_','Terrain','PG_')))]
    for o in occ:
        if o.name.startswith('PN_Feliciano_eaves'): continue
        mw=o.matrix_world; b=len(V); V+=[mw@v.co for v in o.data.vertices]; F+=[[b+i for i in p.vertices] for p in o.data.polygons]
    T=BVHTree.FromPolygons(V,F)
    bm=bmesh.new()
    def seg(a,b,w,h,mi):   # box from a to b (horizontal axis), width w, height h, centred on the line, bottom at a.z
        d=Vector((b.x-a.x,b.y-a.y,0)); L=d.length
        if L<1e-3: return
        d/=L; n=Vector((-d.y,d.x,0))*w/2; vs=[]
        for p in (a,b):
            for s in (-1,1):
                for z in (0,h): vs.append(bm.verts.new(p+n*s+Vector((0,0,z))))
        for q in [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]: bm.faces.new([vs[i] for i in q]).material_index=mi
    def vbox(c,w,z0,z1,mi):
        vs=[bm.verts.new((c.x+sx*w/2,c.y+sy*w/2,z)) for sx in (-1,1) for sy in (-1,1) for z in (z0,z1)]
        for q in [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]: bm.faces.new([vs[i] for i in q]).material_index=mi
    for g in J['g']:
        a=Vector((g['a'][0],g['a'][1],g['z']-0.06)); b=Vector((g['b'][0],g['b'][1],g['z']-0.06))
        d=(b-a).normalized(); a-=d*0.02; b+=d*0.02
        # push 6 cm outward of the fascia: outward = away from the midpoint's inward side (probe both sides for the eave top)
        n=Vector((-d.y,d.x,0)); m=(a+b)/2
        hit=T.ray_cast(m+n*0.3+Vector((0,0,5)),Vector((0,0,-1)),5.3)
        if hit[0] is not None and hit[0].z>g['z']-0.4: n=-n     # n side is over the building -> flip
        seg(a+n*0.07,b+n*0.07,0.13,0.13,0)
    npipe=0; PIPES=[]
    for x,y,z,qx,qy in J['dp']:
        p=Vector((x,y,0)); q=Vector((qx,qy,0))
        h=T.ray_cast(Vector((x,y,z-0.3)),Vector((0,0,-1)),60)
        if h[0] is None: continue
        zb=h[0].z
        if z-0.3-zb<0.6: continue
        seg(Vector((q.x,q.y,z-0.2)),Vector((x,y,z-0.2)),0.09,0.09,0)      # gooseneck under the soffit
        vbox(p,0.1,zb+0.25,z-0.11,0)                                       # pipe
        for zz in [zb+1.5+i*2.5 for i in range(int((z-zb-2)/2.5))]: vbox(p,0.13,zz,zz+0.05,0)   # straps
        dd=(p-q).normalized()*0.25; seg(Vector((x,y,zb+0.03)),Vector((x,y,zb+0.03))+dd,0.12,0.25,0)  # shoe/splash kicker
        npipe+=1; PIPES.append((z-zb,p.copy(),q.copy(),z,zb))
    me=bpy.data.meshes.new(ON); bm.to_mesh(me); bm.free(); me.materials.append(bpy.data.materials['PE_Dickson_coping_dark_bronze_UNVERIFIED'])
    o=bpy.data.objects.new(ON,me); col.objects.link(o); print('PO_GUT gutters',len(J['g']),'pipes',npipe)
    import math
    for drop,p,q,z,zb in sorted(PIPES,key=lambda t:-t[0]):
        out=(q-p).normalized(); tgt=Vector((p.x,p.y,z-1.5)); cam=tgt+out*11+Vector((0,0,2.0))-Vector((-out.y,out.x,0))*5
        h=T.ray_cast(tgt+out*0.3,(cam-tgt).normalized(),(cam-tgt).length)
        if h[0] is None: break
    cd=bpy.data.cameras.new(CAMN); cd.lens=35; c=bpy.data.objects.new(CAMN,cd); col.objects.link(c); c.location=cam
    c.rotation_euler=(tgt-cam).to_track_quat('-Z','Y').to_euler(); print('PO_CAM',[round(v,1) for v in cam],'drop',round(drop,1))
