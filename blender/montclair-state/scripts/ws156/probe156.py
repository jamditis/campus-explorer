# ws156 memory-safe probe: append ONLY Freeman N-face objects from main (no full load) and report geometry/materials
import bpy, json, resource
from mathutils import Vector
M='/workspace/nj-scenes/montclair-state/'
src=M+'montclair_state.blend'
with bpy.data.libraries.load(src, link=False) as (fr, to):
    names=[n for n in fr.objects if ('Freeman' in n and ('_N_' in n or 'N_end' in n or 'letter' in n.lower() or 'end_wall' in n)) or n=='Freeman Hall walls']
    to.objects=names
print('PROBE156 appended',len(names),'RSS',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)
fr6=json.load(open(M+'data/uv/freeman_osm_probe.json')); e=[x for x in fr6['edges'] if x['i']==6][0]
A=Vector((*e['a'],0)); U=Vector((*e['u'],0)).normalized(); N=Vector((*e['n'],0)).normalized()
out={}
for o in bpy.data.objects:
    if o is None: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    t=[(p-A).dot(U) for p in bb]; d=[(p-A).dot(N) for p in bb]; z=[p.z for p in bb]
    r=dict(type=o.type,hide_render=o.hide_render,t=[round(min(t),2),round(max(t),2)],d=[round(min(d),2),round(max(d),2)],z=[round(min(z),2),round(max(z),2)],
           mats=[m.name if m else None for m in (o.data.materials if hasattr(o.data,'materials') else [])])
    if o.type=='FONT': r.update(body=o.data.body,size=round(o.data.size,3),loc=[round(x,2) for x in o.matrix_world.translation],extrude=o.data.extrude,scale=[round(x,3) for x in o.scale])
    if o.type=='MESH': r['nf']=len(o.data.polygons)
    out[o.name]=r
for k in sorted(out): print('PROBE156',k,json.dumps(out[k]))
for m in bpy.data.materials:
    if 'Freeman' in m.name and m.use_nodes:
        cols=[]
        for nd in m.node_tree.nodes:
            if nd.type=='BSDF_PRINCIPLED' and not nd.inputs['Base Color'].is_linked: cols.append(('bsdf',[round(x,3) for x in nd.inputs['Base Color'].default_value[:3]]))
            if nd.type=='VALTORGB': cols.append(('ramp',[[round(x,3) for x in el.color[:3]] for el in nd.color_ramp.elements]))
            if nd.type=='RGB': cols.append(('rgb',[round(x,3) for x in nd.outputs[0].default_value[:3]]))
            if nd.type=='TEX_BRICK': cols.append(('brick',[round(x,3) for x in nd.inputs['Color1'].default_value[:3]],[round(x,3) for x in nd.inputs['Color2'].default_value[:3]],[round(x,3) for x in nd.inputs['Mortar'].default_value[:3]]))
            if nd.type=='TEX_IMAGE' and nd.image: cols.append(('img',nd.image.name))
        print('PROBE156 MAT',m.name,cols)
json.dump(out,open(M+'scripts/ws156/probe156.json','w'),indent=1)
print('PROBE156 DONE RSS',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)
