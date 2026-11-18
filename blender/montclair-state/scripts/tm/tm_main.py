# tm: Bohn facade tone/windows after the 1971/1975 MSU slides (refs/bohn/): warm cream concrete, dark deep-set glazing
# (less sky reflection), faint vertical weathering streaks. Stone/Blanton get streaks only. ALL UNVERIFIED. REVERT=1 undoes.
import bpy,os
REV=os.environ.get('REVERT')=='1'
PAIRS=[('TK_Bohn_wall_eggcrate_UNVERIFIED','TM_Bohn_wall_v2_UNVERIFIED',True),('TK_dorm_wall_darker_UNVERIFIED','TM_dorm_wall_streaked_UNVERIFIED',False)]
if REV:
    n=0
    for me in bpy.data.meshes:
        if 'tm_orig' in me:
            orig=dict(me['tm_orig'])
            for i,s in enumerate(me.materials):
                if s and str(i) in orig: me.materials[i]=bpy.data.materials[orig[str(i)]]; n+=1
            del me['tm_orig']
    for _,new,_ in PAIRS:
        m=bpy.data.materials.get(new)
        if m: bpy.data.materials.remove(m)
    print('TM reverted slots',n)
else:
    for src,new,bohn in PAIRS:
        S=bpy.data.materials[src]; M=S.copy(); M.name=new; nt=M.node_tree; N=nt.nodes
        if bohn:
            N['Mix.004'].inputs['B'].default_value=(0.022,0.026,0.03,1)   # glass darker
            N['Mix.005'].inputs['B'].default_value=0.14                  # glass less mirror-like
            N['Mix.006'].inputs['B'].default_value=0.45                  # less sky reflection
            N['Mix.003'].inputs['B'].default_value=(0.10,0.095,0.09,1)   # reveal/frame shadow
            r=N['Color Ramp'].color_ramp.elements; r[0].color=(0.35,0.32,0.27,1); r[1].color=(0.46,0.42,0.36,1)
            r=N['Color Ramp.001'].color_ramp.elements; r[0].color=(0.32,0.30,0.26,1); r[1].color=(0.42,0.39,0.34,1)
        tc=N['Texture Coordinate']; mp=N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value=(0.9,0.9,0.05)
        nz=N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=3.0; nz.inputs['Detail'].default_value=4.0
        rp=N.new('ShaderNodeValToRGB'); e=rp.color_ramp.elements; e[0].position=0.42; e[0].color=(0.88,0.865,0.84,1); e[1].position=0.62; e[1].color=(1,1,1,1)
        mx=N.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.blend_type='MULTIPLY'; mx.inputs['Factor'].default_value=1.0
        nt.links.new(tc.outputs['Object'],mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'],nz.inputs['Vector'])
        nt.links.new(nz.outputs['Fac'],rp.inputs['Fac'])
        b=N['Principled BSDF']; f=b.inputs['Base Color'].links[0].from_socket
        nt.links.new(f,mx.inputs['A']); nt.links.new(rp.outputs['Color'],mx.inputs['B']); nt.links.new(mx.outputs['Result'],b.inputs['Base Color'])
    n=0
    for me in bpy.data.meshes:
        d={}
        for i,s in enumerate(me.materials):
            for src,new,_ in PAIRS:
                if s and s.name==src: d[str(i)]=src; me.materials[i]=bpy.data.materials[new]; n+=1
        if d: me['tm_orig']=d
    for src,_,_ in PAIRS: bpy.data.materials[src].use_fake_user=True
    print('TM applied slots',n)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
