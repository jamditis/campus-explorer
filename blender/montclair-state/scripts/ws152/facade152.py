# ws152 — Freeman Hall W/E long façades: cream-brick piers framing red porcelain-enamel spandrel bays
# with grey aluminium ribbon-window grid (refs/public/ws151 Commons 2007 + refs/public/ws152 Montclarion 2019).
# Usable in an empty test scene (proxy walls) and in main (finds 'Freeman Hall walls', ray-casts the real wall plane,
# retires old W/E façade skins by geometry, hides not deletes).  All layout UNVERIFIED beyond the photo counts.
import bpy, bmesh, math, random
from mathutils import Vector
TAG='WS152'
# OSM 312845860 ring (scene XY): long sides are W (NNE->SSW) and E; N short side at y~-169, S at y~-222
W_N=Vector((-92.966,-168.958)); W_S=Vector((-105.022,-220.367))
E_N=Vector((-78.293,-172.383)); E_S=Vector((-90.374,-223.781))
Z_GRID_BOT=126.6   # extends below grade (terrain hides it); LiDAR grade W 127.3 (S) .. 128.1 (N), E 125.9..127.5
Z_FLOOR0=127.9     # bottom of the first-storey spandrel (grade 127.3 S .. 128.1 N, so the base band is taller at the S end as in the photos) UNVERIFIED
Z_GRID_TOP=146.2   # underside of white fascia; LiDAR roof slab 146.9
NFL=7              # Montclarion 2019: seven floors; photos: 7 window rows
SPAN_FRAC=0.47     # spandrel share of a storey (crop: spandrel ~120 px vs window ~130 px)
# N->S sequence along each long façade (metres / column counts) from the photos: [3,6,6,6,3,5] columns
COL=1.05; NCORNER=1.2; STAIR=2.4; NPIER=3.0; SCORNER=1.5; BAYS=[3,6,6,6,3,5]
MULL=0.07          # aluminium mullion width
PIER_OUT=0.06; GRID_OUT=0.035; SPAN_IN=0.015; GLASS_IN=0.025

def mat(name, base, rough=0.5, metal=0.0, spec=0.5):
    m=bpy.data.materials.get(name)
    if m: return m
    m=bpy.data.materials.new(name); m.use_nodes=True
    b=m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value=(*base,1); b.inputs['Roughness'].default_value=rough
    b.inputs['Metallic'].default_value=metal
    return m

def glass_mat():
    n=TAG+'_Freeman_ribbon_glass_blinds_var_UNVERIFIED'
    m=bpy.data.materials.get(n)
    if m: return m
    m=bpy.data.materials.new(n); m.use_nodes=True; nt=m.node_tree
    b=nt.nodes.get('Principled BSDF')
    b.inputs['Roughness'].default_value=0.08; b.inputs['Metallic'].default_value=0.0
    if 'IOR Level' in b.inputs: b.inputs['IOR Level'].default_value=0.3
    a=nt.nodes.new('ShaderNodeAttribute'); a.attribute_name='pane_var'; a.attribute_type='GEOMETRY'
    r=nt.nodes.new('ShaderNodeValToRGB'); cr=r.color_ramp
    cr.elements[0].position=0.25; cr.elements[0].color=(0.045,0.052,0.06,1)   # dark glass (room behind)
    cr.elements[1].position=1.0; cr.elements[1].color=(0.26,0.27,0.27,1)      # drawn blinds / pale curtain
    nt.links.new(a.outputs['Fac'],r.inputs['Fac']); nt.links.new(r.outputs['Color'],b.inputs['Base Color'])
    return m

def brick_mat():
    """modular buff brick in façade-plane coords (s along the long axis, z up) so courses stay level on both sides"""
    n=TAG+'_Freeman_cream_brick_modular_facadeplane_UNVERIFIED'
    m=bpy.data.materials.get(n)
    if m: return m
    m=bpy.data.materials.new(n); m.use_nodes=True; nt=m.node_tree; b=nt.nodes.get('Principled BSDF')
    u=(W_S-W_N).normalized()
    g=nt.nodes.new('ShaderNodeNewGeometry'); sp=nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(g.outputs['Position'],sp.inputs[0])
    m1=nt.nodes.new('ShaderNodeMath'); m1.operation='MULTIPLY'; m1.inputs[1].default_value=u.x; nt.links.new(sp.outputs[0],m1.inputs[0])
    m2=nt.nodes.new('ShaderNodeMath'); m2.operation='MULTIPLY_ADD'; m2.inputs[1].default_value=u.y; nt.links.new(sp.outputs[1],m2.inputs[0]); nt.links.new(m1.outputs[0],m2.inputs[2])
    cb=nt.nodes.new('ShaderNodeCombineXYZ'); nt.links.new(m2.outputs[0],cb.inputs[0]); nt.links.new(sp.outputs[2],cb.inputs[1])
    bt=nt.nodes.new('ShaderNodeTexBrick'); bt.inputs['Scale'].default_value=1.0
    bt.inputs['Brick Width'].default_value=0.203; bt.inputs['Row Height'].default_value=0.0677; bt.inputs['Mortar Size'].default_value=0.009
    bt.inputs['Color1'].default_value=(0.50,0.43,0.30,1); bt.inputs['Color2'].default_value=(0.57,0.49,0.34,1); bt.inputs['Mortar'].default_value=(0.57,0.55,0.49,1)
    bt.offset=0.5; nt.links.new(cb.outputs[0],bt.inputs['Vector'])
    nt.links.new(bt.outputs['Color'],b.inputs['Base Color']); b.inputs['Roughness'].default_value=0.88
    bm_=nt.nodes.new('ShaderNodeBump'); bm_.inputs['Strength'].default_value=0.25; bm_.inputs['Distance'].default_value=0.004
    nt.links.new(bt.outputs['Fac'],bm_.inputs['Height']); nt.links.new(bm_.outputs['Normal'],b.inputs['Normal'])
    return m

def materials():
    cream=brick_mat()
    red=mat(TAG+'_Freeman_spandrel_red_enamel_UNVERIFIED',(0.34,0.036,0.03),0.42)
    alu=mat(TAG+'_Freeman_mullion_alu_grey_UNVERIFIED',(0.55,0.56,0.57),0.35,0.6)
    return cream,red,alu,glass_mat()

def wall_plane(N,S,outside_sign,walls=None):
    """returns (origin N at façade plane, unit along N->S, outward normal); ray-casts the walls mesh if present"""
    u=(S-N).normalized(); n=Vector((u.y,-u.x))*outside_sign
    off=0.0
    if walls is not None:
        mw=walls.matrix_world; mi=mw.inverted(); hits=[]
        L=(S-N).length
        for f in (0.1,0.3,0.5,0.7,0.9):
            for z in (132.0,140.0):
                p=N+u*(L*f); o=Vector((p.x+n.x*6,p.y+n.y*6,z)); d=Vector((-n.x,-n.y,0))
                ok,loc,nor,idx=walls.ray_cast(mi@o,(mi.to_3x3()@d).normalized(),distance=20)
                if ok:
                    lw=mw@loc; hits.append((lw.xy-p).dot(n))
        if hits:
            hits.sort(); off=hits[len(hits)//2]   # median distance of real wall face from the OSM line (+ = outside)
            print('FACADE152 wall offset',round(off,3),'n_hits',len(hits),'range',round(hits[0],3),round(hits[-1],3))
    return N+n*off, u, n


def layout(L):
    """N->S spans along the façade: returns stair span, list of bay spans, pier width"""
    ncol=sum(BAYS); fixed=NCORNER+STAIR+NPIER+ncol*COL+SCORNER
    pier=(L-fixed)/(len(BAYS)-1)
    s=NCORNER; stair=(s,s+STAIR); s+=STAIR+NPIER; bays=[]
    for i,nc in enumerate(BAYS):
        if i>0: s+=pier
        bays.append((s,s+nc*COL,nc)); s+=nc*COL
    return stair,bays,pier

def build_side(name,N,S,outside_sign,walls,mats,rnd):
    cream,red,alu,glass=mats
    O,u,n=wall_plane(N,S,outside_sign,walls)
    L=(S-N).length
    stair,bays,pier=layout(L)
    print('FACADE152',name,'L',round(L,2),'pier',round(pier,2),'stair',stair,'bays',[(round(a,2),round(b,2),c) for a,b,c in bays])
    me=bpy.data.meshes.new(name); bm=bmesh.new()
    pv=bm.faces.layers.float.new('pane_var')
    def P(s,z,d): q=O+u*s+n*d; return bm.verts.new((q.x,q.y,z))
    def box(s0,s1,z0,z1,d0,d1,mi,var=0.0):
        v=[P(s0,z0,d0),P(s1,z0,d0),P(s1,z1,d0),P(s0,z1,d0),P(s0,z0,d1),P(s1,z0,d1),P(s1,z1,d1),P(s0,z1,d1)]
        cen=sum((x.co for x in v),Vector())/8
        for f in [(4,5,6,7),(0,4,7,3),(1,2,6,5),(3,7,6,2),(0,1,5,4)]:
            fc=bm.faces.new([v[i] for i in f]); fc.material_index=mi; fc[pv]=var
            fc.normal_update()
            if fc.normal.dot(fc.calc_center_median()-cen)<0: fc.normal_flip()
    zb,zt=Z_GRID_BOT,Z_GRID_TOP
    # cream solids between openings (outer surface PIER_OUT proud of the wall)
    solids=[(0.0,stair[0]),(stair[1],bays[0][0])]+[(bays[i][1],bays[i+1][0]) for i in range(len(bays)-1)]+[(bays[-1][1],L)]
    for a,b in solids: box(a,b,zb,zt,-0.02,PIER_OUT,0)
    pitch=(zt-Z_FLOOR0)/NFL; hsp=pitch*SPAN_FRAC
    def grid(a,b,ncol,stairlike=False):
        cw=(b-a)/ncol
        # sill/head returns (cream reveal) so the recess has depth
        box(a,b,zb,zt,-0.02,0.0,2)                       # back plate at the wall plane (closes any old punched slots)
        for k in range(ncol+1):                          # vertical mullions full height
            s=a+k*cw; box(s-MULL/2 if k else s,s+MULL/2 if k<ncol else s,zb,zt,0.0,GRID_OUT,2)
        rows=[(zb,Z_FLOOR0,'sp')]
        for f in range(NFL):
            z0=Z_FLOOR0+f*pitch
            if stairlike: rows.append((z0,z0+pitch,'gl'))
            else: rows+= [(z0,z0+hsp,'sp'),(z0+hsp,z0+pitch,'gl')]
        for z0,z1,kind in rows:
            if z1<zt-0.01: box(a,b,z1-MULL/2,z1+MULL/2,0.0,GRID_OUT,2)   # horizontal rail at each row top
            for k in range(ncol):
                s0=a+k*cw+MULL/2; s1=a+(k+1)*cw-MULL/2
                if kind=='sp': box(s0,s1,z0+MULL/2,z1-MULL/2,0.0,GRID_OUT-SPAN_IN,1)
                else:
                    zm=z0+(z1-z0)*0.52                     # operable lower sash / fixed upper light (crop: transom ~mid)
                    box(s0,s1,zm-0.02,zm+0.02,0.0,GRID_OUT-0.01,2)
                    box(s0,s1,z0+MULL/2,zm-0.02,0.0,GRID_OUT-GLASS_IN,3,rnd.random())
                    box(s0,s1,zm+0.02,z1-MULL/2,0.0,GRID_OUT-GLASS_IN,3,0.25+0.75*rnd.random())   # upper lights catch more sky
    # ground floor = first storey: spandrel below Z_FLOOR0 then windows; upper storeys spandrel + window
    grid(stair[0],stair[1],2,stairlike=True)
    for a,b,nc in bays: grid(a,b,nc)
    if name.find('_W_')>=0:
        # ground-floor details seen in BOTH photos (W side only; E unknown): white metal door in the last column of the 3rd 6-col bay,
        # dark door in the pier between the 3-col and 5-col bays (2007: exterior steps + rail falling S there — steps UNVERIFIED, not built),
        # a few window AC sleeves in lower sashes (2019 photo). Door sizes 0.95 x 2.15 m standard UNVERIFIED.
        a,b,nc=bays[3]; cw=(b-a)/nc; dz0=Z_FLOOR0
        box(b-cw+MULL/2,b-MULL/2,dz0-0.4,dz0+2.15,0.0,GRID_OUT+0.008,5)
        box(b-cw+0.3,b-0.3,dz0+1.3,dz0+1.95,GRID_OUT+0.008,GRID_OUT+0.012,3,0.1)        # vision lite
        sp=(bays[4][1]+bays[5][0])/2
        box(sp-0.48,sp+0.48,dz0-0.4,dz0+2.15,PIER_OUT,PIER_OUT+0.01,6)
        box(sp-0.62,sp+0.62,dz0+2.15,dz0+2.27,PIER_OUT,PIER_OUT+0.03,4)                # metal head flashing
        for bi,ci in [(2,1),(2,3),(1,4),(3,0),(5,2)]:
            a,b,nc=bays[bi]; cw=(b-a)/nc; s0=a+ci*cw+0.12; s1=s0+0.66
            z0=Z_FLOOR0+pitch*SPAN_FRAC+0.05
            box(s0,s1,z0,z0+0.42,GRID_OUT-0.03,GRID_OUT+0.12,4)                       # AC sleeve unit, beige-white
    # white metal fascia band at the roof edge (photos: white coping overhanging ~0.3 m)
    box(-0.3,L+0.3,zt,147.15,-0.02,0.32,4)
    bm.to_mesh(me); bm.free()
    extra=(bpy.data.materials.get(TAG+'_Freeman_fascia_white_metal_UNVERIFIED') or mat(TAG+'_Freeman_fascia_white_metal_UNVERIFIED',(0.85,0.86,0.86),0.3,0.3),
           mat(TAG+'_Freeman_door_white_metal_UNVERIFIED',(0.78,0.78,0.76),0.35,0.2),
           mat(TAG+'_Freeman_door_brown_metal_UNVERIFIED',(0.16,0.09,0.06),0.45,0.2))
    for m_ in mats+extra:
        me.materials.append(m_)
    ob=bpy.data.objects.new(name,me); return ob

RETIRE_KEEP=('_N_','N_entrance','lettering','Lettering','rail','globe','step','roof','Roof','walls','forecourt','concrete','curb','Lot9','CAM','parapet','RTU','Balance','dining','WS152','band','_S_')
def retire_old(walls_planes):
    out=[]
    for o in bpy.data.objects:
        if 'freeman' not in o.name.lower() or o.type!='MESH' or any(k in o.name for k in RETIRE_KEEP): continue
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        for O,u,n,L in walls_planes:
            d=[ (p.xy-O.xy).dot(n) for p in bb ]; s=[ (p.xy-O.xy).dot(u) for p in bb ]
            if min(d)>-1.0 and max(d)<1.6 and min(s)>-1.0 and max(s)<L+1.0 and max(p.z for p in bb)>129:
                out.append(o.name); o.hide_render=True; o.hide_viewport=True; o.name=o.name[:40]+'_RETIRED_ws152'; break
    print('FACADE152 retired',len(out),out[:40]); return out

def run(walls=None,coll_name=TAG+'_Freeman_facades_red_spandrel_bays_Commons2007_Montclarion2019_UNVERIFIED',do_retire=True):
    rnd=random.Random(152); mats=materials()
    col=bpy.data.collections.get(coll_name) or bpy.data.collections.new(coll_name)
    if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    obs=[]; planes=[]
    for nm,N,S,sg in [(TAG+'_Freeman_W_facade_spandrel_bays_UNVERIFIED',W_N,W_S,+1),(TAG+'_Freeman_E_facade_spandrel_bays_mirrorW_UNVERIFIED',E_N,E_S,-1)]:
        O,u,n=wall_plane(N,S,sg,walls); planes.append((O,u,n,(S-N).length))
        ob=build_side(nm,N,S,sg,walls,mats,rnd); col.objects.link(ob); obs.append(ob)
    if do_retire and walls is not None: retire_old(planes)
    return obs
