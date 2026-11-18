# Session ir (2026-10-25): patch on top of iq (order: ip build -> iq patch -> ir patch; re-run ir after either).
# (1) Softer per-block tone variation (iq's +-9/7/10% read a bit like roof tiles in the close-up): seats +-5.5%, aisle +-4.5%,
#     risers +-6.5%, plus a large-scale (~3 m) weathering patch noise (+-6%) so the variation is not one regular grid.
# (2) Seat-front arris: seat-top cells whose neighbour is a riser stepping DOWN (>5 cm) get ir_amphi_seat_arris, a copy of the
#     seat stone ~12% lighter and slightly smoother (worn, sun-catching front edge), giving each row a highlight line. ~8 cm wide.
# Env: SAVE=1; REVERT=1 puts arris faces back on the seat material (material slot stays, unused).
import bpy, bmesh, os
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data
SEAT=1; RISER=2
names=[m.name if m else None for m in me.materials]
def bsdf(m): return [x for x in m.node_tree.nodes if x.bl_idname=='ShaderNodeBsdfPrincipled'][0]
def insert_mul(m, out_socket):
    nt=m.node_tree; b=bsdf(m); l=b.inputs['Base Color'].links[0]; src=l.from_socket
    mx=nt.nodes.new('ShaderNodeMixRGB'); mx.blend_type='MULTIPLY'; mx.inputs[0].default_value=1.0
    nt.links.new(src,mx.inputs[1]); nt.links.new(out_socket,mx.inputs[2]); nt.links.new(mx.outputs[0],b.inputs['Base Color']); return mx
if os.environ.get('REVERT')=='1':
    if 'ir_amphi_seat_arris' in names:
        k=names.index('ir_amphi_seat_arris')
        for p in me.polygons:
            if p.material_index==k: p.material_index=SEAT
    if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile()
    print('IR REVERTED'); raise SystemExit
# (1) materials
for nm_,amp in [('hn_amphi_seat_stone_blocks',0.055),('io_amphi_aisle_stone',0.045),('hn_amphi_riser_coursed_stone',0.065)]:
    m=bpy.data.materials[nm_]; nt=m.node_tree
    if any(n.label=='ir' for n in nt.nodes): print('IR already patched',nm_); continue
    hit=0
    for n in nt.nodes:
        if n.bl_idname=='ShaderNodeMapRange' and n.inputs['Value'].links and n.inputs['Value'].links[0].from_node.bl_idname=='ShaderNodeTexWhiteNoise':
            n.inputs['To Min'].default_value=1-amp; n.inputs['To Max'].default_value=1+amp; hit+=1
    tc=nt.nodes.new('ShaderNodeTexCoord'); nz=nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=0.33; nz.inputs['Detail'].default_value=3
    nt.links.new(tc.outputs['Object'],nz.inputs['Vector'])
    mr=nt.nodes.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value=0.3; mr.inputs['From Max'].default_value=0.7; mr.inputs['To Min'].default_value=0.94; mr.inputs['To Max'].default_value=1.06
    nt.links.new(nz.outputs['Fac'],mr.inputs['Value']); insert_mul(m,mr.outputs[0]); nt.nodes.new('NodeFrame').label='ir'
    print('IR MAT',nm_,'whitenoise ranges set',hit)
# (2) arris material + faces
seatm=bpy.data.materials['hn_amphi_seat_stone_blocks']
am=bpy.data.materials.get('ir_amphi_seat_arris')
if am is None:
    am=seatm.copy(); am.name='ir_amphi_seat_arris'; nt=am.node_tree
    rgb=nt.nodes.new('ShaderNodeRGB'); rgb.outputs[0].default_value=(1.13,1.12,1.10,1); insert_mul(am,rgb.outputs[0])
    bsdf(am).inputs['Roughness'].default_value=0.78
if 'ir_amphi_seat_arris' not in names: me.materials.append(am); names.append('ir_amphi_seat_arris')
K=names.index('ir_amphi_seat_arris')
bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
for f in bm.faces:
    if f.material_index==K: f.material_index=SEAT
n=0
for f in bm.faces:
    if f.material_index!=SEAT: continue
    zt=max(v.co.z for v in f.verts)
    for e in f.edges:
        for g in e.link_faces:
            if g is f or g.material_index!=RISER: continue
            if min(v.co.z for v in g.verts) < zt-0.05 and max(v.co.z for v in g.verts) <= zt+0.02:
                f.material_index=K; n+=1; break
        if f.material_index==K: break
bm.to_mesh(me); bm.free(); me.update()
print('IR ARRIS faces',n)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('IR SAVED')
