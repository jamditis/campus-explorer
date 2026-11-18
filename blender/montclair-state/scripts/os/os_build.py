# os (Oct 31 2026 ~8:35 PM ET): (A) darker, rougher base course + stronger grade dirt band on the OR skirt base course
# (new material OS_..., assigned at object level? no: mesh slot swap, original name stored in prop os_orig_mat);
# (B) soft splash/drip grime decals under the 103 OR skirt-window cast sills (reuses OM_Schmitt_sill_drip_grime material).
# ALL UNVERIFIED. REVERT=1 restores the OR material and removes os objects/material.
import bpy, bmesh, os, sys, math, ast
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv
ROOT='/workspace/nj-scenes/montclair-state'
CB='OR_skirt_base_course_20261031or'; CN='OS_skirt_sill_drips_20261031os'
OMAT='OR_skirt_base_course_grey_dirt_UNVERIFIED'; NMAT='OS_skirt_base_course_dark_dirt_UNVERIFIED'
def kill_col(n):
    c=bpy.data.collections.get(n)
    if not c: return
    for ob in list(c.objects):
        me=ob.data; bpy.data.objects.remove(ob)
        if me and me.users==0: bpy.data.meshes.remove(me)
    bpy.data.collections.remove(c)
kill_col(CN)
om=bpy.data.materials[OMAT]
for ob in bpy.data.collections[CB].objects:
    me=ob.data
    for i,m in enumerate(me.materials):
        if m and m.name==NMAT: me.materials[i]=om
m=bpy.data.materials.get(NMAT)
if m: bpy.data.materials.remove(m)
if REV:
    om.use_fake_user=False
    print('REVERTED')
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit(0)
# (A)
om.use_fake_user=True   # keep the OR material for REVERT (0 users after the swap)
nm=om.copy(); nm.name=NMAT; nt=nm.node_tree; bs=nt.nodes['Principled BSDF']
cr=[n for n in nt.nodes if n.type=='VALTORGB'][0]; els=sorted(cr.color_ramp.elements,key=lambda e:e.position)
els[0].position=0.45; els[0].color=(0.05,0.042,0.032,1)
els[1].position=0.66; els[1].color=(0.075,0.068,0.056,1)
els[2].position=0.92; els[2].color=(0.13,0.126,0.118,1)
bs.inputs['Roughness'].default_value=0.93
# splash speckle: darken the lower band with a fine noise mask, plus a small bump for a rough cast face
at_=[n for n in nt.nodes if n.type=='ATTRIBUTE'][0]
nz=nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=38; nz.inputs['Detail'].default_value=6; nz.inputs['Roughness'].default_value=0.7
mr=nt.nodes.new('ShaderNodeMapRange'); mr.inputs[1].default_value=0.0; mr.inputs[2].default_value=0.75; mr.inputs[3].default_value=1.0; mr.inputs[4].default_value=0.0; nt.links.new(at_.outputs['Fac'],mr.inputs[0])
sp=nt.nodes.new('ShaderNodeMath'); sp.operation='GREATER_THAN'; sp.inputs[1].default_value=0.62; nt.links.new(nz.outputs['Fac'],sp.inputs[0])
mk=nt.nodes.new('ShaderNodeMath'); mk.operation='MULTIPLY'; nt.links.new(sp.outputs[0],mk.inputs[0]); nt.links.new(mr.outputs[0],mk.inputs[1])
src=bs.inputs['Base Color'].links[0].from_socket
mx=nt.nodes.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.blend_type='MULTIPLY'; nt.links.new(mk.outputs[0],mx.inputs['Factor']); nt.links.new(src,mx.inputs[6]); mx.inputs[7].default_value=(0.55,0.5,0.42,1)
nt.links.new(mx.outputs[2],bs.inputs['Base Color'])
bp=nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.25; bp.inputs['Distance'].default_value=0.004
nz2=nt.nodes.new('ShaderNodeTexNoise'); nz2.inputs['Scale'].default_value=120; nz2.inputs['Detail'].default_value=4
nt.links.new(nz2.outputs['Fac'],bp.inputs['Height']); nt.links.new(bp.outputs['Normal'],bs.inputs['Normal'])
nb=0
for ob in bpy.data.collections[CB].objects:
    me=ob.data
    for i,m in enumerate(me.materials):
        if m and m.name==OMAT: me.materials[i]=nm; nb+=1
print('BASE_SWAPPED',nb)
# (B) drips under OR skirt sills
MD=bpy.data.materials['OM_Schmitt_sill_drip_grime_UNVERIFIED']
rows=[ast.literal_eval(l) for l in open(ROOT+'/data/or/skirt_windows_aligned.txt') if l.strip()]
W={'Center for C':2.2,'Speech Build':2.2,'Calcia Hall ':2.2}
for nmw in ['Center for Computing and Information Science walls','Center for Environmental and Life Sciences walls','Speech Building walls','Calcia Hall walls']:
    W[nmw[:12]]=min(2.2,float(bpy.data.objects[nmw].get('win_w',2.2)))
bm=bmesh.new(); uvs=[]; nd=0
for k,(nmw,H,x,y,sill,nx,ny) in enumerate(rows):
    n=Vector((nx,ny,0)); u=Vector((ny,-nx,0)); half=(W.get(nmw,2.2)/2+0.14)*0.95
    base=Vector((x,y,sill-0.08))+n*0.004
    dh=0.26+0.16*((k*37)%11)/10 if H>1.2 else 0.18+0.08*((k*29)%7)/6
    pts=[base-u*half,base+u*half,base+u*half*0.88-Vector((0,0,dh)),base-u*half*0.88-Vector((0,0,dh))]
    f=bm.faces.new([bm.verts.new(p) for p in pts]); uvs.append(((0,1),(1,1),(1,0),(0,0))); nd+=1
me=bpy.data.meshes.new('OS_skirt_sill_drip_grime'); bm.to_mesh(me)
ul=me.uv_layers.new(name='UVMap')
for pi,poly in enumerate(me.polygons):
    for j,li in enumerate(poly.loop_indices): ul.data[li].uv=uvs[pi][j]
me.materials.append(MD)
col=bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(col)
od=bpy.data.objects.new('OS_skirt_sill_drip_grime',me); col.objects.link(od); od.visible_shadow=False
od['UNVERIFIED']='os: typical sill drip grime under the or skirt windows, no photo'
print('DRIPS',nd)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
