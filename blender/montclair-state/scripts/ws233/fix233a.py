# ws233 fix a (on ws232b): W53o Stone Hall lower volume. The lower volume's base is z 130.7 but the 3DEP/evaluated ground all around
# it is 135.97..136.97 (probe233a), so the shader's window rows (z0+0.95+k*3.3, 1.52 m tall: 131.65, 134.95, 138.25) put the 134.95-136.47
# row half under the lawn -> sliced windows at grade. Stone Hall has two residence floors (Montclarion 2016); a window cut by the lawn is
# not physical. Decision: rows whose window bottom is below grade are not windows (below-grade wall) -> per-object attribute ti_wmin
# (local z) gates the window/frame/mullion masks; lower volume ti_wmin=137.0 keeps the 138.25 row, drops 131.65/134.95. Objects without
# the attribute read 0 -> unaffected (upper0, any other user of the material).
# Also W53o specks: QS_Richardson_lawn_grass_points verts > 1.0 m above USGS 3DEP in x 100..180, y 170..278 are deleted (floating clumps).
import bpy, bmesh, json, numpy as np
MS='/workspace/nj-scenes/montclair-state/'; rep={}
o=bpy.data.objects['TI_Stone_Hall_313028565_lower_UNVERIFIED']; me=o.data
rep['matrix_identity']=[round(v,4) for row in o.matrix_world for v in row]
a=me.attributes.get('ti_wmin') or me.attributes.new('ti_wmin','FLOAT','POINT')
Wi=o.matrix_world.inverted(); from mathutils import Vector
zl=(Wi@Vector((o.matrix_world.translation.x,o.matrix_world.translation.y,137.0))).z
for i in range(len(me.vertices)): a.data[i].value=zl
rep['ti_wmin_local']=zl
mt=bpy.data.materials['TR_Stone_brick_detail_UNVERIFIED']; nt=mt.node_tree; N=nt.nodes
rep['mat_users']=[ob.name for ob in bpy.data.objects if ob.type=='MESH' and any(s.material==mt for s in ob.material_slots)]
if 'WS233_wmin' not in N:
    at=N.new('ShaderNodeAttribute'); at.name='WS233_wmin'; at.attribute_name='ti_wmin'; at.attribute_type='GEOMETRY'
    gt=N.new('ShaderNodeMath'); gt.name='WS233_wmin_gt'; gt.operation='GREATER_THAN'
    mu=N.new('ShaderNodeMath'); mu.name='WS233_wmin_mul'; mu.operation='MULTIPLY'
    nt.links.new(N['Separate XYZ'].outputs['Z'],gt.inputs[0]); nt.links.new(at.outputs['Fac'],gt.inputs[1])
    m12=N['Math.012']; l=[l for l in nt.links if l.to_node==m12 and l.from_node.name=='Math.009'][0]
    nt.links.new(N['Math.009'].outputs[0],mu.inputs[0]); nt.links.new(gt.outputs[0],mu.inputs[1])
    nt.links.remove(l); nt.links.new(mu.outputs[0],m12.inputs[0] if not m12.inputs[0].is_linked else m12.inputs[1])
    rep['nodes']='added'
# floating grass clumps
P=np.load(MS+'scripts/ws230/dep1m_full_x-280_280_y-280_280_rowS.npy')
def p3(x,y):
    gx=x+280-0.5; gy=y+280-0.5; i=int(np.floor(gy)); j=int(np.floor(gx)); fy=gy-i; fx=gx-j
    return float(P[i,j]*(1-fx)*(1-fy)+P[i,j+1]*fx*(1-fy)+P[i+1,j]*(1-fx)*fy+P[i+1,j+1]*fx*fy)
for gn in ('QS_Richardson_lawn_grass_points_UNVERIFIED','QN_cels_east_lawn_grass_points_UNVERIFIED'):
    g=bpy.data.objects.get(gn)
    if not g: continue
    W=g.matrix_world; bm=bmesh.new(); bm.from_mesh(g.data); dv=[]; hs=[]
    for v in bm.verts:
        w=W@v.co
        if 100<w.x<180 and 170<w.y<278:
            h=w.z-p3(w.x,w.y); hs.append(h)
            if h>1.0: dv.append(v)
    rep[gn]={'n_in_box':len(hs),'max_above_3dep':round(max(hs),2) if hs else None,'deleted':len(dv),'deleted_xyz':[[round(c,2) for c in (W@v.co)] for v in dv[:20]]}
    if dv: bmesh.ops.delete(bm,geom=dv,context='VERTS'); bm.to_mesh(g.data)
    bm.free()
print('F233A',json.dumps(rep),flush=True)
json.dump(rep,open(MS+'scripts/ws233/fix233a_report.json','w'))
