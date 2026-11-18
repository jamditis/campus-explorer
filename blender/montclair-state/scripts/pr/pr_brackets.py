# pr: downpipe stand-off brackets (pipe -> wall arms at each po strap) and splash blocks at the pipe feet
# (precast concrete 0.3 x 0.6 m at grade; 0.45 m square walkway pad on lower roofs). ALL UNVERIFIED (no photo).
# REVERT=1 removes the object.
import bpy, bmesh, os, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'; ON='PR_Feliciano_downpipe_brackets_splash_UNVERIFIED'
if ON in bpy.data.objects:
    o=bpy.data.objects[ON]; me=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(me); print('REVERTED_PR_BR')
if not REV:
    J=json.load(open('data/pq/gutters.json')); col=bpy.data.collections['PN_Feliciano_remass_20261101pn_UNVERIFIED']
    V=[];F=[]
    for o in bpy.data.objects:
        if o.type!='MESH' or o.hide_render or not o.visible_get(): continue
        if not (('Feliciano' in o.name and not o.name.startswith(('PO_','PN_Feliciano_eaves'))) or o.name.startswith(('PK_','Terrain'))): continue
        mw=o.matrix_world; b=len(V); V+=[mw@v.co for v in o.data.vertices]; F+=[[b+i for i in p.vertices] for p in o.data.polygons]
    T=BVHTree.FromPolygons(V,F); bm=bmesh.new()
    def box(c,ax,hx,hy,hz,mi):
        ay=Vector((-ax.y,ax.x,0)); vs=[bm.verts.new(c+ax*sx*hx+ay*sy*hy+Vector((0,0,sz*hz))) for sx in (-1,1) for sy in (-1,1) for sz in (-1,1)]
        for q in [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]: bm.faces.new([vs[i] for i in q]).material_index=mi
    nb=0; ns=0; nr=0
    for x,y,z,qx,qy in J['dp']:
        p=Vector((x,y,0)); q=Vector((qx,qy,0)); out=(p-q); out.z=0
        if out.length<1e-3: continue
        out.normalize()
        h=T.ray_cast(Vector((x,y,z-0.3)),Vector((0,0,-1)),60)
        if h[0] is None: continue
        zb=h[0].z
        if z-0.3-zb<0.6: continue
        # wall distance behind the pipe (horizontal ray toward the wall at mid height)
        for zz in [zb+1.5+i*2.5 for i in range(int((z-zb-2)/2.5))]:
            hw=T.ray_cast(Vector((x,y,zz+0.025)),-out,1.0)
            if hw[0] is None: continue
            L=(Vector((x,y,0))-Vector((hw[0].x,hw[0].y,0))).length
            if L<0.07: continue
            c=Vector((x,y,zz+0.025))-out*(L/2+0.02)
            box(c,out,L/2-0.02,0.012,0.02,0); box(Vector((hw[0].x,hw[0].y,zz+0.025))+out*0.004,out,0.004,0.035,0.04,0); nb+=1   # arm + wall plate
        g=Vector((x,y,zb))
        if zb<141.0:
            c=g+out*0.42; hh=T.ray_cast(c+Vector((0,0,1)),Vector((0,0,-1)),2.0); zc=hh[0].z if hh[0] is not None else zb
            box(Vector((c.x,c.y,zc+0.02)),out,0.3,0.15,0.035,1); ns+=1
        else:
            box(Vector((x,y,zb+0.012))+out*0.12,out,0.225,0.225,0.012,1); nr+=1
    me=bpy.data.meshes.new(ON); bm.to_mesh(me); bm.free()
    me.materials.append(bpy.data.materials['PE_Dickson_coping_dark_bronze_UNVERIFIED'])
    mc=bpy.data.materials.get('PR_precast_concrete_splash_UNVERIFIED')
    if mc is None:
        mc=bpy.data.materials.new('PR_precast_concrete_splash_UNVERIFIED'); mc.use_nodes=True
        b=mc.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=(0.42,0.41,0.38,1); b.inputs['Roughness'].default_value=0.85
    me.materials.append(mc)
    o=bpy.data.objects.new(ON,me); col.objects.link(o); print('PR_BR brackets',nb,'splash',ns,'roofpads',nr)
