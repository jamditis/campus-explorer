"""ws18: subtle rain/drip stains below the 4 east glazed-bay sills of Cole's north addition (UNVERIFIED weathering)."""
import bpy, bmesh, os
from mathutils import Vector
o=bpy.data.objects['TZ_Cole_north_addition_UNVERIFIED']; me=o.data; M=o.matrix_world
bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
slots=[s.material.name for s in o.material_slots]; SILL=slots.index('TZ_Cole_sill_drip_UNVERIFIED')
# sills = SILL faces facing up, near z 135.0
tops=[f for f in bm.faces if f.material_index==SILL and f.normal.z>0.9 and 134.9<f.calc_center_median().z<135.1]
print('sill tops',len(tops))
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
V=[];F=[];UV=[]
for f in tops:
    vs=[v.co for v in f.verts]
    # sill outward dir = Fn from glaze: estimate from the face's long axis
    e=max(f.edges,key=lambda e:e.calc_length()); a,b=e.verts[0].co.copy(),e.verts[1].co.copy()
    W=(b-a); W.z=0; W.normalize(); Fn=Vector((W.y,-W.x,0))
    c=f.calc_center_median()
    # pick the outward side: the face edge farthest along +/-Fn from wall... use the long edge closest to the outer side
    ds=[(v-c).dot(Fn) for v in vs]
    outer=max(ds); inner=min(ds)
    # wall plane is REV(0.22) behind the sill front; sill front = 0.06 proud of wall
    if abs(outer)<abs(inner): Fn=-Fn; outer,inner=-inner,-outer
    wallpt=c+Fn*(outer-0.06)
    us=[(v-c).dot(W) for v in vs]; u0,u1=min(us)+0.02,max(us)-0.02
    zt=c.z-0.08
    wpt=M@Vector((wallpt.x,wallpt.y,zt))
    h=sc.ray_cast(dg,wpt+(M.to_3x3()@Fn).normalized()*0.06,Vector((0,0,-1)))
    g=h[1].z if h[0] else zt-1
    zb=max(zt-0.55,g+0.03)
    print('bay',round(u1-u0,2),'zt',round(zt,2),'ground',round(g,2),'zb',round(zb,2))
    base=len(V)
    for uu,zz,uv in [(u0,zb,(0,0)),(u1,zb,(1,0)),(u1,zt,(1,1)),(u0,zt,(0,1))]:
        p=wallpt+W*uu+Fn*0.004; V.append(Vector((p.x,p.y,zz))); UV.append(uv)
    F.append([base,base+1,base+2,base+3])
bm.free()
m2=bpy.data.meshes.new('WS18_Cole_add_east_sill_drip_stains_UNVERIFIED'); m2.from_pydata([tuple(v) for v in V],[],F); m2.update()
uvl=m2.uv_layers.new(name='UVMap')
for p in m2.polygons:
    for li,vi in zip(p.loop_indices,p.vertices): uvl.data[li].uv=UV[vi]
# material: dark grey-brown, alpha = vertical streak noise * fade down from sill
mat=bpy.data.materials.get('WS18_sill_drip_stain_UNVERIFIED') or bpy.data.materials.new('WS18_sill_drip_stain_UNVERIFIED')
mat.use_nodes=True; nt=mat.node_tree; nt.nodes.clear()
out=nt.nodes.new('ShaderNodeOutputMaterial'); bsdf=nt.nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Base Color'].default_value=(0.20,0.18,0.15,1); bsdf.inputs['Roughness'].default_value=0.9
tc=nt.nodes.new('ShaderNodeTexCoord'); sep=nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['UV'],sep.inputs[0])
mp=nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value=(60,1.2,1); nt.links.new(tc.outputs['UV'],mp.inputs['Vector'])
nz=nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=1.0; nz.inputs['Detail'].default_value=4; nt.links.new(mp.outputs[0],nz.inputs['Vector'])
cr=nt.nodes.new('ShaderNodeMapRange'); cr.inputs['From Min'].default_value=0.45; cr.inputs['From Max'].default_value=0.75; nt.links.new(nz.outputs['Fac'],cr.inputs['Value'])
# fade: v^1.6 (strong just under the sill)
pw=nt.nodes.new('ShaderNodeMath'); pw.operation='POWER'; pw.inputs[1].default_value=1.8; nt.links.new(sep.outputs['Y'],pw.inputs[0])
mul=nt.nodes.new('ShaderNodeMath'); mul.operation='MULTIPLY'; nt.links.new(cr.outputs[0],mul.inputs[0]); nt.links.new(pw.outputs[0],mul.inputs[1])
mx=nt.nodes.new('ShaderNodeMath'); mx.operation='MULTIPLY'; mx.inputs[1].default_value=0.38; nt.links.new(mul.outputs[0],mx.inputs[0])
nt.links.new(mx.outputs[0],bsdf.inputs['Alpha']); nt.links.new(bsdf.outputs[0],out.inputs[0])
m2.materials.append(mat)
ob=bpy.data.objects.new('WS18_Cole_add_east_sill_drip_stains_UNVERIFIED',m2); ob.matrix_world=M.copy()
for c in o.users_collection: c.objects.link(ob)
ob.visible_shadow=False
print('BUILT',len(F))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
