"""wh probe2: skirt attributes ou_edge / ow2_strip, shader routing, patch bbox, south gap."""
import bpy, json
from mathutils import Vector
from collections import Counter

ROOT='/workspace/nj-scenes/montclair-state'
PN='WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED'
SK='Context_skirt_3DEP_ortho_4km'
P=bpy.data.objects[PN]; sk=bpy.data.objects[SK]
out={}

def attrs_of(me, label):
    rec=[]
    for a in me.attributes:
        info=dict(name=a.name, domain=a.domain, type=a.data_type)
        try:
            n=len(a.data)
            info['n']=n
            if a.data_type=='FLOAT' and n:
                vs=[a.data[i].value for i in range(0,n,max(1,n//50))]
                info['sample_min']=round(min(vs),4); info['sample_max']=round(max(vs),4)
                info['sample_mean']=round(sum(vs)/len(vs),4)
            elif a.data_type in ('FLOAT_COLOR','BYTE_COLOR') and n:
                vs=[tuple(a.data[i].color) for i in range(0,min(5,n))]
                info['sample']=vs
        except Exception as e:
            info['err']=str(e)
        rec.append(info)
    print(label, rec)
    return rec

out['patch_base_attrs']=attrs_of(P.data,'PATCH_BASE')
out['skirt_base_attrs']=attrs_of(sk.data,'SKIRT_BASE')

dg=bpy.context.evaluated_depsgraph_get()
ske=sk.evaluated_get(dg); sme=ske.to_mesh()
out['skirt_eval_attrs']=attrs_of(sme,'SKIRT_EVAL')
# sample ou_edge and ow2_strip in east-dorm box vs outside
def sample_attr(me, obj, aname, pts):
    attr=me.attributes.get(aname)
    if not attr:
        return None
    # build a simple nearest-vert lookup via bounding — instead iterate faces? too heavy.
    # Use a dict of xy->value from a stride sample of verts, then nearest.
    import numpy as np
    n=len(me.vertices)
    step=max(1, n//80000)
    xs=[]; ys=[]; vs=[]
    mw=obj.matrix_world
    for i in range(0,n,step):
        c=mw@me.vertices[i].co
        xs.append(c.x); ys.append(c.y)
        if attr.data_type=='FLOAT':
            vs.append(attr.data[i].value)
        elif attr.data_type in ('FLOAT_COLOR','BYTE_COLOR'):
            vs.append(attr.data[i].color[0])
        else:
            vs.append(None)
    xs=np.array(xs); ys=np.array(ys); vs=np.array(vs,dtype=float)
    recs=[]
    for x,y,lab in pts:
        d=(xs-x)**2+(ys-y)**2
        j=int(d.argmin())
        recs.append(dict(lab=lab,x=x,y=y, nearest_xy=(round(float(xs[j]),2),round(float(ys[j]),2)),
                         dist=round(float(d[j]**0.5),2), val=round(float(vs[j]),4)))
    return recs

pts=[
    (175,420,'patch_interior'),
    (250,400,'east_of_bohn'),
    (280,450,'NE_esc'),
    (298,400,'east_edge_in'),
    (310,400,'east_edge_out'),
    (52,400,'west_edge_in'),
    (40,400,'west_edge_out'),
    (200,322,'south_gap'),
    (200,318,'south_out'),
    (200,360,'south_in'),
    (180,500,'northish'),
    (200,200,'south_of_patch_lidar_zone'),
    (0,0,'origin'),
    (100,100,'SW_campus'),
]
if sme.attributes.get('ou_edge'):
    out['ou_edge_samples']=sample_attr(sme, sk, 'ou_edge', pts)
    print('OU_EDGE', out['ou_edge_samples'])
if sme.attributes.get('ow2_strip'):
    out['ow2_strip_samples']=sample_attr(sme, sk, 'ow2_strip', pts)
    print('OW2_STRIP', out['ow2_strip_samples'])
# any other float attrs of interest
for an in sme.attributes.keys():
    if an not in ('ou_edge','ow2_strip','position','sharp_face','UVMap','ortho','.selection'):
        print('OTHER ATTR', an, sme.attributes[an].data_type, sme.attributes[an].domain)

ske.to_mesh_clear()

# shader routing from Attribute nodes
mat=P.data.materials[0]; nt=mat.node_tree
def trace(node, depth=0, seen=None):
    if seen is None: seen=set()
    if node.name in seen or depth>8: return
    seen.add(node.name)
    outs=[]
    for s in node.outputs:
        for l in s.links:
            rec=f"{'  '*depth}{node.name}.{s.name} -> {l.to_node.name}.{l.to_socket.name} ({l.to_node.type})"
            print(rec); outs.append(rec)
            trace(l.to_node, depth+1, seen)
    return outs

print('--- TRACE Attribute (ou_edge) ---')
out['trace_ou']= []
# recapture print via list
lines=[]
for n in nt.nodes:
    if n.type=='ATTRIBUTE':
        print('ATTR NODE', n.name, n.attribute_name)
        trace(n)

# dump key input defaults for ah_mrV / TS_gate / Map Range tied to attrs
for nm in ['ah_mrV','ah_mrS','ah_leafon','Map Range','Map Range.001','Math','Math.001','Mix','Mix.001',
           'EP_haze_mr','TS_gate','TS_naip_hsv','TS_haze','TS_final','QV_x0','QV_x1','QV_y0','QV_y1']:
    n=nt.nodes.get(nm)
    if not n: continue
    ins={}
    for i in n.inputs:
        if i.is_linked:
            ins[i.name]='LINKED from '+i.links[0].from_node.name+'.'+i.links[0].from_socket.name
        else:
            try:
                v=i.default_value
                if hasattr(v,'__len__') and not isinstance(v,str):
                    v=[round(float(x),4) for x in list(v)[:4]]
                else:
                    v=round(float(v),4) if isinstance(v,(int,float)) else str(v)
            except Exception:
                v='?'
            ins[i.name]=v
    print(nm, n.type, ins)
    out.setdefault('node_inputs',{})[nm]=dict(type=n.type, inputs=ins)

# patch bbox from verts
import numpy as np
n=len(P.data.vertices)
co=np.zeros(n*3,np.float32); P.data.vertices.foreach_get('co',co); co=co.reshape(n,3)
mw=np.array(P.matrix_world)
# P at origin likely
print('PATCH xyz min', co.min(0), 'max', co.max(0))
print('PATCH y percentiles', np.percentile(co[:,1],[0,1,5,50,95,99,100]))
print('PATCH x percentiles', np.percentile(co[:,0],[0,1,5,50,95,99,100]))
out['patch_bbox']=dict(xmin=float(co[:,0].min()), xmax=float(co[:,0].max()),
                       ymin=float(co[:,1].min()), ymax=float(co[:,1].max()),
                       zmin=float(co[:,2].min()), zmax=float(co[:,2].max()))

# south-edge band: find verts with y<325 and report z vs expected
south=co[co[:,1]<325]
print('SOUTH y<325 verts', len(south), 'z min/max/mean', south[:,2].min() if len(south) else None,
      south[:,2].max() if len(south) else None, south[:,2].mean() if len(south) else None)
if len(south):
    # lowest 10
    idx=south[:,2].argsort()[:12]
    out['south_low']=[dict(x=round(float(south[i,0]),2),y=round(float(south[i,1]),2),z=round(float(south[i,2]),2)) for i in idx]
    print('SOUTH lowest', out['south_low'])

# GN on skirt: list node groups briefly
gns=[]
for m in sk.modifiers:
    if m.type=='NODES' and m.node_group:
        ng=m.node_group
        gns.append(dict(mod=m.name, ng=ng.name, nodes=[n.name+':'+n.type for n in ng.nodes][:40],
                        outputs=[i.name for i in ng.interface.items_tree if getattr(i,'in_out',None)=='OUTPUT']))
        print('GN', m.name, 'out', gns[-1]['outputs'], 'nodes', len(ng.nodes))
out['skirt_gns_brief']=[{k:g[k] for k in ('mod','ng','outputs')} for g in gns]

# does OU / OW2 store named attrs?
for m in sk.modifiers:
    if m.type=='NODES' and m.node_group and m.name in ('OU_skirt_edge_tone','OW2_skirt_strip_mask'):
        ng=m.node_group
        store=[]
        for n in ng.nodes:
            if 'STORE' in n.type or n.type=='GeometryNodeStoreNamedAttribute':
                store.append(dict(name=n.name, attr=getattr(n,'name','') or n.inputs['Name'].default_value if 'Name' in n.inputs else '?',
                                  typ=n.data_type if hasattr(n,'data_type') else ''))
            if n.type=='GeometryNodeInputNamedAttribute':
                store.append(dict(read=n.inputs['Name'].default_value if 'Name' in n.inputs else getattr(n,'name','')))
        print('STORE', m.name, store)
        out.setdefault('gn_stores',{})[m.name]=store

json.dump(out, open(f'{ROOT}/data/wh/probe2.json','w'), indent=2)
print('WROTE probe2')
