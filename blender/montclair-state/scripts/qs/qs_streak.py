# qs part 2: Richardson tower precast streaks read uniform/brushed -> gate the qr streak term by a low-frequency column mask
# (only some panel columns streak) and a height fade (strongest under the cap, fading toward the base). UNVERIFIED (visual).
# REVERT=1 removes QS_ nodes and relinks the original streak MapRange to its consumer.
import bpy, os
m=bpy.data.materials['QR_Richardson_tower_precast_UNVERIFIED']; N=m.node_tree.nodes; L=m.node_tree.links
def revert():
    qs=[n for n in N if n.name.startswith('QS_')]
    if not qs: return
    st=N[m['qs_st']]; tgt=N[m['qs_tgt']]; si=m['qs_si']
    for n in qs: N.remove(n)
    L.new(st.outputs[0],tgt.inputs[si]); del m['qs_st'],m['qs_tgt'],m['qs_si']; print('QS streak reverted')
revert()
if os.environ.get('REVERT')!='1':
    st=[n for n in N if n.bl_idname=='ShaderNodeMapRange' and abs(n.inputs['From Min'].default_value-0.45)<1e-6 and abs(n.inputs['To Max'].default_value-0.74)<1e-6][0]
    lk=[l for l in L if l.from_node==st][0]; tgt=lk.to_node; si=list(tgt.inputs).index(lk.to_socket)
    m['qs_st']=st.name; m['qs_tgt']=tgt.name; m['qs_si']=si
    uv=[n for n in N if n.bl_idname=='ShaderNodeUVMap'][0]
    def new(t,nm,**kw):
        n=N.new(t); n.name=nm
        for k,v in kw.items(): setattr(n,k,v)
        return n
    sp=new('ShaderNodeSeparateXYZ','QS_sep'); L.new(uv.outputs[0],sp.inputs[0])
    cu=new('ShaderNodeCombineXYZ','QS_colvec'); mu=new('ShaderNodeMath','QS_umul',operation='MULTIPLY'); mu.inputs[1].default_value=0.35
    L.new(sp.outputs[0],mu.inputs[0]); L.new(mu.outputs[0],cu.inputs[0]); cu.inputs[2].default_value=7.3
    nz=new('ShaderNodeTexNoise','QS_colnoise'); nz.inputs['Scale'].default_value=1.0; nz.inputs['Detail'].default_value=1.0; L.new(cu.outputs[0],nz.inputs['Vector'])
    cm=new('ShaderNodeMapRange','QS_colmask'); cm.inputs['From Min'].default_value=0.42; cm.inputs['From Max'].default_value=0.62; L.new(nz.outputs['Fac'],cm.inputs['Value'])
    hf=new('ShaderNodeMapRange','QS_hfade'); hf.inputs['From Min'].default_value=141.0; hf.inputs['From Max'].default_value=156.5; hf.inputs['To Min'].default_value=0.15; hf.inputs['To Max'].default_value=1.0; L.new(sp.outputs[1],hf.inputs['Value'])
    mk=new('ShaderNodeMath','QS_mask',operation='MULTIPLY'); L.new(cm.outputs[0],mk.inputs[0]); L.new(hf.outputs[0],mk.inputs[1])
    mx=new('ShaderNodeMix','QS_streakmix'); mx.data_type='FLOAT'; L.new(mk.outputs[0],mx.inputs[0]); mx.inputs[2].default_value=1.0; L.new(st.outputs[0],mx.inputs[3])
    L.new(mx.outputs[0],tgt.inputs[si]); print('QS streak gated',st.name,'->',tgt.name,si)
if os.environ.get('QSSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
