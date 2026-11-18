# ow: (A) CCIS LiDAR roof read as patchy red/white tile patches in the aerial: per-vertex roofc alpha/brightness from the ortho drape is noisy.
#     Removable GN modifier OW_ccis_roof_tile_ring overrides 'roofc' on the evaluated mesh only: pitched verts (vertex normal z < NZ) -> alpha 1 and
#     brightness lifted to >= BW (tile), flat verts -> alpha 0 (membrane). Mesh/material unedited. UNVERIFIED (tile ring + flat centre = campus convention; ortho warm tone).
# (B) OV gap-fill base-course boxes: ov took the outward side from the OSM wall polygon normal, which points inward on some segments, so those boxes stick
#     out 25 cm (the short dark box at the CELS jog inside corner). New collection OW_basefix_20261031ow rebuilds every OV gap-fill base box with the outside side
#     found by upward ray probes (roof of the same building above = inside), 6 cm proud / 25 cm deep, ends extended 8 cm to wrap under the neighbours
#     (top 5 mm lower, face 5.5 cm proud so no coplanar faces). OV originals hidden (props store prior state). REVERT=1 undoes all.
import bpy, bmesh, os, sys
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv
CC='Center for Computing and Information Science roof (LiDAR)'; MOD='OW_ccis_roof_tile_ring'; NG='OW_ccis_roof_tile_ring_GN'; COL='OW_basefix_20261031ow'
r=bpy.data.objects[CC]
# --- clean
if MOD in r.modifiers: r.modifiers.remove(r.modifiers[MOD])
if NG in bpy.data.node_groups: bpy.data.node_groups.remove(bpy.data.node_groups[NG])
if 'UNVERIFIED_ow_tile_ring' in r: del r['UNVERIFIED_ow_tile_ring']
c=bpy.data.collections.get(COL)
if c:
    for o in list(c.objects):
        me=o.data; bpy.data.objects.remove(o)
        if me and me.users==0: (bpy.data.meshes if isinstance(me,bpy.types.Mesh) else bpy.data.cameras).remove(me)
    bpy.data.collections.remove(c)
for o in bpy.data.objects:
    if 'ow_prev_hide' in o:
        hv,hr=o['ow_prev_hide']; o.hide_viewport=bool(hv); o.hide_render=bool(hr); del o['ow_prev_hide']
if REV:
    print('REVERTED_OW')
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit(0)
NZ=float(os.environ.get('NZ','0.985')); BW=float(os.environ.get('BW','0.34'))
# --- (A) GN
ng=bpy.data.node_groups.new(NG,'GeometryNodeTree')
ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
N=ng.nodes; L=ng.links.new
gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
na=N.new('GeometryNodeInputNamedAttribute'); na.data_type='FLOAT_COLOR'; na.inputs['Name'].default_value='roofc'
sep=N.new('FunctionNodeSeparateColor'); L(na.outputs['Attribute'],sep.inputs['Color'])
# bw = .3r+.59g+.11b
def m(op,a=None,b=None,va=0.0,vb=0.0):
    n=N.new('ShaderNodeMath'); n.operation=op; n.inputs[0].default_value=va; n.inputs[1].default_value=vb
    if a is not None: L(a,n.inputs[0])
    if b is not None: L(b,n.inputs[1])
    return n.outputs[0]
bw=m('ADD',m('ADD',m('MULTIPLY',sep.outputs['Red'],vb=0.3),m('MULTIPLY',sep.outputs['Green'],vb=0.59)),m('MULTIPLY',sep.outputs['Blue'],vb=0.11))
k=m('MAXIMUM',m('DIVIDE',vb=0.0,b=m('MAXIMUM',bw,vb=0.02),va=BW),vb=1.0)
k=m('MINIMUM',k,vb=4.0)
cmb=N.new('FunctionNodeCombineColor')
for ch in ('Red','Green','Blue'): L(m('MINIMUM',m('MULTIPLY',sep.outputs[ch],k),vb=0.95),cmb.inputs[ch])
cmb.inputs['Alpha'].default_value=1.0
cfl=N.new('FunctionNodeCombineColor')
for ch in ('Red','Green','Blue'): L(sep.outputs[ch],cfl.inputs[ch])
cfl.inputs['Alpha'].default_value=0.0
nrm=N.new('GeometryNodeInputNormal'); sxyz=N.new('ShaderNodeSeparateXYZ'); L(nrm.outputs['Normal'],sxyz.inputs[0])
cmp=N.new('FunctionNodeCompare'); cmp.data_type='FLOAT'; cmp.operation='LESS_THAN'; L(sxyz.outputs['Z'],cmp.inputs[0]); cmp.inputs[1].default_value=NZ
sw=N.new('GeometryNodeSwitch'); sw.input_type='RGBA'; L(cmp.outputs['Result'],sw.inputs['Switch']); L(cfl.outputs['Color'],sw.inputs['False']); L(cmb.outputs['Color'],sw.inputs['True'])
st=N.new('GeometryNodeStoreNamedAttribute'); st.data_type='FLOAT_COLOR'; st.domain='POINT'; st.inputs['Name'].default_value='roofc'
L(gi.outputs[0],st.inputs['Geometry']); L(sw.outputs['Output'],st.inputs['Value']); L(st.outputs['Geometry'],go.inputs[0])
md=r.modifiers.new(MOD,'NODES'); md.node_group=ng
r['UNVERIFIED_ow_tile_ring']='roofc override: pitched (vertex nz<%.3f) tile alpha1 bw>=%.2f, flat membrane alpha0'%(NZ,BW)
# --- (B) base course fix
col=bpy.data.collections.new(COL); bpy.context.scene.collection.children.link(col)
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
def inside(p,wn):
    ok,loc,nn,i,ob,mx=sc.ray_cast(dg,p,Vector((0,0,1)),distance=60.0)
    key=wn.split(' wa')[0][:15]; return ok and ob is not None and ob.name[:len(key)]==key and not ob.name.startswith(('OV_','OW_','OO_','OR_','OQ_','OS_','OT_'))
rep=[]
for o in [x for x in bpy.data.objects if x.name.startswith('OV_gapfill_base_') and x.type=='MESH']:
    wn=o.name[len('OV_gapfill_base_'):]; wm=o.matrix_world; vs=[wm@v.co for v in o.data.vertices]
    VB=[];FB=[]
    for j in range(0,len(vs),8):
        Ao,Ai,Bo,Bi=vs[j],vs[j+2],vs[j+4],vs[j+6]; zA=(vs[j].z+0.22); zB=(vs[j+4].z+0.22)  # ground at each end
        dA=(Ai-Ao); dA.z=0; d=dA.normalized(); wA=Ao+d*0.06; wB=Bo+d*0.06; wA.z=wB.z=0
        t=(wB-wA); t.z=0; Lseg=t.length; t.normalize()
        mid=(wA+wB)/2; zt=max(zA,zB)+1.2
        ins_p=inside(Vector((mid.x+d.x*0.8,mid.y+d.y*0.8,zt)),wn); ins_m=inside(Vector((mid.x-d.x*0.8,mid.y-d.y*0.8,zt)),wn)
        # ov's 'in' side is +d. outside = the side without the building above
        if ins_m and not ins_p: out=d; flip=True
        else: out=-d; flip=False
        rep.append((wn[:24],j//8,round(Lseg,2),'ins+',ins_p,'ins-',ins_m,'FLIP' if flip else 'keep'))
        o1=out*0.055; o2=-out*0.25; k0=len(VB)
        for (P,g,e) in ((wA,zA,-0.08),(wB,zB,0.08)):
            Q=P+t*e
            for off in (o1,o2):
                VB.append(Vector((Q.x+off.x,Q.y+off.y,g-0.22))); VB.append(Vector((Q.x+off.x,Q.y+off.y,g+0.415)))
        for q in ((0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5),(1,5,7,3),(0,2,6,4)): FB.append([k0+x for x in q])
    mb=bpy.data.meshes.new('OW_basefix_'+wn[:36]); mb.from_pydata(VB,[],FB); mb.update()
    bm=bmesh.new(); bm.from_mesh(mb); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(mb); bm.free()
    for mt in o.data.materials: mb.materials.append(mt)
    ob=bpy.data.objects.new('OW_basefix_'+wn[:36],mb); col.objects.link(ob); ob['UNVERIFIED']='ow rebuilt ov gap-fill base course (outside side by roof ray probe, ends wrapped 8 cm)'
    o['ow_prev_hide']=[int(o.hide_viewport),int(o.hide_render)]; o.hide_viewport=True; o.hide_render=True
for x in rep: print('BOX',x)
# close-up cam on the jog inside corner (lower, nearer than OV's)
cd=bpy.data.cameras.new('OW_CAM_closeup_CELS_jog_base_wrap'); cd.lens=32
cam=bpy.data.objects.new('OW_CAM_closeup_CELS_jog_base_wrap',cd); col.objects.link(cam)
tgt=Vector((127.3,196.2,129.7)); cam.location=Vector((131.8,193.4,131.2))
cam.rotation_euler=(tgt-cam.location).to_track_quat('-Z','Y').to_euler()
print('BUILT_OW',len(rep))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
