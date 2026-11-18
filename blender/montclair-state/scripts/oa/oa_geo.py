# oa geometry/material helpers (shared by oa_build.py and the asset kit script). Metres; local origin = floor centre, front faces +Y. UNVERIFIED generic kit.
import bpy, bmesh, mathutils, math, random
V=mathutils.Vector
def box(bm,x0,x1,y0,y1,z0,z1):
    r=bmesh.ops.create_cube(bm,size=1.0)
    for v in r['verts']: v.co=V(((x0+x1)/2+v.co.x*(x1-x0),(y0+y1)/2+v.co.y*(y1-y0),(z0+z1)/2+v.co.z*(z1-z0)))
def cyl(bm,c,r,z0,z1,seg=24):
    q=bmesh.ops.create_cone(bm,cap_ends=True,segments=seg,radius1=r,radius2=r,depth=z1-z0)
    for v in q['verts']: v.co=V((c[0]+v.co.x,c[1]+v.co.y,(z0+z1)/2+v.co.z))
def torus(bm,c,R,r,z,seg=32,rs=8):
    rings=[]
    for i in range(seg):
        a=2*math.pi*i/seg; ring=[]
        for j in range(rs):
            b=2*math.pi*j/rs; rr=R+r*math.cos(b)
            ring.append(bm.verts.new((c[0]+rr*math.cos(a),c[1]+rr*math.sin(a),z+r*math.sin(b))))
        rings.append(ring)
    for i in range(seg):
        for j in range(rs):
            a,b=rings[i],rings[(i+1)%seg]; bm.faces.new((a[j],b[j],b[(j+1)%rs],a[(j+1)%rs]))
def mesh(nm,bm,smooth=False):
    me=bpy.data.meshes.new(nm); bm.to_mesh(me); bm.free()
    if smooth:
        for p in me.polygons: p.use_smooth=True
    return me
def pm(n,c,r,metal=0.0,sheen=0.0,emit=None,es=0.0):
    m=bpy.data.materials.get(n)
    if m: return m
    m=bpy.data.materials.new(n); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*c,1); b.inputs['Roughness'].default_value=r; b.inputs['Metallic'].default_value=metal
    if sheen: b.inputs['Sheen Weight'].default_value=sheen
    if emit: b.inputs['Emission Color'].default_value=(*emit,1); b.inputs['Emission Strength'].default_value=es
    return m
def fabric(n,c,sheen=0.15):
    """woven upholstery: base colour with fine noise tweed + sheen"""
    m=bpy.data.materials.get(n)
    if m: return m
    m=pm(n,c,0.9,sheen=sheen); nt=m.node_tree; b=nt.nodes['Principled BSDF']
    tc=nt.nodes.new('ShaderNodeTexCoord'); nz=nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=420.0; nz.inputs['Detail'].default_value=2.0
    nt.links.new(tc.outputs['Object'],nz.inputs['Vector'])
    cr=nt.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color=(c[0]*0.72,c[1]*0.72,c[2]*0.72,1); cr.color_ramp.elements[1].color=(min(1,c[0]*1.18),min(1,c[1]*1.18),min(1,c[2]*1.18),1)
    nt.links.new(nz.outputs['Fac'],cr.inputs['Fac']); nt.links.new(cr.outputs['Color'],b.inputs['Base Color'])
    bp=nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.12; nt.links.new(nz.outputs['Fac'],bp.inputs['Height']); nt.links.new(bp.outputs['Normal'],b.inputs['Normal'])
    return m
def lounge_chair(seat_w=0.74):
    """club lounge chair (arms, loose seat cushion, 4 short metal legs). local floor z=0, front +Y. returns [(part,mesh,matkey)]"""
    w=seat_w/2+0.12; d=0.38; out=[]
    bm=bmesh.new(); box(bm,-w+0.115,w-0.115,-d+0.01,d-0.02,0.11,0.36); out.append(('base',mesh('OA lounge base',bm),'fab'))
    bm=bmesh.new(); box(bm,-w,-w+0.12,-d,d,0.11,0.62); box(bm,w-0.12,w,-d,d,0.11,0.62); out.append(('arms',mesh('OA lounge arms',bm),'fab'))
    bm=bmesh.new(); box(bm,-w+0.12,w-0.12,-d,-d+0.17,0.36,0.80); out.append(('back',mesh('OA lounge back',bm),'fab'))
    bm=bmesh.new(); box(bm,-w+0.125,w-0.125,-d+0.175,d-0.005,0.361,0.45); out.append(('seat cushion',mesh('OA lounge seat cushion',bm),'fab2'))
    bm=bmesh.new()
    for sx in (-1,1):
        for sy in (-1,1): cyl(bm,(sx*(w-0.06),sy*(d-0.06)),0.016,0.0,0.112,12)
    out.append(('legs',mesh('OA lounge legs',bm,True),'steel'))
    return out
def sofa(seat_w=1.6): return lounge_chair(seat_w)
def low_table(L=1.0,W=0.6,H=0.40):
    out=[]; bm=bmesh.new(); box(bm,-L/2,L/2,-W/2,W/2,H-0.03,H); out.append(('top',mesh('OA low table top',bm),'oak'))
    bm=bmesh.new()
    for sx in (-1,1):
        for sy in (-1,1): box(bm,sx*(L/2-0.05)-0.0125,sx*(L/2-0.05)+0.0125,sy*(W/2-0.05)-0.0125,sy*(W/2-0.05)+0.0125,0.0,H-0.0305)
    box(bm,-L/2+0.05,L/2-0.05,-0.01,0.01,0.12,0.14)   # stretcher
    out.append(('frame',mesh('OA low table frame',bm),'black'))
    return out
def bar_stool(h=0.76):
    out=[]; bm=bmesh.new(); cyl(bm,(0,0),0.19,h-0.05,h,32); out.append(('seat',mesh('OA stool seat',bm,True),'seat'))
    bm=bmesh.new(); cyl(bm,(0,0),0.024,0.025,h-0.049,16); cyl(bm,(0,0),0.21,0.0,0.026,32); torus(bm,(0,0),0.17,0.011,0.30)
    out.append(('base',mesh('OA stool base',bm,True),'steel'))
    bm=bmesh.new()
    for k in range(3):   # footring spokes
        a=2*math.pi*k/3+0.5; ca,sa=math.cos(a),math.sin(a)
        r0,r1=0.02,0.165
        q=bmesh.ops.create_cube(bm,size=1.0)
        for v in q['verts']:
            lx=(r0+r1)/2+v.co.x*(r1-r0); ly=v.co.y*0.012; lz=0.30+v.co.z*0.012
            v.co=V((lx*ca-ly*sa,lx*sa+ly*ca,lz))
    out.append(('spokes',mesh('OA stool spokes',bm),'steel'))
    return out
def counter(x0,x1,y0,y1,ztop,legs):
    """wall study counter: 30 mm top, steel legs, modesty panel, flush power/USB modules"""
    out=[]; bm=bmesh.new(); box(bm,x0,x1,y0,y1,ztop-0.03,ztop); out.append(('top',mesh('OA counter top',bm),'oak'))
    bm=bmesh.new()
    for lx in legs: box(bm,lx-0.025,lx+0.025,y0+0.06,y0+0.11,ztop-1.07+0.0,ztop-0.031)
    for lx in legs: box(bm,lx-0.025,lx+0.025,y0+0.06,y1-0.02,ztop-0.07,ztop-0.031)   # top rails
    out.append(('legs',mesh('OA counter legs',bm),'black'))
    bm=bmesh.new(); box(bm,x0+0.05,x1-0.05,y1-0.04,y1-0.022,ztop-0.42,ztop-0.031); out.append(('modesty',mesh('OA counter modesty panel',bm),'black'))
    return out
def power_modules(xs,yc,ztop):
    bm=bmesh.new(); dk=bmesh.new()
    for x in xs:
        box(bm,x-0.08,x+0.08,yc-0.03,yc+0.03,ztop-0.004,ztop+0.002)
        for u in (-0.045,-0.015): box(dk,x+u-0.009,x+u+0.009,yc-0.012,yc+0.012,ztop+0.0015,ztop+0.0025)   # outlet faces
        for u in (0.025,0.05): box(dk,x+u-0.005,x+u+0.005,yc-0.003,yc+0.003,ztop+0.0015,ztop+0.0025)      # USB-A/C
    return [('power modules',mesh('OA counter power modules',bm),'alu'),('power ports',mesh('OA counter power ports',dk),'black')]
def rug(x0,x1,y0,y1,z):
    bm=bmesh.new(); box(bm,x0,x1,y0,y1,z,z+0.008); return [('rug',mesh('OA area rug',bm),'rug')]
def rug_material(n):
    m=bpy.data.materials.get(n)
    if m: return m
    m=pm(n,(0.12,0.13,0.15),0.95); nt=m.node_tree; b=nt.nodes['Principled BSDF']
    tc=nt.nodes.new('ShaderNodeTexCoord'); w=nt.nodes.new('ShaderNodeTexWave'); w.inputs['Scale'].default_value=60.0; w.inputs['Distortion'].default_value=1.5
    nt.links.new(tc.outputs['Object'],w.inputs['Vector'])
    nz=nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=300.0; nt.links.new(tc.outputs['Object'],nz.inputs['Vector'])
    mx=nt.nodes.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.inputs['Factor'].default_value=0.5
    nt.links.new(w.outputs['Fac'],mx.inputs['A']); nt.links.new(nz.outputs['Fac'],mx.inputs['B'])
    cr=nt.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color=(0.07,0.08,0.10,1); cr.color_ramp.elements[1].color=(0.21,0.22,0.25,1)
    nt.links.new(mx.outputs['Result'],cr.inputs['Fac']); nt.links.new(cr.outputs['Color'],b.inputs['Base Color'])
    return m
def display(xc,yw,zb,W=1.24,H=0.71,ny=1):
    """wall-mounted signage display on a wall plane y=yw facing +y (ny=1) or -y"""
    s=ny; out=[]
    bm=bmesh.new(); y0,y1=sorted((yw+s*0.012,yw+s*0.050)); box(bm,xc-W/2,xc+W/2,y0,y1,zb,zb+H); out.append(('bezel',mesh('OA display bezel',bm),'black'))
    bm=bmesh.new(); y0,y1=sorted((yw+s*0.0505,yw+s*0.0515)); box(bm,xc-W/2+0.012,xc+W/2-0.012,y0,y1,zb+0.012,zb+H-0.012); out.append(('screen',mesh('OA display screen',bm),'screen'))
    bm=bmesh.new(); y0,y1=sorted((yw-s*0.002,yw+s*0.0125)); box(bm,xc-0.2,xc+0.2,y0,y1,zb+0.15,zb+H-0.15); out.append(('mount',mesh('OA display wall mount',bm),'black'))
    return out
def screen_material(n):
    m=bpy.data.materials.get(n)
    if m: return m
    m=bpy.data.materials.new(n); m.use_nodes=True; nt=m.node_tree; nd=nt.nodes; b=nd['Principled BSDF']
    b.inputs['Base Color'].default_value=(0.01,0.01,0.012,1); b.inputs['Roughness'].default_value=0.12
    tc=nd.new('ShaderNodeTexCoord'); sp=nd.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Generated'],sp.inputs[0])
    # generic event-slide layout: red header band, white title bars, photo block (UNVERIFIED content)
    cr=nd.new('ShaderNodeValToRGB'); cr.color_ramp.interpolation='CONSTANT'
    e=cr.color_ramp.elements; e[0].position=0.0; e[0].color=(0.92,0.92,0.93,1); e[1].position=0.80; e[1].color=(0.55,0.02,0.05,1)
    nt.links.new(sp.outputs['Z'],cr.inputs['Fac'])
    nz=nd.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=4.0; nt.links.new(tc.outputs['Generated'],nz.inputs['Vector'])
    ph=nd.new('ShaderNodeValToRGB'); ph.color_ramp.elements[0].color=(0.08,0.12,0.2,1); ph.color_ramp.elements[1].color=(0.55,0.45,0.35,1); nt.links.new(nz.outputs['Fac'],ph.inputs['Fac'])
    def M(op,a,vb):
        q=nd.new('ShaderNodeMath'); q.operation=op; nt.links.new(a,q.inputs[0]); q.inputs[1].default_value=vb; return q.outputs[0]
    def mul(a,b):
        q=nd.new('ShaderNodeMath'); q.operation='MULTIPLY'; nt.links.new(a,q.inputs[0]); nt.links.new(b,q.inputs[1]); return q.outputs[0]
    photo=mul(mul(M('GREATER_THAN',sp.outputs['X'],0.55),M('LESS_THAN',sp.outputs['X'],0.94)),mul(M('GREATER_THAN',sp.outputs['Z'],0.12),M('LESS_THAN',sp.outputs['Z'],0.72)))
    m1=nd.new('ShaderNodeMix'); m1.data_type='RGBA'; nt.links.new(photo,m1.inputs['Factor']); nt.links.new(cr.outputs['Color'],m1.inputs['A']); nt.links.new(ph.outputs['Color'],m1.inputs['B'])
    # text bars on the left (dark grey lines)
    lines=mul(mul(M('LESS_THAN',sp.outputs['X'],0.48),M('GREATER_THAN',sp.outputs['X'],0.06)),mul(M('GREATER_THAN',M('FRACT',M('MULTIPLY',sp.outputs['Z'],14.0),1.0),0.62),mul(M('GREATER_THAN',sp.outputs['Z'],0.15),M('LESS_THAN',sp.outputs['Z'],0.70))))
    m2=nd.new('ShaderNodeMix'); m2.data_type='RGBA'; nt.links.new(lines,m2.inputs['Factor']); nt.links.new(m1.outputs['Result'],m2.inputs['A']); m2.inputs['B'].default_value=(0.25,0.25,0.27,1)
    nt.links.new(m2.outputs['Result'],b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value=1.2
    return m
def tackboard(x0,x1,yw,z0,z1,ny=1,seed=7):
    """cork tack board with aluminium frame and pinned flyers on wall plane y=yw facing +y"""
    s=ny; out=[]; Y=lambda a,b: sorted((yw+s*a,yw+s*b))
    bm=bmesh.new(); y0,y1=Y(-0.002,0.012); box(bm,x0+0.02,x1-0.02,y0,y1,z0+0.02,z1-0.02); out.append(('cork',mesh('OA tack board cork',bm),'cork'))
    bm=bmesh.new(); y0,y1=Y(-0.002,0.018)
    box(bm,x0,x1,y0,y1,z1-0.02,z1); box(bm,x0,x1,y0,y1,z0,z0+0.02); box(bm,x0,x0+0.02,y0,y1,z0+0.02,z1-0.02); box(bm,x1-0.02,x1,y0,y1,z0+0.02,z1-0.02)
    out.append(('frame',mesh('OA tack board frame',bm),'alu'))
    rnd=random.Random(seed); fl={k:bmesh.new() for k in ('pw','py','pb','pr','pg')}; pins=bmesh.new(); placed=[]
    sizes=[(0.216,0.279),(0.279,0.216),(0.14,0.216),(0.216,0.279),(0.1,0.15),(0.216,0.279),(0.28,0.43)]
    for k in range(40):
        if len(placed)>=13: break
        w,h=rnd.choice(sizes); cx=rnd.uniform(x0+0.05+w/2,x1-0.05-w/2); cz=rnd.uniform(z0+0.05+h/2,z1-0.05-h/2)
        if sum(1 for (a,b,c,d) in placed if abs(cx-a)<(w+c)/2*0.75 and abs(cz-b)<(h+d)/2*0.75)>0: continue
        placed.append((cx,cz,w,h)); kk=rnd.choice(['pw','pw','pw','py','pb','pr','pg']); d=0.0125+0.0004*len(placed)
        y0,y1=Y(d,d+0.0006); box(fl[kk],cx-w/2,cx+w/2,y0,y1,cz-h/2,cz+h/2)
        y0,y1=Y(d+0.0006,d+0.006); cyl_y=bmesh.ops.create_cone(pins,cap_ends=True,segments=10,radius1=0.0045,radius2=0.0045,depth=y1-y0)
        for v in cyl_y['verts']: v.co=V((cx+v.co.x,(y0+y1)/2+v.co.z,cz+h/2-0.02+v.co.y))
    for k,b in fl.items(): out.append(('flyers '+k,mesh('OA tack board flyers '+k,b),k))
    out.append(('pins',mesh('OA tack board pins',pins,True),'pin'))
    return out
def laptop(c,rot=0.0,open_deg=110):
    """open 14 in laptop, base on z=c[2], hinge toward -y in local space; returned meshes are in local space (place with loc/rot)"""
    out=[]; bm=bmesh.new(); box(bm,-0.16,0.16,-0.11,0.11,0.0,0.016); out.append(('base',mesh('OA laptop base',bm),'alu'))
    bm=bmesh.new(); a=math.radians(open_deg-90)
    q=bmesh.ops.create_cube(bm,size=1.0)
    for v in q['verts']:
        lx=v.co.x*0.32; ly=v.co.y*0.006-0.003; lz=(v.co.z+0.5)*0.215
        v.co=V((lx,-0.108+ly*math.cos(a)-lz*math.sin(a),0.016+ly*math.sin(a)+lz*math.cos(a)))
    out.append(('lid',mesh('OA laptop lid',bm),'alu'))
    bm=bmesh.new(); q=bmesh.ops.create_cube(bm,size=1.0)
    for v in q['verts']:
        lx=v.co.x*0.29; ly=v.co.y*0.001+0.0012; lz=0.012+(v.co.z+0.5)*0.185
        v.co=V((lx,-0.108+ly*math.cos(a)-lz*math.sin(a),0.016+ly*math.sin(a)+lz*math.cos(a)))
    out.append(('screen',mesh('OA laptop screen',bm),'lscreen'))
    bm=bmesh.new(); box(bm,-0.13,0.13,-0.08,0.0,0.0155,0.0175); out.append(('keys',mesh('OA laptop keyboard',bm),'black'))
    return out
def cup(h=0.11):
    bm=bmesh.new(); q=bmesh.ops.create_cone(bm,cap_ends=True,segments=24,radius1=0.028,radius2=0.04,depth=h)
    for v in q['verts']: v.co.z+=h/2
    out=[('cup',mesh('OA paper cup',bm,True),'cupw')]
    bm=bmesh.new(); cyl(bm,(0,0),0.042,h,h+0.012,24); out.append(('lid',mesh('OA paper cup lid',bm,True),'black'))
    bm=bmesh.new(); q=bmesh.ops.create_cone(bm,cap_ends=True,segments=24,radius1=0.0335,radius2=0.0375,depth=0.045)
    for v in q['verts']: v.co.z+=0.06
    out.append(('sleeve',mesh('OA paper cup sleeve',bm,True),'kraft'))
    return out
def backpack():
    bm=bmesh.new(); box(bm,-0.15,0.15,-0.09,0.09,0.0,0.44); out=[('body',mesh('OA backpack body',bm),'pack')]
    bm=bmesh.new(); box(bm,-0.12,0.12,0.09,0.15,0.03,0.25); out.append(('pocket',mesh('OA backpack front pocket',bm),'pack2'))
    bm=bmesh.new(); torus(bm,(0,0),0.04,0.008,0.0,16,6)
    for v in bm.verts: v.co=V((v.co.x,v.co.z-0.085,0.45+v.co.y))
    out.append(('handle',mesh('OA backpack top handle',bm,True),'pack2'))
    return out
def poster_frame(xc,yw,z0,W,H,ny=-1):
    """framed print on wall plane y=yw facing -y (ny=-1): black 25 mm frame, white mat, print inset"""
    s=ny; Y=lambda a,b: sorted((yw+s*a,yw+s*b)); out=[]
    bm=bmesh.new(); y0,y1=Y(-0.002,0.03); x0,x1,z1=xc-W/2,xc+W/2,z0+H; t=0.025
    box(bm,x0,x1,y0,y1,z1-t,z1); box(bm,x0,x1,y0,y1,z0,z0+t); box(bm,x0,x0+t,y0,y1,z0+t,z1-t); box(bm,x1-t,x1,y0,y1,z0+t,z1-t)
    out.append(('frame',mesh('OA poster frame',bm),'black'))
    bm=bmesh.new(); y0,y1=Y(-0.002,0.012); box(bm,x0+t,x1-t,y0,y1,z0+t,z1-t); out.append(('mat',mesh('OA poster mat',bm),'mat'))
    bm=bmesh.new(); y0,y1=Y(0.012,0.0125); m=0.07; box(bm,x0+t+m,x1-t-m,y0,y1,z0+t+m,z1-t-m); out.append(('print',mesh('OA poster print',bm),'print'))
    return out
def print_material(n,seed,tint):
    """generic framed print: high-contrast photo-like image block (upper 72 %) over a white caption band with dark text bars"""
    m=bpy.data.materials.get(n)
    if m: return m
    m=pm(n,(0.5,0.5,0.5),0.5); nt=m.node_tree; nd=nt.nodes; b=nd['Principled BSDF']; L=nt.links.new
    tc=nd.new('ShaderNodeTexCoord'); sp=nd.new('ShaderNodeSeparateXYZ'); L(tc.outputs['Generated'],sp.inputs[0])
    nz=nd.new('ShaderNodeTexNoise'); nz.noise_dimensions='4D'; nz.inputs['W'].default_value=seed
    nz.inputs['Scale'].default_value=3.5; nz.inputs['Detail'].default_value=8.0; nz.inputs['Roughness'].default_value=0.62; L(tc.outputs['Generated'],nz.inputs['Vector'])
    cr=nd.new('ShaderNodeValToRGB'); e=cr.color_ramp.elements; e[0].position=0.40; e[0].color=(0.02,0.02,0.03,1); e[1].position=0.62; e[1].color=(*tint,1)
    e2=cr.color_ramp.elements.new(0.52); e2.color=(tint[0]*0.35,tint[1]*0.35,tint[2]*0.4,1)
    L(nz.outputs['Fac'],cr.inputs['Fac'])
    def M(op,a,vb):
        q=nd.new('ShaderNodeMath'); q.operation=op; L(a,q.inputs[0]); q.inputs[1].default_value=vb; return q.outputs[0]
    def mul(a,c):
        q=nd.new('ShaderNodeMath'); q.operation='MULTIPLY'; L(a,q.inputs[0]); L(c,q.inputs[1]); return q.outputs[0]
    cap=M('LESS_THAN',sp.outputs['Z'],0.27)
    m1=nd.new('ShaderNodeMix'); m1.data_type='RGBA'; L(cap,m1.inputs['Factor']); L(cr.outputs['Color'],m1.inputs['A']); m1.inputs['B'].default_value=(0.85,0.85,0.83,1)
    txt=mul(mul(cap,M('GREATER_THAN',M('FRACT',M('MULTIPLY',sp.outputs['Z'],22.0),1.0),0.55)),mul(M('GREATER_THAN',sp.outputs['X'],0.08),mul(M('LESS_THAN',sp.outputs['Z'],0.22),M('LESS_THAN',sp.outputs['X'],0.72))))
    m2=nd.new('ShaderNodeMix'); m2.data_type='RGBA'; L(txt,m2.inputs['Factor']); L(m1.outputs['Result'],m2.inputs['A']); m2.inputs['B'].default_value=(0.12,0.12,0.13,1)
    L(m2.outputs['Result'],b.inputs['Base Color'])
    return m
def floor_box(c,z):
    """flush floor power/data box: stainless cover ring + carpet-insert lid with two flip doors"""
    bm=bmesh.new(); box(bm,c[0]-0.13,c[0]+0.13,c[1]-0.13,c[1]+0.13,z-0.004,z+0.003); out=[('ring',mesh('OA floor box ring',bm),'steel')]
    bm=bmesh.new(); box(bm,c[0]-0.11,c[0]+0.11,c[1]-0.11,c[1]+0.11,z+0.003,z+0.004); out.append(('lid',mesh('OA floor box lid',bm),'black'))
    bm=bmesh.new()
    for dx in (-0.055,0.055): box(bm,c[0]+dx-0.04,c[0]+dx+0.04,c[1]-0.07,c[1]+0.07,z+0.004,z+0.0048)
    out.append(('doors',mesh('OA floor box flip doors',bm),'alu'))
    return out
def mats(P):
    return {'fab':fabric(P+'_lounge_fabric_charcoal_UNVERIFIED',(0.022,0.023,0.027)),
            'fab2':fabric(P+'_lounge_cushion_charcoal_UNVERIFIED',(0.027,0.028,0.033)),
            'fabR':fabric(P+'_lounge_fabric_crimson_UNVERIFIED',(0.32,0.03,0.04)),
            'fabR2':fabric(P+'_lounge_cushion_crimson_UNVERIFIED',(0.35,0.035,0.045)),
            'steel':pm(P+'_brushed_steel_UNVERIFIED',(0.6,0.6,0.6),0.32,1.0),
            'black':pm(P+'_black_powdercoat_UNVERIFIED',(0.02,0.02,0.022),0.45,0.3),
            'oak':pm(P+'_white_oak_laminate_UNVERIFIED',(0.52,0.38,0.24),0.45),
            'seat':pm(P+'_stool_seat_black_UNVERIFIED',(0.025,0.025,0.027),0.5),
            'alu':pm(P+'_anodised_aluminium_UNVERIFIED',(0.7,0.7,0.71),0.35,1.0),
            'rug':rug_material(P+'_area_rug_grey_loop_UNVERIFIED'),
            'screen':screen_material(P+'_signage_screen_event_slide_UNVERIFIED'),
            'cork':pm(P+'_cork_UNVERIFIED',(0.45,0.3,0.17),0.9),
            'pw':pm(P+'_flyer_white_UNVERIFIED',(0.85,0.85,0.83),0.7),'py':pm(P+'_flyer_yellow_UNVERIFIED',(0.85,0.75,0.25),0.7),
            'pb':pm(P+'_flyer_blue_UNVERIFIED',(0.25,0.45,0.75),0.7),'pr':pm(P+'_flyer_red_UNVERIFIED',(0.7,0.08,0.1),0.7),
            'lscreen':pm(P+'_laptop_screen_UNVERIFIED',(0.02,0.02,0.03),0.1,emit=(0.55,0.62,0.75),es=0.6),'cupw':pm(P+'_paper_cup_white_UNVERIFIED',(0.85,0.84,0.8),0.6),'kraft':pm(P+'_cup_sleeve_kraft_UNVERIFIED',(0.45,0.3,0.17),0.8),'pack':fabric(P+'_backpack_navy_UNVERIFIED',(0.03,0.05,0.12)),'pack2':fabric(P+'_backpack_trim_grey_UNVERIFIED',(0.12,0.12,0.13)),
            'mat':pm(P+'_poster_mat_white_UNVERIFIED',(0.86,0.86,0.84),0.8),'p1':print_material(P+'_poster_print_1_UNVERIFIED',1.3,(0.75,0.15,0.12)),'p2':print_material(P+'_poster_print_2_UNVERIFIED',4.7,(0.55,0.62,0.7)),'p3':print_material(P+'_poster_print_3_UNVERIFIED',8.1,(0.85,0.7,0.45)),
            'pg':pm(P+'_flyer_green_UNVERIFIED',(0.35,0.65,0.35),0.7),'pin':pm(P+'_push_pin_red_UNVERIFIED',(0.6,0.03,0.03),0.3)}
