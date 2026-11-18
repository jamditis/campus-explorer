# ws121 b: plaza saw-cut joints + tan bands (2020 ortho: tan cross bands ~4.4 m apart, first at y ~ -169.7, panels
# aligned to College Ave ~11 deg E of N), precast coping on the D planter, planter shrubs -> Yew shrub material+displace.
import bpy, bmesh, math, os, numpy as np
def ob(p): return next(o for o in bpy.data.objects if o.name.startswith(p))
base=ob('WS120_Chapin_W_N_plaza_ext').data.materials[0]
m=bpy.data.materials.new('WS121_Chapin_W_plaza_concrete_sawcut_1p5m_tan_bands_4p4m_ortho2020_UNVERIFIED'); m.use_nodes=True
nt=m.node_tree; N=nt.nodes; L=nt.links
bs=N.get('Principled BSDF'); bs.inputs['Roughness'].default_value=0.8
geo=N.new('ShaderNodeNewGeometry'); sep=N.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Position'],sep.inputs[0])
a=math.radians(11.3); ca,sa=math.cos(a),math.sin(a)
def mth(op,x,y=None,v=None):
    n=N.new('ShaderNodeMath'); n.operation=op
    for idx,s in enumerate((x,y)):
        if s is None: continue
        if isinstance(s,(int,float)): n.inputs[idx].default_value=s
        else: L.new(s,n.inputs[idx])
    return n.outputs[0]
# along (v) and across (u) coordinates
v=mth('ADD',mth('MULTIPLY',sep.outputs['X'],sa),mth('MULTIPLY',sep.outputs['Y'],ca))
u=mth('SUBTRACT',mth('MULTIPLY',sep.outputs['X'],ca),mth('MULTIPLY',sep.outputs['Y'],sa))
V0=(-207.5*sa+(-169.7)*ca)
band=mth('LESS_THAN',mth('PINGPONG',mth('SUBTRACT',v,V0),2.2),0.225)  # 0.45 m tan band every 4.4 m
def joint(c,p,w):
    return mth('LESS_THAN',mth('PINGPONG',c,p/2),w)
j=mth('MAXIMUM',joint(v,1.466,0.006),joint(u,1.5,0.006))
mix=N.new('ShaderNodeMix'); mix.data_type='RGBA'; L.new(band,mix.inputs['Factor'])
mix.inputs['A'].default_value=(0.62,0.60,0.56,1); mix.inputs['B'].default_value=(0.55,0.42,0.30,1)
mix2=N.new('ShaderNodeMix'); mix2.data_type='RGBA'; L.new(j,mix2.inputs['Factor'])
L.new(mix.outputs['Result'],mix2.inputs['A']); mix2.inputs['B'].default_value=(0.22,0.21,0.2,1)
noi=N.new('ShaderNodeTexNoise'); noi.inputs['Scale'].default_value=3.0
mix3=N.new('ShaderNodeMix'); mix3.data_type='RGBA'; mix3.blend_type='MULTIPLY'; mix3.inputs['Factor'].default_value=0.12
L.new(mix2.outputs['Result'],mix3.inputs['A']); L.new(noi.outputs['Color'],mix3.inputs['B'])
L.new(mix3.outputs['Result'],bs.inputs['Base Color']); m.diffuse_color=(0.62,0.60,0.56,1)
n=0
for o in bpy.data.objects:
    if o.type=='MESH' and o.name.startswith(('WS116_Chapin_W_plaza_concrete','WS119_Chapin_W_N_plaza_concrete','WS119_Chapin_W_terrace_walk_N','WS120_Chapin_W_N_plaza_ext','WS121_Chapin_W_plaza_NW_corner')):
        for i,s in enumerate(o.data.materials):
            if s==base or (s and s.name.startswith('Paving_concrete')): o.data.materials[i]=m; n+=1
print('M121b plaza mat on',n)
# coping on the D planter (precast, 0.32 wide, 6 cm, 3.5 cm overhang each side)
CX,CY,AX,BY=-208.3,-171.9,2.95,6.2; TOP=125.20; TW=0.25
def dshape(a,b,n=28): return [(CX-a,CY)]+[(CX-a*math.cos(t),CY+b*math.sin(t)) for t in np.linspace(0,math.pi,n)[1:-1]]+[(CX+a,CY)]
po=dshape(AX+0.035,BY+0.035); pi=[(x,y+TW-0.035) for x,y in dshape(AX-TW-0.035,BY-TW-0.035)]
po=[(x,y-0.035) if abs(y-CY)<1e-6 else (x,y) for x,y in po]
cop=ob('WS119_Chapin_W_terrace_wall_coping')
me=bpy.data.meshes.new('WS121_Chapin_W_round_planter_coping_precast_UNVERIFIED'); o=bpy.data.objects.new(me.name,me)
for c in cop.users_collection: c.objects.link(o)
me.materials.append(cop.data.materials[0])
bm=bmesh.new(); nn=len(po)
ot=[bm.verts.new((x,y,TOP+0.06)) for x,y in po]; it=[bm.verts.new((x,y,TOP+0.06)) for x,y in pi]
ob_=[bm.verts.new((x,y,TOP-0.005)) for x,y in po]; ib=[bm.verts.new((x,y,TOP-0.005)) for x,y in pi]
for i in range(nn):
    k=(i+1)%nn
    bm.faces.new((ot[i],ot[k],it[k],it[i])); bm.faces.new((ob_[k],ob_[i],ib[i],ib[k]))
    bm.faces.new((ot[k],ot[i],ob_[i],ob_[k])); bm.faces.new((it[i],it[k],ib[k],ib[i]))
bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free()
print('M121b coping verts',len(me.vertices))
# planter shrubs: use the campus Yew shrub material + its displace (as on WS105 bank shrubs)
src=ob('WS105_bank_shrub_02_ortho2020'); sh=ob('WS120_Chapin_W_round_planter_shrubs')
sh.data.materials[0]=src.data.materials[0]
for md in src.modifiers:
    if md.type=='DISPLACE':
        d=sh.modifiers.new('WS121_displace','DISPLACE')
        for at in ('texture','strength','mid_level','direction','texture_coords'):
            try: setattr(d,at,getattr(md,at))
            except Exception as e: print('M121b attr',at,e)
        d.strength=min(d.strength,0.12)
print('M121b shrubs mat',sh.data.materials[0].name,[md.type for md in sh.modifiers])
SAVE=os.environ.get('SAVE','main')
if SAVE=='main': bpy.ops.wm.save_mainfile(); print('M121b SAVED main')
else: bpy.ops.wm.save_as_mainfile(filepath=SAVE,copy=True); print('M121b SAVED',SAVE)
