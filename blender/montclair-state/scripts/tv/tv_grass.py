# tv: fill bare lawn cells in front of Blanton's W entrances with TJ-style grass points. REVERT=1 deletes appended verts (count stored).
import bpy, os, random, json
from mathutils import Vector
SAVE=os.environ.get('SAVE')=='1'; REV=os.environ.get('REVERT')=='1'; DRY=os.environ.get('DRY')=='1'
O=bpy.data.objects['TJ_Webster_lawn_grass_points_UNVERIFIED']; me=O.data
X0,X1,Y0,Y1=float(os.environ.get('X0',74)),float(os.environ.get('X1',96)),float(os.environ.get('Y0',418)),float(os.environ.get('Y1',458))
import bmesh
if REV:
    n0=me.get('tv_n0')
    if n0 is not None:
        bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
        bmesh.ops.delete(bm,geom=[v for v in bm.verts[n0:]],context='VERTS'); bm.to_mesh(me); bm.free()
        del me['tv_n0']; print('REVERTED to',n0)
else:
    mw=O.matrix_world; mi=mw.inverted()
    pts=[mw@v.co for v in me.vertices]
    # density reference: open lawn cells with points
    cell={}
    for p in pts:
        if X0-30<p.x<X1+30 and Y0-30<p.y<Y1+30:
            k=(int(p.x//1),int(p.y//1)); cell[k]=cell.get(k,0)+1
    occ=[c for c in cell.values()]; occ.sort()
    dens=occ[len(occ)//2] if occ else 4
    print('ref cells',len(occ),'median per m2',dens)
    dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
    from mathutils.bvhtree import BVHTree
    trees=[]
    for ob in bpy.data.objects:
        if ob.type!='MESH' or ob.hide_render or ob is O: continue
        bb=[ob.matrix_world@Vector(c) for c in ob.bound_box]
        if max(b.x for b in bb)<X0-1 or min(b.x for b in bb)>X1+1 or max(b.y for b in bb)<Y0-1 or min(b.y for b in bb)>Y1+1: continue
        if 'grass' in ob.name.lower() or 'tree' in ob.name.lower() or 'farfield' in ob.name.lower() or ob.name=='Context_ground_beyond_data': continue
        ev=ob.evaluated_get(dg); m=ev.to_mesh()
        if len(m.polygons)==0 or len(m.polygons)>3000000: ev.to_mesh_clear(); continue
        vs=[ob.matrix_world@v.co for v in m.vertices]; fs=[tuple(pp.vertices) for pp in m.polygons]
        trees.append((ob.name,BVHTree.FromPolygons(vs,fs))); ev.to_mesh_clear()
    print('trees',[t[0] for t in trees])
    def cast(x,y):
        best=None
        for nm,t in trees:
            r=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))
            if r[0] is not None and (best is None or r[3]<best[3]): best=(r[0],r[1],nm,r[3])
        return best
    random.seed(5)
    new=[]; donors=[i for i,p in enumerate(pts) if X0-30<p.x<X1+30 and Y0-30<p.y<Y1+30]
    bad={}
    for ix in range(int(X0),int(X1)):
        for iy in range(int(Y0),int(Y1)):
            if cell.get((ix,iy),0)>=max(1,dens//3): continue
            for _ in range(dens):
                x=ix+random.random(); y=iy+random.random()
                r=cast(x,y)
                if r is None: continue
                p,nrm,nm,_=r
                if not ('Terrain' in nm or 'lawn' in nm.lower() or 'Ground' in nm or 'Context_skirt' in nm):
                    bad[nm]=bad.get(nm,0)+1; continue
                if nrm.z<0.8: continue
                new.append((p.copy(),random.choice(donors)))
    print('new',len(new),'blocked by',sorted(bad.items(),key=lambda t:-t[1])[:8])
    if not DRY and new:
        n0=len(me.vertices); me['tv_n0']=n0
        me.vertices.add(len(new))
        for j,(p,d) in enumerate(new):
            me.vertices[n0+j].co=mi@(p+Vector((0,0,0.0)))
        # copy point attributes from donors
        for a in me.attributes:
            if a.domain!='POINT' or a.name=='position' or a.name.startswith('.'): continue
            for j,(p,d) in enumerate(new):
                try: a.data[n0+j].value=a.data[d].value
                except Exception:
                    try: a.data[n0+j].vector=a.data[d].vector
                    except Exception: pass
        me.update(); print('added',len(new),'attrs',[a.name for a in me.attributes if a.domain=='POINT'])
if SAVE: bpy.ops.wm.save_mainfile()
