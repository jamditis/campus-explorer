# nz geometry/material helpers (shared by nz_build.py and the asset kit script). All dims in metres. UNVERIFIED generic kit.
import bpy, bmesh, mathutils, math
V=mathutils.Vector
def box(bm,x0,x1,y0,y1,z0,z1):
    r=bmesh.ops.create_cube(bm,size=1.0)
    for v in r['verts']: v.co=V(((x0+x1)/2+v.co.x*(x1-x0),(y0+y1)/2+v.co.y*(y1-y0),(z0+z1)/2+v.co.z*(z1-z0)))
def cyl(bm,c,r,axis,d0,d1,seg=24):
    q=bmesh.ops.create_cone(bm,cap_ends=True,segments=seg,radius1=r,radius2=r,depth=d1-d0); m=(d0+d1)/2
    for v in q['verts']:
        a,b,h=v.co.x,v.co.y,v.co.z
        if axis=='z': v.co=V((c[0]+a,c[1]+b,m+h))
        elif axis=='y': v.co=V((c[0]+a,m+h,c[1]+b))
        else: v.co=V((m+h,c[0]+a,c[1]+b))
def mesh(nm,bm,smooth=False):
    me=bpy.data.meshes.new(nm); bm.to_mesh(me); bm.free()
    if smooth:
        for p in me.polygons: p.use_smooth=True
    return me
def pm(n,c,r,metal=0.0,coat=0.0):
    m=bpy.data.materials.get(n)
    if m: return m
    m=bpy.data.materials.new(n); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*c,1); b.inputs['Roughness'].default_value=r; b.inputs['Metallic'].default_value=metal
    if coat: b.inputs['Coat Weight'].default_value=coat
    return m
def projector(o):
    """ceiling projector on a drop pole; o=(x,y,ztop_ceiling). lens faces +y. returns list of (name,mesh,matname)"""
    x,y,zc=o; out=[]
    bm=bmesh.new(); box(bm,x-0.165,x+0.165,y-0.135,y+0.135,zc-0.51,zc-0.401); out.append(('body',mesh('NZ projector body',bm),'body'))
    bm=bmesh.new(); cyl(bm,(x+0.075,zc-0.455),0.038,'y',y+0.13,y+0.152,32); cyl(bm,(x+0.075,zc-0.455),0.044,'y',y+0.128,y+0.137,32)
    out.append(('lens barrel',mesh('NZ projector lens barrel',bm,True),'dark'))
    bm=bmesh.new(); cyl(bm,(x+0.075,zc-0.455),0.029,'y',y+0.150,y+0.154,32); out.append(('lens glass',mesh('NZ projector lens glass',bm,True),'glass'))
    bm=bmesh.new()
    for k in range(7): box(bm,x+0.1645,x+0.1665,y-0.10+k*0.022,y-0.088+k*0.022,zc-0.49,zc-0.42)    # side vent slots
    for k in range(5): box(bm,x-0.12+k*0.03,x-0.105+k*0.03,y+0.1345,y+0.1365,zc-0.495,zc-0.475)   # front intake grille
    out.append(('vents',mesh('NZ projector vents',bm),'dark'))
    bm=bmesh.new(); cyl(bm,(x,y),0.07,'z',zc-0.016,zc-0.004,32); cyl(bm,(x,y),0.019,'z',zc-0.39,zc-0.015,20)
    box(bm,x-0.115,x+0.115,y-0.09,y+0.09,zc-0.4005+0.0005,zc-0.388)   # spider bracket
    for sx in (-1,1):
        for sy in (-1,1): cyl(bm,(x+sx*0.1,y+sy*0.075),0.006,'z',zc-0.408,zc-0.387,10)  # bracket feet screws into body top
    out.append(('mount',mesh('NZ projector ceiling mount',bm,True),'mount'))
    bm=bmesh.new(); cyl(bm,(x+0.03,y-0.115),0.006,'z',zc-0.405,zc-0.006,10)
    out.append(('cables',mesh('NZ projector cable drop',bm,True),'cable'))
    bm=bmesh.new(); cyl(bm,(x-0.13,zc-0.42),0.0025,'y',y+0.134,y+0.1375,10); out.append(('status led',mesh('NZ projector status LED',bm,True),'led'))
    return out
def screen_case(x0,x1,yc,ztop):
    out=[]; bm=bmesh.new(); box(bm,x0+0.02,x1-0.02,yc-0.055,yc+0.055,ztop-0.105,ztop-0.002); out.append(('case',mesh('NZ screen case',bm),'case'))
    bm=bmesh.new(); box(bm,x0,x0+0.025,yc-0.06,yc+0.06,ztop-0.11,ztop-0.001); box(bm,x1-0.025,x1,yc-0.06,yc+0.06,ztop-0.11,ztop-0.001)
    out.append(('end caps',mesh('NZ screen end caps',bm),'mount'))
    bm=bmesh.new(); box(bm,x0+0.07,x1-0.07,yc-0.008,yc+0.008,ztop-0.125,ztop-0.106)   # hem bar
    xm=(x0+x1)/2; box(bm,xm-0.0015,xm+0.0015,yc-0.0015,yc+0.0015,ztop-0.20,ztop-0.124)  # pull cord
    box(bm,xm-0.02,xm+0.02,yc-0.006,yc+0.006,ztop-0.228,ztop-0.199)   # pull handle
    out.append(('hem bar and pull',mesh('NZ screen hem bar and pull',bm),'dark'))
    bm=bmesh.new(); box(bm,x0+0.07,x1-0.07,yc-0.0025,yc+0.0025,ztop-0.107,ztop-0.104)   # sliver of white fabric at the slot
    out.append(('fabric',mesh('NZ screen fabric sliver',bm),'fabric'))
    return out
def wall_plate(kind,c,n):
    """kind 'duplex'|'switch'|'av'; c=(x,y,z) centre on the wall plane; n=+x/-x/+y/-y unit normal into the room"""
    out=[]; nx,ny=n
    def wbox(bm,u0,u1,d0,d1,z0,z1):   # u = along-wall offset, d = depth off wall
        if nx: box(bm,c[0]+nx*d0 if nx>0 else c[0]-d1,c[0]+nx*d1 if nx>0 else c[0]-d0,c[1]+u0,c[1]+u1,c[2]+z0,c[2]+z1)
        else: box(bm,c[0]+u0,c[0]+u1,c[1]+ny*d0 if ny>0 else c[1]-d1,c[1]+ny*d1 if ny>0 else c[1]-d0,c[2]+z0,c[2]+z1)
    bm=bmesh.new(); wbox(bm,-0.035,0.035,-0.002,0.006,-0.0575,0.0575); out.append(('plate',mesh('NZ wall plate '+kind,bm),'plate'))
    bm=bmesh.new(); dk=bmesh.new()
    if kind=='duplex':
        for zc in (-0.021,0.021):
            wbox(bm,-0.017,0.017,0.005,0.009,zc-0.0165,zc+0.0165)
            for u in (-0.0063,0.0063): wbox(dk,u-0.0012,u+0.0012,0.0085,0.0095,zc-0.002,zc+0.008)
            wbox(dk,-0.002,0.002,0.0085,0.0095,zc-0.011,zc-0.007)
    elif kind=='switch':
        wbox(bm,-0.0165,0.0165,0.005,0.011,-0.033,0.033); wbox(dk,-0.0165,0.0165,0.0105,0.0112,-0.0005,0.0005)
    else:
        wbox(bm,-0.017,0.017,0.005,0.008,-0.04,0.04)
        wbox(dk,-0.008,0.008,0.0075,0.0085,0.012,0.018); wbox(dk,-0.011,0.011,0.0075,0.0085,-0.012,-0.004); wbox(dk,-0.005,0.005,0.0075,0.0085,-0.032,-0.024)
    out.append(('insert',mesh('NZ wall plate insert '+kind,bm),'plate2')); out.append(('slots',mesh('NZ wall plate slots '+kind,dk),'dark'))
    return out
def mats(P):
    return {'body':pm(P+'_projector_body_light_grey_UNVERIFIED',(0.80,0.80,0.79),0.42),
            'dark':pm(P+'_av_black_plastic_UNVERIFIED',(0.015,0.015,0.016),0.55),
            'glass':pm(P+'_projector_lens_glass_UNVERIFIED',(0.02,0.03,0.05),0.04,0.0,1.0),
            'mount':pm(P+'_mount_black_powdercoat_UNVERIFIED',(0.03,0.03,0.032),0.38,0.6),
            'cable':pm(P+'_cable_white_UNVERIFIED',(0.75,0.75,0.74),0.5),
            'led':pm(P+'_status_led_UNVERIFIED',(0.05,0.6,0.15),0.3),
            'case':pm(P+'_screen_case_white_aluminium_UNVERIFIED',(0.86,0.86,0.85),0.3,0.2),
            'fabric':pm(P+'_screen_fabric_matte_white_UNVERIFIED',(0.9,0.9,0.9),0.85),
            'plate':pm(P+'_wall_plate_white_UNVERIFIED',(0.82,0.81,0.78),0.35),
            'plate2':pm(P+'_wall_plate_insert_UNVERIFIED',(0.78,0.77,0.74),0.3)}
def ghost_material(n,strength=0.38):
    m=bpy.data.materials.get(n)
    if m: return m
    m=bpy.data.materials.new(n); m.use_nodes=True; nt=m.node_tree; nd=nt.nodes; lk=nt.links
    for x in list(nd): nd.remove(x)
    def N(t,**k):
        q=nd.new(t)
        for a,b in k.items(): setattr(q,a,b)
        return q
    def M(op,a=None,b=None,va=0.0,vb=0.0):
        q=N('ShaderNodeMath',operation=op); q.inputs[0].default_value=va; q.inputs[1].default_value=vb
        if a is not None: lk.new(a,q.inputs[0])
        if b is not None: lk.new(b,q.inputs[1])
        return q.outputs[0]
    out=N('ShaderNodeOutputMaterial'); mix=N('ShaderNodeMixShader'); tr=N('ShaderNodeBsdfTransparent')
    df=N('ShaderNodeBsdfPrincipled'); df.inputs['Base Color'].default_value=(0.42,0.44,0.5,1); df.inputs['Roughness'].default_value=0.55
    tc=N('ShaderNodeTexCoord'); sp=N('ShaderNodeSeparateXYZ'); lk.new(tc.outputs['Object'],sp.inputs[0])
    X,Z=sp.outputs['X'],sp.outputs['Z']
    LH=0.085                                              # handwriting line pitch
    row=M('FLOOR',M('DIVIDE',Z,None,vb=LH)); fr=M('FRACT',M('DIVIDE',Z,None,vb=LH))
    jn=N('ShaderNodeTexNoise'); jn.inputs['Scale'].default_value=28.0; jn.inputs['Detail'].default_value=2.0; lk.new(tc.outputs['Object'],jn.inputs['Vector'])
    fr=M('ADD',fr,M('MULTIPLY',M('SUBTRACT',jn.outputs['Fac'],None,vb=0.5),None,vb=0.6))      # ragged letter tops/bottoms (ascenders)
    band=M('MULTIPLY',M('GREATER_THAN',fr,None,vb=0.22),M('LESS_THAN',fr,None,vb=0.74))     # x-height band of each line
    cb=N('ShaderNodeCombineXYZ'); lk.new(M('MULTIPLY',X,None,vb=3.2),cb.inputs[0]); lk.new(M('MULTIPLY',row,None,vb=1.37),cb.inputs[1])
    wn=N('ShaderNodeTexNoise'); wn.inputs['Scale'].default_value=1.0; wn.inputs['Detail'].default_value=1.0; lk.new(cb.outputs[0],wn.inputs['Vector'])
    words=M('MINIMUM',M('MAXIMUM',M('MULTIPLY',M('SUBTRACT',wn.outputs['Fac'],None,vb=0.47),None,vb=12.0),None,vb=0.0),None,vb=1.0)   # soft word runs
    blk=N('ShaderNodeTexNoise'); blk.inputs['Scale'].default_value=0.9; blk.inputs['Detail'].default_value=0.0; lk.new(tc.outputs['Object'],blk.inputs['Vector'])
    region=M('GREATER_THAN',blk.outputs['Fac'],None,vb=0.47)                                  # erased blocks of old notes, gaps between
    wv=N('ShaderNodeTexWave',wave_type='BANDS',bands_direction='DIAGONAL'); wv.inputs['Scale'].default_value=55.0
    wv.inputs['Distortion'].default_value=18.0; wv.inputs['Detail'].default_value=3.0; wv.inputs['Detail Scale'].default_value=1.6
    lk.new(tc.outputs['Object'],wv.inputs['Vector'])
    stroke=M('GREATER_THAN',wv.outputs['Fac'],None,vb=0.80)                                   # thin scribbly pen strokes
    sm=N('ShaderNodeTexNoise'); sm.inputs['Scale'].default_value=3.0; sm.inputs['Detail'].default_value=4.0; lk.new(tc.outputs['Object'],sm.inputs['Vector'])
    fade=M('MULTIPLY',sm.outputs['Fac'],None,vb=1.4)                                           # uneven erasing
    ink=M('MULTIPLY',M('MULTIPLY',M('MULTIPLY',band,words),M('MULTIPLY',region,stroke)),fade)
    ink=M('MULTIPLY',ink,None,vb=strength)
    mp=N('ShaderNodeMapping'); mp.inputs['Scale'].default_value=(1.0,9.0,1.0); lk.new(tc.outputs['Object'],mp.inputs['Vector'])
    sw=N('ShaderNodeTexNoise'); sw.inputs['Scale'].default_value=5.0; sw.inputs['Detail'].default_value=5.0; lk.new(mp.outputs['Vector'],sw.inputs['Vector'])
    swipe=M('MULTIPLY',M('MAXIMUM',M('SUBTRACT',sw.outputs['Fac'],None,vb=0.55),None,vb=0.0),None,vb=0.5)   # faint eraser swipes
    fac=M('MINIMUM',M('ADD',ink,swipe),None,vb=0.6)
    lk.new(fac,mix.inputs['Fac']); lk.new(tr.outputs[0],mix.inputs[1]); lk.new(df.outputs[0],mix.inputs[2]); lk.new(mix.outputs[0],out.inputs['Surface'])
    return m
