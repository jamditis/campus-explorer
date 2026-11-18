# qb: SW slope tone blend. The pz feather / pk west fill (pale ortho grass) dive under the dark-green 3DEP context skirt
# (ou-darkened, canopy-green at grazing angles) -> hard tone edge at eye level. Store 'qb_fade' (1 where the
# object is under the skirt, smoothstep to 0 by R m away) and use a material copy that applies the same ou multiply tint by
# qb_fade x noise. REVERT=1 restores the previous slot material + link, removes the attribute and the copies. UNVERIFIED.
import bpy, bmesh, os
from mathutils import Vector, kdtree
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'; R=float(os.environ.get('QB_R','7'))
OBJS=['PZ_Feliciano_SW_DTM_edge_feather_UNVERIFIED','PK_Feliciano_west_DTM_fill_UNVERIFIED']
for on in OBJS:
    o=bpy.data.objects[on]
    if 'qb_prev_mat' in o:
        s=o.material_slots[0]; cp=s.material
        s.link=o['qb_prev_link']; 
        pm_=bpy.data.materials[o['qb_prev_mat']]; pm_.use_fake_user=bool(o.get('qb_prev_fake',0))
        if s.link=='OBJECT': s.material=pm_
        if cp and cp.name.startswith('QB_'): bpy.data.materials.remove(cp)
        del o['qb_prev_mat']; del o['qb_prev_link']
        if 'qb_prev_fake' in o: del o['qb_prev_fake']
        if 'UNVERIFIED_qb' in o: del o['UNVERIFIED_qb']
        if 'qb_fade' in o.data.attributes: o.data.attributes.remove(o.data.attributes['qb_fade'])
        print('REVERTED',on)
if not REV:
    dg=bpy.context.evaluated_depsgraph_get(); sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km'].evaluated_get(dg)
    bm=bmesh.new(); bm.from_mesh(sk.to_mesh()); bm.transform(sk.matrix_world); S=BVHTree.FromBMesh(bm); bm.free(); sk.to_mesh_clear()
    for on in OBJS:
        o=bpy.data.objects[on]; me=o.data; mw=o.matrix_world
        W=[mw@v.co for v in me.vertices]; hid=[]
        for c in W:
            h=S.ray_cast(Vector((c.x,c.y,c.z+60)),Vector((0,0,-1)),120)
            hid.append(h[0] is not None and h[0].z>c.z+0.005)
        nh=sum(hid); kd=kdtree.KDTree(max(nh,1))
        for i,c in enumerate(W):
            if hid[i]: kd.insert(Vector((c.x,c.y,0)),i)
        kd.balance(); fade=[]
        for i,c in enumerate(W):
            if hid[i]: fade.append(1.0); continue
            if nh==0: fade.append(0.0); continue
            co,j,d=kd.find(Vector((c.x,c.y,0)))
            t=min(1.0,d/R); fade.append(1.0-(3*t*t-2*t*t*t))
        a=me.attributes.new('qb_fade','FLOAT','POINT'); a.data.foreach_set('value',fade)
        nv=sum(1 for f in fade if 0<f<1)
        s=o.material_slots[0]; prev=s.material; o['qb_prev_link']=s.link; o['qb_prev_mat']=prev.name; o['qb_prev_fake']=int(prev.use_fake_user); prev.use_fake_user=True
        cp=prev.copy(); cp.name='QB_%s_skirt_fade_UNVERIFIED'%('PZ_feather' if on.startswith('PZ') else 'PK_fill')
        N=cp.node_tree.nodes; L=cp.node_tree.links
        bs=[n for n in N if n.type=='BSDF_PRINCIPLED'][0]; lk=bs.inputs['Base Color'].links[0]; src=lk.from_socket
        at=N.new('ShaderNodeAttribute'); at.attribute_name='qb_fade'; at.attribute_type='GEOMETRY'
        tc=N.new('ShaderNodeTexCoord'); nz=N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=0.035; nz.inputs['Detail'].default_value=4
        mr=N.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value=0.35; mr.inputs['From Max'].default_value=0.65; mr.inputs['To Min'].default_value=0.72; mr.inputs['To Max'].default_value=1.0
        mu=N.new('ShaderNodeMath'); mu.operation='MULTIPLY'
        mx=N.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.blend_type=os.environ.get('QB_BLEND','MIX'); mx.name='QB_fade_mix'
        SI=lambda nd,i:[x for x in nd.inputs if x.identifier==i][0]; SO=lambda nd,i:[x for x in nd.outputs if x.identifier==i][0]
        SI(mx,'B_Color').default_value=tuple(float(x) for x in os.environ.get('QB_TINT','0.06,0.12,0.055').split(','))+(1,)
        L.new(tc.outputs['Object'],nz.inputs['Vector']); L.new(nz.outputs['Fac'],mr.inputs['Value'])
        L.new(at.outputs['Fac'],mu.inputs[0]); L.new(mr.outputs['Result'],mu.inputs[1])
        L.new(mu.outputs['Value'],SI(mx,'Factor_Float')); L.new(src,SI(mx,'A_Color')); L.new(SO(mx,'Result_Color'),bs.inputs['Base Color'])
        # grazing-angle sky sheen is what reads pale at eye level: ease specular down + roughness up with the same factor
        KS=float(os.environ.get('QB_SPEC','0.85'))
        sp=bs.inputs['Specular IOR Level']; ms=N.new('ShaderNodeMath'); ms.operation='MULTIPLY_ADD'; ms.inputs[1].default_value=-KS; ms.inputs[2].default_value=1.0
        L.new(mu.outputs['Value'],ms.inputs[0]); m2=N.new('ShaderNodeMath'); m2.operation='MULTIPLY'
        if sp.is_linked: L.new(sp.links[0].from_socket,m2.inputs[0])
        else: m2.inputs[0].default_value=sp.default_value
        L.new(ms.outputs['Value'],m2.inputs[1]); L.new(m2.outputs['Value'],sp)
        rg=bs.inputs['Roughness']; mf=N.new('ShaderNodeMix'); mf.data_type='FLOAT'
        if rg.is_linked: L.new(rg.links[0].from_socket,SI(mf,'A_Float'))
        else: SI(mf,'A_Float').default_value=rg.default_value
        SI(mf,'B_Float').default_value=1.0; L.new(mu.outputs['Value'],SI(mf,'Factor_Float')); L.new(SO(mf,'Result_Float'),rg)
        s.link='OBJECT'; s.material=cp
        o['UNVERIFIED_qb']='qb (Nov 2 2026): tone tinted toward the ou-darkened skirt within %.0f m of where it dives under the skirt (attr qb_fade, %s); UNVERIFIED'%(R,cp.name)
        print('QB_FADE',on,'verts',len(W),'hidden',nh,'ramp',nv,'mat',cp.name)
