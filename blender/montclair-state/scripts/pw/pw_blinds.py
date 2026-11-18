# pw (Nov 1-2 2026): interior window dressing behind Dickson's set-back glass (pv2 recessed openings). ALL UNVERIFIED
# (no photo of Dickson's interiors/blinds). Per opening, seeded variety: slatted blind fully up / part down / mostly down
# (two slat tones), pleated curtain pairs part-drawn (three muted fabrics, real zig-zag pleat geometry, rod), or nothing.
# Slot rectangles are read straight from PV2_Dickson_window_reveals_glass_UNVERIFIED (10 quads/slot: 4 reveals, glass, back, 4 sides).
# New object PW_Dickson_window_blinds_curtains_UNVERIFIED only; REVERT=1 removes it and the new PW materials.
import bpy, bmesh, os, random
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; ON='PW_Dickson_window_blinds_curtains_UNVERIFIED'
NEWM=['PW_blind_slats_beige_UNVERIFIED','PW_curtain_oatmeal_UNVERIFIED','PW_curtain_slate_UNVERIFIED','PW_curtain_rust_UNVERIFIED','PW_Dickson_glass_clearer_UNVERIFIED']
if ON in bpy.data.objects:
    o=bpy.data.objects[ON]; m2=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(m2); print('REVERTED_PW_BLINDS')
rv0=bpy.data.objects['PV2_Dickson_window_reveals_glass_UNVERIFIED']
if 'pw_prev_glass' in rv0:
    rv0.data.materials[1]=bpy.data.materials[rv0['pw_prev_glass']]; del rv0['pw_prev_glass']; print('REVERTED_PW_GLASS')
if REV:
    for n in NEWM:
        m=bpy.data.materials.get(n)
        if m and m.users==0: bpy.data.materials.remove(m)
else:
    rv=rv0; g0=rv.data.materials[1]; rv['pw_prev_glass']=g0.name
    g=bpy.data.materials.get(NEWM[4]) or g0.copy(); g.name=NEWM[4]; b=g.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(0.62,0.68,0.68,1); b.inputs['Transmission Weight'].default_value=max(0.92,b.inputs['Transmission Weight'].default_value)
    rv.data.materials[1]=g; print('PW_GLASS',g0.name,'->',g.name)   # Dickson-only clearer glass so the dressing reads (Calcia keeps PS glass)
    rv=bpy.data.objects['PV2_Dickson_window_reveals_glass_UNVERIFIED']; mw=rv.matrix_world; V=[mw@v.co for v in rv.data.vertices]
    assert len(V)%40==0, len(V)
    rnd=random.Random(20261102); bm=bmesh.new(); cnt={}
    def quad(a,b,c,d,mi): bm.faces.new([bm.verts.new(a),bm.verts.new(b),bm.verts.new(c),bm.verts.new(d)]).material_index=mi
    def box(c,ex,ey,ez,mi):
        vs=[bm.verts.new(c+ex*sx+ey*sy+ez*sz) for sx in (-1,1) for sy in (-1,1) for sz in (-1,1)]
        for q in [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]: bm.faces.new([vs[i] for i in q]).material_index=mi
    for s in range(len(V)//40):
        A,B,C,D=V[40*s+16:40*s+20]            # glass quad: A=(u0,v0) B=(u1,v0) C=(u1,v1) D=(u0,v1)
        bc=sum(V[40*s+20:40*s+24],Vector())/4; gc=(A+B+C+D)/4
        n=(gc-bc); depth=n.length; n.normalize()       # outward
        if depth<0.25: continue
        ex=(B-A); W=ex.length; eu=ex/W; ey=(D-A); H=ey.length; ev=ey/H
        P=lambda fu,fv,d: A+ex*fu+ey*fv-n*d     # fractions across/up, depth behind glass
        r=rnd.random()
        if r<0.62:   # slatted blind
            frac=0.03 if r<0.17 else (rnd.uniform(0.15,0.6) if r<0.47 else rnd.uniform(0.7,0.97))
            mi=0 if rnd.random()<0.65 else 1; d=0.07; ix=0.018/W; top=1-0.035/H
            fb=top-frac*(top-0.012/H)
            if frac>0.05: quad(P(ix,fb,d),P(1-ix,fb,d),P(1-ix,top,d),P(ix,top,d),mi)
            bc_=P(0.5,fb,d-0.004)-ev*0.008; box(bc_,eu*(W/2-0.02),ev*0.008,n*0.006,2)          # bottom rail
            box(P(0.5,top,d-0.01)+ev*0.012,eu*(W/2-0.012),ev*0.022,n*0.016,2)                  # head box
            if frac<=0.05: box(P(0.5,top,d)-ev*0.03,eu*(W/2-0.02),ev*0.02,n*0.012,mi)            # stacked slats
            cnt['blind']=cnt.get('blind',0)+1
        elif r<0.9:  # pleated curtain pair, part drawn
            mi=3+rnd.choice((0,0,1,2)); d=0.11; drop=rnd.uniform(0.92,0.985); pl=0.07
            box(P(0.5,1,d)-ev*0.04,eu*(W/2+0.0),ev*0.008,n*0.008,6)                              # rod
            for side in (0,1):
                cov=rnd.uniform(0.14,0.42); wid=cov*W; npl=max(3,int(wid/pl)); amp=0.022
                for k in range(npl):
                    f0=k/npl*cov; f1=(k+1)/npl*cov
                    if side: f0,f1=1-f1,1-f0
                    d0=d+(amp if k%2 else 0); d1=d+(0 if k%2 else amp)
                    if side: d0,d1=d1,d0
                    yb=1-drop; yt=1-0.05/H
                    quad(P(f0,yb,d0),P(f1,yb,d1),P(f1,yt,d1),P(f0,yt,d0),mi)
            cnt['curtain']=cnt.get('curtain',0)+1
        else: cnt['none']=cnt.get('none',0)+1
    m2=bpy.data.meshes.new(ON); bm.to_mesh(m2); bm.free()
    for p in m2.polygons: p.use_smooth=False
    pt=bpy.data.materials['PT_blind_slats_offwhite_UNVERIFIED']
    def slatcopy(name,col):
        m=bpy.data.materials.get(name)
        if m is None:
            m=pt.copy(); m.name=name; nt=m.node_tree
            cr=[x for x in nt.nodes if x.type=='VALTORGB'][0]
            cr.color_ramp.elements[0].color=(col[0]*0.55,col[1]*0.55,col[2]*0.55,1); cr.color_ramp.elements[1].color=col
        return m
    def fab(name,col):
        m=bpy.data.materials.get(name)
        if m is None:
            m=bpy.data.materials.new(name); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
            b.inputs['Base Color'].default_value=col; b.inputs['Roughness'].default_value=0.9
            b.inputs['Sheen Weight'].default_value=0.4
            b.inputs['Transmission Weight'].default_value=0.0
        return m
    for m in (pt, slatcopy(NEWM[0],(0.66,0.58,0.46,1)), bpy.data.materials['PT_blind_rail_grey_UNVERIFIED'],
              fab(NEWM[1],(0.62,0.56,0.46,1)), fab(NEWM[2],(0.30,0.34,0.38,1)), fab(NEWM[3],(0.42,0.22,0.15,1)),
              bpy.data.materials['PE_Dickson_coping_dark_bronze_UNVERIFIED']):
        m2.materials.append(m)
    o=bpy.data.objects.new(ON,m2); o['source_note']='UNVERIFIED: interior blinds/curtains invented (pw, Nov 2 2026); slots = PV2 glass quads'
    rv.users_collection[0].objects.link(o); print('PW_BLINDS',cnt,'V',len(m2.vertices),'F',len(m2.polygons))
