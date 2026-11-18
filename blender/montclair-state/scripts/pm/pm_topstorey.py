# pm (session pm, Nov 1 2026). ALL UNVERIFIED, removable; REVERT=1 deletes the collection.
# Feliciano: where the LiDAR roof rises >2 m above the OSM wall top just inside the wall line (the lumpy tile 'curtains'),
# the photo (feliciano_commons_08) shows a full-height stucco top storey under a LOW hip roof with a deep dark eave.
# Builds per 1.5 m wall segment: vertical stucco extension (wall top -> H), low-pitch tile eave strip (0.9 m overhang,
# ~16 deg, 3.4 m deep), dark fascia, inner riser. H = smoothed LiDAR roof height 6 m inside - 0.6 m. OSM/LiDAR untouched.
import bpy, os, sys, statistics
from mathutils import Vector
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv; OUT=os.environ.get('SAVEAS')
CN='PM_Feliciano_top_storey_low_hip_eave_20261101pm_UNVERIFIED'
if CN in bpy.data.collections:
    c=bpy.data.collections[CN]
    for o in list(c.objects):
        me=o.data; bpy.data.objects.remove(o)
        if me and me.users==0: bpy.data.meshes.remove(me)
    bpy.data.collections.remove(c)
if not REV:
    r=bpy.data.objects['Feliciano School of Business roof (LiDAR)']; w=bpy.data.objects['Feliciano School of Business walls']
    mw=r.matrix_world; bv=BVHTree.FromPolygons([mw@v.co for v in r.data.vertices],[p.vertices for p in r.data.polygons])
    def rz(p):
        h=bv.ray_cast(Vector((p.x,p.y,200)),Vector((0,0,-1))); return h[0].z if h[0] else None
    ww=w.matrix_world; V=[ww@v.co for v in w.data.vertices]
    cand=[]
    for p in w.data.polygons:
        vs=[V[i] for i in p.vertices]; zt=max(v.z for v in vs)
        top=[v for v in vs if abs(v.z-zt)<0.05]
        if len(top)!=2: continue
        a,b=top[0].copy(),top[1].copy(); d=b-a; d.z=0
        if d.length<0.5: continue
        n=Vector((-d.y,d.x,0)).normalized(); mid=(a+b)/2
        best=None
        for s in (1,-1):
            z25=rz(mid+n*s*2.5); z6=rz(mid+n*s*6)
            if z25 is None or z6 is None: continue
            if best is None or z25>best[1]: best=(s,z25,z6)
        if not best: continue
        s,z25,z6=best
        if z25<zt+2.0: continue
        cand.append(dict(a=a,b=b,zt=zt,inn=n*s,mid=mid,dir=d.normalized(),H0=max(z6,z25)-0.6))
    for c in cand:
        nb=[o['H0'] for o in cand if (o['mid']-c['mid']).xy.length<5.0 and abs(o['dir'].dot(c['dir']))>0.9]
        c['H']=statistics.median(nb)
    col=bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(col)
    st=bpy.data.materials['PG_Feliciano_wall_stucco_plain_no_shader_windows_UNVERIFIED']
    tl=bpy.data.materials['PI_Feliciano_roof_tile_forced_UNVERIFIED']; fw=bpy.data.materials['Eave_fascia_dark_wood']
    so=bpy.data.materials['Eave_tile_top_soffit_under']
    verts=[];faces=[];mats=[]
    def quad(p,m):
        i=len(verts); verts.extend(p); faces.append((i,i+1,i+2,i+3)); mats.append(m)
    OV=0.9; DEP=3.4; RISE=0.95
    for k,c in enumerate(cand):
        a,b,H,inn=c['a'],c['b'],c['H'],c['inn']; out=-inn; e=0.004*(k%3)
        ext=c['dir']*0.02
        a2=a-ext; b2=b+ext
        # wall extension (2 cm proud of the wall plane outward so it is not coplanar with the OSM wall below)
        o2=out*0.02
        quad([a2+o2+Vector((0,0,-0.05)), b2+o2+Vector((0,0,-0.05)), Vector((b2.x,b2.y,H))+o2, Vector((a2.x,a2.y,H))+o2],0)
        ao=Vector((a2.x,a2.y,H-0.25+e))+out*OV; bo=Vector((b2.x,b2.y,H-0.25+e))+out*OV
        ai=Vector((a2.x,a2.y,H-0.25+RISE+e))+inn*DEP; bi=Vector((b2.x,b2.y,H-0.25+RISE+e))+inn*DEP
        quad([ao,bo,bi,ai],1)                                  # tile top
        quad([ao+Vector((0,0,-0.32)),bo+Vector((0,0,-0.32)),bo,ao],2)   # fascia
        quad([Vector((a2.x,a2.y,H-0.57+e))+o2,Vector((b2.x,b2.y,H-0.57+e))+o2,bo+Vector((0,0,-0.32)),ao+Vector((0,0,-0.32))],3)  # soffit
        quad([ai,bi,bi+Vector((0,0,-1.4)),ai+Vector((0,0,-1.4))],1)  # inner riser
    me=bpy.data.meshes.new('PM_feliciano_top_storey_eave_UNVERIFIED'); me.from_pydata([tuple(v) for v in verts],[],faces)
    for m in (st,tl,fw,so): me.materials.append(m)
    for i,p in enumerate(me.polygons): p.material_index=mats[i]; p.use_smooth=False
    me.update()
    ob=bpy.data.objects.new('PM_Feliciano_top_storey_low_hip_eave_UNVERIFIED',me); col.objects.link(ob)
    ob['UNVERIFIED_pm']='top storey stucco + low hip tile eave per feliciano_commons_08; heights from LiDAR, eave depth/pitch guessed'
    print('PM_TOP segs',len(cand),'faces',len(faces),'H range',min(c['H'] for c in cand),max(c['H'] for c in cand),'gap range',min(c['H']-c['zt'] for c in cand),max(c['H']-c['zt'] for c in cand))
else: print('REVERTED_PM_TOP')
if OUT: bpy.ops.wm.save_as_mainfile(filepath=OUT,copy=True); print('SAVED_AS',OUT)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
