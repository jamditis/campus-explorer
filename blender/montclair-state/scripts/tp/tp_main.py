# tp (Nov 5 2026 ~12:40 AM ET, MAIN, day 8 Student Center east edge). ALL UNVERIFIED, reversible (REVERT=1).
# Bohn Hall blank service shafts / roof bulkheads where the 2017 B17 LiDAR DSM rises 2.5-3 m above the modelled TL level roofs
# (data/tp/bohn_excess.json from scripts/tp/tp_find.py), echoing the tall windowless shafts in the 1971 MSU slide (refs/bohn/).
# Shaft footprints = LiDAR excess cells -> rectangle aligned to the 70.5 deg axis, clipped to the level polygon + 0.12 m proud.
# Where a footprint reaches the level's outer wall the shaft runs down to grade (blank facade strip), else it is a roof bulkhead.
import bpy, bmesh, os, json, math
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'
CN='TP_Bohn_service_shafts_UNVERIFIED'
def revert():
    for o in [o for o in bpy.data.objects if 'tp_obj' in o]:
        me=o.data; t=o.type; bpy.data.objects.remove(o)
        if me and me.users==0:
            (bpy.data.meshes if t=='MESH' else bpy.data.cameras).remove(me)
    c=bpy.data.collections.get(CN)
    if c: bpy.data.collections.remove(c)
    for n in ('TP_Bohn_shaft_blank_UNVERIFIED','TP_Bohn_shaft_cap_UNVERIFIED'):
        m=bpy.data.materials.get(n)
        if m: bpy.data.materials.remove(m)
    print('TP reverted')
revert()
if REV:
    if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit
sc=bpy.context.scene
D='/workspace/nj-scenes/montclair-state/'
def mat(name,c0,c1,rough,scale,streak):
    m=bpy.data.materials.new(name); m.use_nodes=True; N=m.node_tree.nodes; L=m.node_tree.links; b=N['Principled BSDF']
    tc=N.new('ShaderNodeTexCoord'); nz=N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=scale; nz.inputs['Detail'].default_value=8
    L.new(tc.outputs['Object'],nz.inputs['Vector']); cr=N.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color=c0; cr.color_ramp.elements[1].color=c1
    L.new(nz.outputs['Fac'],cr.inputs[0]); last=cr.outputs['Color']
    if streak:
        mp=N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value=(1.8,1.8,0.07); L.new(tc.outputs['Object'],mp.inputs['Vector'])
        n2=N.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value=1.4; n2.inputs['Detail'].default_value=3; L.new(mp.outputs[0],n2.inputs['Vector'])
        r2=N.new('ShaderNodeMapRange'); r2.inputs['From Min'].default_value=0.45; r2.inputs['From Max'].default_value=0.75; r2.inputs['To Min'].default_value=1.0; r2.inputs['To Max'].default_value=0.86
        L.new(n2.outputs['Fac'],r2.inputs['Value'])
        mx=N.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.blend_type='MULTIPLY'; mx.inputs['Factor'].default_value=1.0
        cv=N.new('ShaderNodeCombineColor'); L.new(r2.outputs[0],cv.inputs[0]); L.new(r2.outputs[0],cv.inputs[1]); L.new(r2.outputs[0],cv.inputs[2])
        L.new(last,mx.inputs['A']); L.new(cv.outputs[0],mx.inputs['B']); last=mx.outputs['Result']
    L.new(last,b.inputs['Base Color']); b.inputs['Roughness'].default_value=rough; b.inputs['Specular IOR Level'].default_value=0.25
    bp=N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.12; L.new(nz.outputs['Fac'],bp.inputs['Height']); L.new(bp.outputs['Normal'],b.inputs['Normal'])
    return m
WM=mat('TP_Bohn_shaft_blank_UNVERIFIED',(0.36,0.33,0.28,1),(0.46,0.42,0.36,1),0.85,2.5,True)
CM=mat('TP_Bohn_shaft_cap_UNVERIFIED',(0.20,0.20,0.20,1),(0.28,0.28,0.27,1),0.7,8.0,False)
col=bpy.data.collections.new(CN); sc.collection.children.link(col); col['tp_obj']=1
SH=json.load(open(D+'data/tp/shafts.json'))
def prism(bm,pts,z0,z1):
    vb=[bm.verts.new((x,y,z0)) for x,y in pts]; vt=[bm.verts.new((x,y,z1)) for x,y in pts]
    bm.faces.new(vb[::-1]); bm.faces.new(vt); n=len(pts)
    for i in range(n): bm.faces.new((vb[i],vb[(i+1)%n],vt[(i+1)%n],vt[i]))
made=[]
for s_ in SH:
    k=s_['k']; lname=s_['level']; top=s_['top']; bot=s_['bot']
    bm=bmesh.new(); prism(bm,s_['fp'],bot,top-0.08)
    bmc=bmesh.new(); prism(bmc,s_['cap'],top-0.08,top)
    for nm,b_,m_ in (('TP_Bohn_shaft_%d_%s_UNVERIFIED'%(k,lname),bm,WM),('TP_Bohn_shaft_%d_%s_coping_UNVERIFIED'%(k,lname),bmc,CM)):
        me=bpy.data.meshes.new(nm); b_.to_mesh(me); b_.free(); me.materials.append(m_)
        o=bpy.data.objects.new(nm,me); o['tp_obj']=1; col.objects.link(o)
    made.append((k,lname,s_['area'],s_['edge'],bot,top))
print('TP shafts',made)
# camera: oblique of the east step-backs + shaft heads (also checks the tn window-column snap)
cd=bpy.data.cameras.new('TP_CAM_oblique_Bohn_stepbacks_from_E'); cd.lens=32
cam=bpy.data.objects.new('TP_CAM_oblique_Bohn_stepbacks_from_E',cd); cam['tp_obj']=1; col.objects.link(cam)
cam.location=Vector((float(os.environ.get('CX',300)),float(os.environ.get('CY',330)),float(os.environ.get('CZ',178))))
tgt=Vector((232,378,150)); cam.rotation_euler=(tgt-cam.location).to_track_quat('-Z','Y').to_euler()
cd2=bpy.data.cameras.new('TP_CAM_closeup_Bohn_W_shaft'); cd2.lens=35
cam2=bpy.data.objects.new('TP_CAM_closeup_Bohn_W_shaft',cd2); cam2['tp_obj']=1; col.objects.link(cam2)
cam2.location=Vector((float(os.environ.get('C2X',200)),float(os.environ.get('C2Y',322)),float(os.environ.get('C2Z',141))))
t2=Vector((224,354,151)); cam2.rotation_euler=(t2-cam2.location).to_track_quat('-Z','Y').to_euler()
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
