"""wh probe: patch/skirt seam — materials, coords, z-gap, attributes. Read-only."""
import bpy, json, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from collections import Counter

ROOT='/workspace/nj-scenes/montclair-state'
PN='WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED'
SK='Context_skirt_3DEP_ortho_4km'
X0,X1,Y0,Y1=50.,300.,320.,520.
out={}

P=bpy.data.objects.get(PN)
sk=bpy.data.objects.get(SK)
print('PATCH', P is not None, 'SKIRT', sk is not None)
out['patch_exists']=P is not None
out['skirt_exists']=sk is not None
if not P or not sk:
    json.dump(out, open(f'{ROOT}/data/wh/probe.json','w'), indent=2)
    raise SystemExit(1)

print('PATCH mats', [m.name if m else None for m in P.data.materials])
print('SKIRT mats', [m.name if m else None for m in sk.data.materials])
print('shared_mat_ptr', bool(P.data.materials and sk.data.materials and P.data.materials[0]==sk.data.materials[0]))
print('PATCH verts', len(P.data.vertices), 'faces', len(P.data.polygons))
print('PATCH location', tuple(round(x,4) for x in P.location))
print('PATCH dims', tuple(round(x,3) for x in P.dimensions))
print('PATCH attrs', list(P.data.attributes.keys()) if hasattr(P.data,'attributes') else None)
print('PATCH color_attrs', list(P.data.color_attributes.keys()) if hasattr(P.data,'color_attributes') else None)
print('PATCH uv', [uv.name for uv in P.data.uv_layers])
print('SKIRT uv', [uv.name for uv in sk.data.uv_layers])
print('PATCH smooth_count', sum(1 for p in P.data.polygons if p.use_smooth), '/', len(P.data.polygons))
print('SKIRT mods', [m.name+':'+m.type for m in sk.modifiers])
print('PATCH mods', [m.name+':'+m.type for m in P.modifiers])
print('PATCH props', {k:P[k] for k in P.keys()})

out['patch_mats']=[m.name if m else None for m in P.data.materials]
out['skirt_mats']=[m.name if m else None for m in sk.data.materials]
out['shared_mat']=bool(P.data.materials and sk.data.materials and P.data.materials[0]==sk.data.materials[0])
out['patch_nverts']=len(P.data.vertices)
out['patch_nfaces']=len(P.data.polygons)
out['patch_uv']=[uv.name for uv in P.data.uv_layers]
out['skirt_uv']=[uv.name for uv in sk.data.uv_layers]
out['patch_smooth']=sum(1 for p in P.data.polygons if p.use_smooth)
out['skirt_mods']=[m.name+':'+m.type for m in sk.modifiers]
out['patch_mods']=[m.name+':'+m.type for m in P.modifiers]

# material node dump
mat = P.data.materials[0] if P.data.materials else None
out['mat_name']=mat.name if mat else None
nodes_info=[]
if mat and mat.node_tree:
    nt=mat.node_tree
    print('MAT use_nodes', mat.use_nodes, 'nodes', len(nt.nodes))
    for n in nt.nodes:
        rec=dict(name=n.name, type=n.type, label=n.label or '')
        if n.type=='TEX_COORD':
            rec['outputs_used']=[s.name for s in n.outputs if s.is_linked]
        if n.type=='TEX_IMAGE':
            rec['image']=n.image.name if n.image else None
            rec['proj']=getattr(n,'projection','')
        if n.type=='MAPPING':
            rec['scale']=list(n.inputs['Scale'].default_value) if 'Scale' in n.inputs else None
        if n.type=='ATTRIBUTE':
            rec['attr']=getattr(n,'attribute_name','')
        if n.type=='UVMAP':
            rec['uv']=getattr(n,'uv_map','')
        if n.type=='NORMAL_MAP':
            rec['space']=getattr(n,'space','')
        if n.type=='VECT_MATH':
            rec['op']=n.operation
        if n.type=='SEPXYZ' or n.type=='COMBXYZ':
            pass
        if n.type=='VALTORGB':
            rec['elements']=[[list(e.color), e.position] for e in n.color_ramp.elements]
        if n.type=='HUE_SAT':
            rec['hue']=n.inputs['Hue'].default_value
            rec['sat']=n.inputs['Saturation'].default_value
            rec['val']=n.inputs['Value'].default_value
        if n.type=='BSDF_PRINCIPLED':
            rec['base']=list(n.inputs['Base Color'].default_value) if not n.inputs['Base Color'].is_linked else 'LINKED'
            rec['rough']=n.inputs['Roughness'].default_value
            rec['spec']=n.inputs['Specular IOR Level'].default_value if 'Specular IOR Level' in n.inputs else None
        nodes_info.append(rec)
    # links of interest: TexCoord / UV / Geometry / Attribute sources
    sources=[]
    for l in nt.links:
        if l.from_node.type in ('TEX_COORD','UVMAP','NEW_GEOMETRY','ATTRIBUTE','TEX_IMAGE','SEPXYZ','VALUE','MAP_RANGE'):
            sources.append(f"{l.from_node.name}[{l.from_socket.name}] -> {l.to_node.name}[{l.to_socket.name}] ({l.to_node.type})")
    out['coord_links']=sources
    print('COORD LINKS:')
    for s in sources:
        print(' ', s)
out['nodes']=[n for n in nodes_info if n['type'] in (
    'TEX_COORD','UVMAP','TEX_IMAGE','MAPPING','ATTRIBUTE','NORMAL_MAP','BSDF_PRINCIPLED',
    'HUE_SAT','VALTORGB','NEW_GEOMETRY','MAP_RANGE','SEPXYZ','VECT_MATH','MIX','MIX_RGB','GAMMA','BRIGHTCONTRAST'
)]

# named nodes matching ah_ / tone / fade
named=[n.name for n in (mat.node_tree.nodes if mat and mat.node_tree else [])]
out['node_names']=named
print('NODE NAMES', named)

# geometric edge samples
dg=bpy.context.evaluated_depsgraph_get()
Pe=P.evaluated_get(dg); pme=Pe.to_mesh()
pvs=[P.matrix_world@v.co for v in pme.vertices]
pfs=[tuple(p.vertices) for p in pme.polygons]
bp=BVHTree.FromPolygons(pvs,pfs); Pe.to_mesh_clear()
ske=sk.evaluated_get(dg); sme=ske.to_mesh()
svs=[sk.matrix_world@v.co for v in sme.vertices]
sfs=[tuple(p.vertices) for p in sme.polygons]
bs=BVHTree.FromPolygons(svs,sfs); ske.to_mesh_clear()

def hit(bvh,x,y,z0=400):
    h=bvh.ray_cast(Vector((x,y,z0)), Vector((0,0,-1)))
    return h[0] if h[0] is not None else None

# sample just inside and just outside each edge
edges=[]
# east x=300, west x=50, south y=320, north y=520
samples=[]
def add_edge(name, pts_in, pts_out):
    rec={'name':name,'inside':[],'outside':[],'dz':[]}
    for (x,y) in pts_in:
        hp=hit(bp,x,y); hs=hit(bs,x,y)
        rec['inside'].append(dict(x=x,y=y,
            pz=None if hp is None else round(hp.z,3),
            sz=None if hs is None else round(hs.z,3),
            dz=None if (hp is None or hs is None) else round(hp.z-hs.z,3)))
    for (x,y) in pts_out:
        hp=hit(bp,x,y); hs=hit(bs,x,y)
        rec['outside'].append(dict(x=x,y=y,
            pz=None if hp is None else round(hp.z,3),
            sz=None if hs is None else round(hs.z,3)))
    zs=[r['dz'] for r in rec['inside'] if r['dz'] is not None]
    rec['dz_stats']=dict(n=len(zs),
        min=min(zs) if zs else None, max=max(zs) if zs else None,
        mean=round(sum(zs)/len(zs),3) if zs else None)
    samples.append(rec)
    print(name, 'inside_dz', rec['dz_stats'], 'n_out_patchhits', sum(1 for r in rec['outside'] if r['pz'] is not None))

ys=list(range(330,511,20))
xs=list(range(60,291,20))
add_edge('east_x300', [(298,y) for y in ys], [(302,y) for y in ys])
add_edge('west_x50', [(52,y) for y in ys], [(48,y) for y in ys])
add_edge('south_y320', [(x,322) for x in xs], [(x,318) for x in xs])
add_edge('north_y520', [(x,518) for x in xs], [(x,522) for x in xs])
# mid-edge more densely on east escarpment
add_edge('east_esc_dense', [(297,y) for y in range(340,501,10)], [(303,y) for y in range(340,501,10)])
out['edges']=samples

# interior vs near-edge z compared to skirt (should be ~+0.06 where GN dipped)
interior=[]
for x,y in [(175,420),(200,400),(250,400),(100,360),(280,480),(220,450)]:
    hp=hit(bp,x,y); hs=hit(bs,x,y)
    interior.append(dict(x=x,y=y,
        pz=None if hp is None else round(hp.z,3),
        sz=None if hs is None else round(hs.z,3),
        dz=None if (hp is None or hs is None) else round(hp.z-hs.z,3)))
out['interior']=interior
print('INTERIOR dz (patch-skirt, expect ~0.06 under overlap)', interior)

# cameras
cams=[o.name for o in bpy.data.objects if o.type=='CAMERA' and any(k in o.name for k in (
    'TI_CAM_oblique_east','WF_CAM','WG_CAM','WD_CAM','WH_CAM','WE_CAM'))]
out['cams']=cams
print('CAMS', cams)

# walk/pad materials for alternate B
walk=bpy.data.objects.get('WD_walk_1132693523_UNVERIFIED')
pad=bpy.data.objects.get('WG_Bohn_W_door_landing_slab_UNVERIFIED')
out['walk_mats']=[m.name if m else None for m in walk.data.materials] if walk else None
out['pad_mats']=[m.name if m else None for m in pad.data.materials] if pad else None
print('WALK mats', out['walk_mats'], 'PAD mats', out['pad_mats'])

# collection
out['collections']=[c.name for c in bpy.data.collections if c.name.startswith('W') and (
    'WF' in c.name or 'WG' in c.name or 'WH' in c.name or 'east_dorm' in c.name or 'Bohn_W' in c.name)]
print('COLS', out['collections'])

json.dump(out, open(f'{ROOT}/data/wh/probe.json','w'), indent=2)
print('WROTE data/wh/probe.json')
