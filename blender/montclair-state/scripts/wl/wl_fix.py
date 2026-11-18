"""wl: N-eye foreground lawn looked sparse. (A) fill visible 0.5 m lawn cells (2-22 m from WA1 N eye) to TGT tufts/m2,
clumped, >=0.15 m off slabs; (B) fine turf micro-variation + bump on the shared ground material, gated to a soft box
around the Stone footway / Richardson south lawn and to green ortho tones."""
import bpy, random, os, numpy as np, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
random.seed(20261109); O=bpy.data.objects; sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
TGT=float(os.environ.get('TGT','20')); step=0.5
GRP=('WV_stone_west_LiDAR','QW_DTM','WT_richardson_west_LiDAR','WU_richardson_reid','RZ2_','WF_east_dorm_LiDAR')
def bv(o,flat=False):
    m=o.matrix_world; V=[m@v.co for v in o.data.vertices]
    if flat: V=[Vector((v.x,v.y,0)) for v in V]
    return BVHTree.FromPolygons(V,[tuple(p.vertices) for p in o.data.polygons])
slabn=[n for n in O.keys() if O[n].type=='MESH' and n.startswith(('QS_footway_','QS_service_','QW_footway_','QW_service_','QT_soil_edge_','QW_soil_edge_','QS_walk','QT_walk'))]
SF=[bv(O[n],True) for n in slabn]
GR=[bv(O[n]) for n in O.keys() if O[n].type=='MESH' and n.startswith(GRP)]
def gz(x,y):
    z=[b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))[0] for b in GR]; z=[h.z for h in z if h is not None]
    return max(z) if z else None
def clear(x,y):
    p=Vector((x,y,0))
    return all(b.find_nearest(p,0.15)[0] is None for b in SF)
from bpy_extras.object_utils import world_to_camera_view
allpts={}
for gg in [O[n] for n in O.keys() if 'grass_points' in n and O[n].type=='MESH']:
    mm=gg.matrix_world
    for vv in gg.data.vertices:
        c=mm@vv.co; k=(float(np.floor(c.x/step)*step),float(np.floor(c.y/step)*step)); allpts[k]=allpts.get(k,0)+1
cells=set()
for camn in os.environ.get('CAMS','WA1_CAM_eye_stone_footway_from_N').split(','):
    cam=O[camn]; o=cam.matrix_world.translation
    for ix in range(int((o.x-24)/step),int((o.x+24)/step)):
        for iy in range(int((o.y-24)/step),int((o.y+24)/step)):
            k=(ix*step,iy*step); x,y=k[0]+0.25,k[1]+0.25
            d=((x-o.x)**2+(y-o.y)**2)**0.5
            if d<2 or d>22: continue
            z=gz(x,y)
            if z is None: continue
            p=world_to_camera_view(sc,cam,Vector((x,y,z)))
            if not (0<=p.x<=1 and 0<=p.y<=0.62 and p.z>0): continue
            nb=sum(allpts.get((k[0]+a*step,k[1]+b*step),0) for a in (-1,0,1) for b in (-1,0,1))
            if nb<3: continue
            if not clear(x,y): continue
            cells.add(k)
print('CELLS',len(cells))
cnt={}
for gg in [O[n] for n in O.keys() if 'grass_points' in n and O[n].type=='MESH']:
    mm=gg.matrix_world
    for vv in gg.data.vertices:
        c=mm@vv.co; k=(float(np.floor(c.x/step)*step),float(np.floor(c.y/step)*step))
        if k in cells: cnt[k]=cnt.get(k,0)+1
before=sum(cnt.values())/(len(cells)*step*step) if cells else 0
g=O['QS_Richardson_lawn_grass_points_UNVERIFIED']; mi=g.matrix_world.inverted()
bm=bmesh.new(); bm.from_mesh(g.data); add=0
for k in sorted(cells):
    n=int(TGT*step*step-cnt.get(k,0)+random.random())
    if n<=0: continue
    cx,cy=k[0]+0.1+random.random()*0.3,k[1]+0.1+random.random()*0.3
    for i in range(n):
        for t in range(6):
            if t>2: cx,cy=k[0]+0.1+random.random()*0.3,k[1]+0.1+random.random()*0.3
            x=cx+random.gauss(0,0.1); y=cy+random.gauss(0,0.1)
            if not clear(x,y): continue
            z=gz(x,y)
            if z is None: continue
            bm.verts.new(mi@Vector((x,y,z))); add+=1; break
bm.to_mesh(g.data); bm.free(); g.data.update()
print('DENS before %.1f/m2, added %d, after %.1f/m2'%(before,add,before+add/(len(cells)*step*step)))
# (B) shader
m=bpy.data.materials['OW2_Context_skirt_ortho_strip_tone_UNVERIFIED']; nt=m.node_tree; N=nt.nodes; L=nt.links
for n in [n for n in N if n.name.startswith('WL_')]: N.remove(n)
bs=N['Principled BSDF']; src=N['WJ_final'].outputs['Result']
def nn(t,name,loc):
    n=N.new(t); n.name=name; n.label=name; n.location=loc; return n
X0,X1,Y0,Y1,F=116.0,152.0,244.0,302.0,2.5
geo=nn('ShaderNodeNewGeometry','WL_geo',(1400,-2200)); sp=nn('ShaderNodeSeparateXYZ','WL_sep',(1600,-2200)); L.new(geo.outputs['Position'],sp.inputs[0])
def ramp(sock,a,b,name,loc,inv=False):
    r=nn('ShaderNodeMapRange',name,loc); r.inputs[1].default_value=a; r.inputs[2].default_value=b
    if inv: r.inputs[3].default_value=1; r.inputs[4].default_value=0
    L.new(sock,r.inputs[0]); return r.outputs[0]
gx0=ramp(sp.outputs[0],X0,X0+F,'WL_gx0',(1800,-2100)); gx1=ramp(sp.outputs[0],X1-F,X1,'WL_gx1',(1800,-2250),True)
gy0=ramp(sp.outputs[1],Y0,Y0+F,'WL_gy0',(1800,-2400)); gy1=ramp(sp.outputs[1],Y1-F,Y1,'WL_gy1',(1800,-2550),True)
def mul(a,b,name,loc):
    mm=nn('ShaderNodeMath',name,loc); mm.operation='MULTIPLY'; L.new(a,mm.inputs[0]); L.new(b,mm.inputs[1]); return mm.outputs[0]
box=mul(mul(gx0,gx1,'WL_m1',(2000,-2150)),mul(gy0,gy1,'WL_m2',(2000,-2450)),'WL_box',(2200,-2300))
# greenness gate: G - R of the ortho tone
sc_=nn('ShaderNodeSeparateColor','WL_csep',(1600,-1900)); L.new(src,sc_.inputs[0])
dgr=nn('ShaderNodeMath','WL_gmr',(1800,-1900)); dgr.operation='SUBTRACT'; L.new(sc_.outputs['Green'],dgr.inputs[0]); L.new(sc_.outputs['Red'],dgr.inputs[1])
gate=mul(box,ramp(dgr.outputs[0],float(os.environ.get('G0','-0.03')),float(os.environ.get('G1','0.0')),'WL_green',(2000,-1900)),'WL_gate',(2400,-2100))
nz=nn('ShaderNodeTexNoise','WL_fine',(1800,-2700)); nz.inputs['Scale'].default_value=float(os.environ.get('FS','38')); nz.inputs['Detail'].default_value=4; nz.inputs['Roughness'].default_value=0.6
L.new(geo.outputs['Position'],nz.inputs['Vector'])
fv=ramp(nz.outputs['Fac'],0.3,0.7,'WL_fv',(2000,-2700)); fvn=fv.node; fvn.inputs[3].default_value=float(os.environ.get('LO','0.72')); fvn.inputs[4].default_value=float(os.environ.get('HI','1.0'))
sv=nn('ShaderNodeVectorMath','WL_scale',(2400,-1700)); sv.operation='SCALE'; L.new(src,sv.inputs[0]); L.new(fv,sv.inputs['Scale'])
tf=nn('ShaderNodeMix','WL_turf',(2500,-1700)); tf.data_type='RGBA'; tf.inputs['Factor'].default_value=float(os.environ.get('TINT','0.35'))
L.new(sv.outputs[0],tf.inputs['A']); tf.inputs['B'].default_value=(0.085,0.13,0.045,1)
tsv=nn('ShaderNodeVectorMath','WL_tscale',(2550,-1900)); tsv.operation='SCALE'; L.new(tf.outputs['Result'],tsv.inputs[0]); L.new(fv,tsv.inputs['Scale'])
mx=nn('ShaderNodeMix','WL_final',(2600,-1500)); mx.data_type='RGBA'; L.new(gate,mx.inputs['Factor']); L.new(src,mx.inputs['A']); L.new(tsv.outputs[0],mx.inputs['B'])
L.new(mx.outputs['Result'],bs.inputs['Base Color'])
bp=nn('ShaderNodeBump','WL_bump',(2600,-2700)); bp.inputs['Distance'].default_value=0.01
L.new(gate,bp.inputs['Strength'])
sc2=nn('ShaderNodeMath','WL_bstr',(2400,-2900)); sc2.operation='MULTIPLY'; sc2.inputs[1].default_value=float(os.environ.get('BS','0.35'))
L.new(gate,sc2.inputs[0]); L.new(sc2.outputs[0],bp.inputs['Strength'])
L.new(nz.outputs['Fac'],bp.inputs['Height'])
if bs.inputs['Normal'].is_linked:
    prev=bs.inputs['Normal'].links[0].from_socket; L.new(prev,bp.inputs['Normal'])
L.new(bp.outputs['Normal'],bs.inputs['Normal'])
print('WL nodes',len([n for n in N if n.name.startswith('WL_')]), 'users',m.users)
bpy.ops.wm.save_mainfile(); print('SAVED')
