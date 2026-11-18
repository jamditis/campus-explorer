# Session iq (2026-10-25): patch on top of ip (run AFTER scripts/ip/ip_amphi_build.py; re-run if ip is rebuilt).
# (1) Green seam fix: terrain triangle edges between lowered DTM verts poked up through the bowl at row transitions
#     (177 faces had a centroid/edge midpoint above the bowl surface). Every DTM vert under the bowl now drops to the
#     bowl's MINIMUM height within +-1.0 m minus 0.15 m, which keeps whole edges below. Originals in terr['iq_terrain_orig'].
# (2) Per-block tone variation on seat/aisle stone (one random value per bench block, +-~9%), so the seat tops stop reading
#     as one flat sheet from the top row. (3) Dirt/lichen in the riser joints and seat/riser contact (AO-masked, patchy noise).
# Env: SAVE=1; REVERT=1 restores the terrain verts (materials are rebuilt by the ip script).
import bpy, numpy as np, json, os
terr=bpy.data.objects['Terrain_LiDAR_DTM_1m']
if 'iq_terrain_orig' in terr:
    for i,z in json.loads(terr['iq_terrain_orig']).items(): terr.data.vertices[int(i)].co.z=z
    del terr['iq_terrain_orig']
if os.environ.get('REVERT')=='1':
    terr.data.update()
    if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile()
    print('IQ REVERTED'); raise SystemExit
bowl=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=bowl.data
co=np.empty(len(me.vertices)*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3); A=np.array(bowl.matrix_world); bw=co@A[:3,:3].T+A[:3,3]
# bowl top surface only: skip skirt verts (0.7 m drop) by taking per-cell max height, then local min of that
C=0.25; x0,y0=bw[:,0].min()-2,bw[:,1].min()-2; nx=int((bw[:,0].max()+2-x0)/C)+1; ny=int((bw[:,1].max()+2-y0)/C)+1
Hm=np.full((ny,nx),-np.inf); ix=((bw[:,0]-x0)/C).astype(int); iy=((bw[:,1]-y0)/C).astype(int)
np.maximum.at(Hm,(iy,ix),bw[:,2]); has=np.isfinite(Hm); Hc=np.where(has,Hm,np.inf)
r=4; Hp=np.pad(Hc,r,constant_values=np.inf); L=np.full_like(Hc,np.inf)
for dy in range(-r,r+1):
    for dx in range(-r,r+1): L=np.minimum(L,Hp[r+dy:r+dy+ny,r+dx:r+dx+nx])
tc=np.empty(len(terr.data.vertices)*3); terr.data.vertices.foreach_get('co',tc); tc=tc.reshape(-1,3); T=np.array(terr.matrix_world); tw=tc@T[:3,:3].T+T[:3,3]
jx=((tw[:,0]-x0)/C).astype(int); jy=((tw[:,1]-y0)/C).astype(int); ok=(jx>=0)&(jx<nx)&(jy>=0)&(jy<ny)
orig={}; n=0
for k in np.nonzero(ok)[0]:
    if not has[jy[k],jx[k]]: continue
    tgt=L[jy[k],jx[k]]-0.15
    if np.isfinite(tgt) and tw[k,2]>tgt:
        orig[str(int(k))]=float(terr.data.vertices[int(k)].co.z); terr.data.vertices[int(k)].co.z-= (tw[k,2]-tgt); n+=1
terr['iq_terrain_orig']=json.dumps(orig); terr.data.update(); print('IQ TERRAIN lowered',n)
# --- materials
def bsdf(m): return [x for x in m.node_tree.nodes if x.bl_idname=='ShaderNodeBsdfPrincipled'][0]
def insert_mul(m, out_socket):
    nt=m.node_tree; b=bsdf(m); l=b.inputs['Base Color'].links[0]; src=l.from_socket
    mx=nt.nodes.new('ShaderNodeMixRGB'); mx.blend_type='MULTIPLY'; mx.inputs[0].default_value=1.0
    nt.links.new(src,mx.inputs[1]); nt.links.new(out_socket,mx.inputs[2]); nt.links.new(mx.outputs[0],b.inputs['Base Color']); return mx
def block_var(m, amp, rowoff=0.5):
    nt=m.node_tree; uv=nt.nodes.new('ShaderNodeUVMap'); uv.uv_map='UVMap'; sp=nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(uv.outputs[0],sp.inputs[0])
    # brick texture (scale 1, offset 0.5 every 2nd row): block id = floor(u + 0.5*(floor(v) mod 2)), floor(v)
    fv=nt.nodes.new('ShaderNodeMath'); fv.operation='FLOOR'; nt.links.new(sp.outputs[1],fv.inputs[0])
    md=nt.nodes.new('ShaderNodeMath'); md.operation='FLOORED_MODULO'; md.inputs[1].default_value=2; nt.links.new(fv.outputs[0],md.inputs[0])
    of=nt.nodes.new('ShaderNodeMath'); of.operation='MULTIPLY_ADD'; of.inputs[1].default_value=rowoff; nt.links.new(md.outputs[0],of.inputs[0]); nt.links.new(sp.outputs[0],of.inputs[2])
    fu=nt.nodes.new('ShaderNodeMath'); fu.operation='FLOOR'; nt.links.new(of.outputs[0],fu.inputs[0])
    cb=nt.nodes.new('ShaderNodeCombineXYZ'); nt.links.new(fu.outputs[0],cb.inputs[0]); nt.links.new(fv.outputs[0],cb.inputs[1])
    wn=nt.nodes.new('ShaderNodeTexWhiteNoise'); wn.noise_dimensions='3D'; nt.links.new(cb.outputs[0],wn.inputs['Vector'])
    mr=nt.nodes.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value=1-amp; mr.inputs['To Max'].default_value=1+amp; nt.links.new(wn.outputs['Value'],mr.inputs['Value'])
    insert_mul(m, mr.outputs[0])
def dirt(m, strength, col=(0.62,0.64,0.55)):
    nt=m.node_tree; ao=nt.nodes.new('ShaderNodeAmbientOcclusion'); ao.inputs['Distance'].default_value=0.25; ao.samples=8
    tc=nt.nodes.new('ShaderNodeTexCoord'); nz=nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=2.2; nz.inputs['Detail'].default_value=6; nt.links.new(tc.outputs['Object'],nz.inputs['Vector'])
    nm=nt.nodes.new('ShaderNodeMapRange'); nm.inputs['From Min'].default_value=0.45; nm.inputs['From Max'].default_value=0.65; nt.links.new(nz.outputs['Fac'],nm.inputs['Value'])
    inv=nt.nodes.new('ShaderNodeMath'); inv.operation='SUBTRACT'; inv.inputs[0].default_value=1.0; nt.links.new(ao.outputs['AO'],inv.inputs[1])
    mm=nt.nodes.new('ShaderNodeMath'); mm.operation='MULTIPLY'; nt.links.new(inv.outputs[0],mm.inputs[0]); nt.links.new(nm.outputs[0],mm.inputs[1])
    fs=nt.nodes.new('ShaderNodeMath'); fs.operation='MULTIPLY'; fs.inputs[1].default_value=strength; fs.use_clamp=True; nt.links.new(mm.outputs[0],fs.inputs[0])
    mx=nt.nodes.new('ShaderNodeMixRGB'); mx.blend_type='MIX'; mx.inputs[1].default_value=(1,1,1,1); mx.inputs[2].default_value=(*col,1); nt.links.new(fs.outputs[0],mx.inputs[0])
    insert_mul(m, mx.outputs[0])
for nm_,amp,ds in [('hn_amphi_seat_stone_blocks',0.09,1.6),('io_amphi_aisle_stone',0.07,1.2),('hn_amphi_riser_coursed_stone',0.10,2.2)]:
    m=bpy.data.materials[nm_]
    if any(n.label=='iq' for n in m.node_tree.nodes): print('IQ already patched',nm_); continue
    block_var(m,amp); dirt(m,ds); m.node_tree.nodes.new('NodeFrame').label='iq'
print('IQ MATERIALS done')
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('IQ SAVED')
