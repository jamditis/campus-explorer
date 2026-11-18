# Session dT (Oct 21 2026): CCOM north-wing fixes (MAIN). Idempotent. SAVE=1 saves; REVERT=1 restores.
# A) "dark eave blob" seen from the north lawn = a 2-3 m gap between CCOM's ragged LiDAR-derived
#    upper wall tops (144.35-146.9) and the eave soffit/roof above (147.1-149.3). Wall-top vertices
#    (z>143.5) with the SCM eave soffit/roof directly above (<=4 m) are raised to the measured soffit
#    underside. Original z stored in the mesh attribute 'dT_orig_z' for REVERT.
# B) "plain grey panel" by the north-wing door = room-box side walls of corner windows poking out
#    through the adjacent facade. Instances whose room box crosses the SCM walls get a local variant
#    with a narrower/shallower room box (+-1.4 m wide, 2.0 m deep; opening/frame/glass unchanged).
import bpy, os
from mathutils import Vector
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
sc=bpy.context.scene
W=bpy.data.objects['School of Communication and Media walls']
me=W.data
att=me.attributes.get('dT_orig_z')
# ---- revert ----
if att is not None:
    for v,a in zip(me.vertices,att.data):
        if a.value>-1e8: v.co.z=a.value
    me.attributes.remove(att); me.update(); print('A reverted')
for o in bpy.data.objects:
    if o.get('dT_orig_coll'):
        o.instance_collection=bpy.data.collections[o['dT_orig_coll']]; del o['dT_orig_coll']
vc=bpy.data.collections.get('CCOM_Win_Wing_A_corner_dT')
if vc:
    for ob in list(vc.objects):
        if ob.library is None: bpy.data.objects.remove(ob)
    bpy.data.collections.remove(vc)
bpy.context.view_layer.update()
if REVERT:
    if SAVE: bpy.ops.wm.save_mainfile()
    print('REVERTED'); raise SystemExit
assert abs(W.matrix_world.determinant()-1)<1e-6 and W.matrix_world.translation.length<1e-6, 'walls not at identity'
# ---- A ----
dg=bpy.context.evaluated_depsgraph_get()
OK=('School of Communication and Media eave soffit','School of Communication and Media roof')
vn=[Vector() for _ in me.vertices]
for p in me.polygons:
    for i in p.vertices: vn[i]+=p.normal
att=me.attributes.new('dT_orig_z','FLOAT','POINT')
for a in att.data: a.value=-1e9
moved=[]
for v in me.vertices:
    if v.co.z<143.5: continue
    n=vn[v.index]; n.z=0
    if n.length<1e-6: continue
    n.normalize()
    o=v.co-n*0.12+Vector((0,0,0.03))
    h,p,_,_,ob,_=sc.ray_cast(dg,o,Vector((0,0,1)),distance=4.0)
    if not h or not ob.name.startswith(OK): continue
    dz=p.z-v.co.z
    if dz<0.05: continue
    att.data[v.index].value=v.co.z; v.co.z=p.z-0.01; moved.append((round(v.co.x,2),round(v.co.y,2),round(dz,2),ob.name[:40]))
me.update()
print('A raised',len(moved),'wall-top verts; max dz',max([m[2] for m in moved]) if moved else 0)
for m in moved: print('  RAISE',m)
# ---- B ----
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
src=bpy.data.collections['CCOM_Win_Wing_A']
def crosses_wall(a,b):
    d=b-a; L=d.length; d.normalize(); o=a.copy(); t=0
    for _ in range(12):
        h,p,_,_,ob,_=sc.ray_cast(dg,o,d,distance=L-t)
        if not h: return False
        if ob.name=='School of Communication and Media walls': return True
        t+=(p-o).length+1e-3; o=p+d*1e-3
    return False
def protrudes(inst,hw,dep):
    M=inst.matrix_world
    for z in (-0.5,2.9):
        a=M@Vector((0,-0.5,z))
        for sx in (-hw,hw):
            for y in (-0.3,-dep):
                if crosses_wall(a,M@Vector((sx,y,z))): return True
    return False
cands=[o for o in bpy.data.objects if o.instance_type=='COLLECTION' and o.instance_collection==src and not o.hide_render]
bad=[o for o in cands if protrudes(o,2.1,3.0)]
print('B checked',len(cands),'instances; protruding:',[o.name for o in bad])
if bad:
    vc=bpy.data.collections.new('CCOM_Win_Wing_A_corner_dT')
    hold=bpy.data.collections.get('CCOM_windows_modelled'); 
    for ob in src.all_objects:
        base=ob.name.replace('CCOM_Win_Wing_A_','')
        if base in ('floor','ceil','wall','back','light'):
            m=ob.data.copy(); m.name='CCOM_Win_Wing_A_corner_dT_'+base
            for v in m.vertices:
                c=ob.matrix_world@v.co
                v.co=Vector((c.x*1.4/2.1, -0.3+(c.y+0.3)*(1.7/2.7), c.z))
            n=bpy.data.objects.new('CCOM_Win_Wing_A_corner_dT_'+base,m)
            n.hide_render=ob.hide_render; n.visible_camera=ob.visible_camera
            for a in ('visible_shadow','visible_glossy','visible_transmission','visible_diffuse','visible_volume_scatter'):
                setattr(n,a,getattr(ob,a))
            vc.objects.link(n)
        else:
            vc.objects.link(ob)
    for o in bad:
        o['dT_orig_coll']=src.name; o.instance_collection=vc
    bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
    still=[o.name for o in bad if protrudes(o,1.4,2.0)]
    print('B variant applied to',len(bad),'; still protruding after narrowing:',still)
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
