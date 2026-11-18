"""vz polish: after WIP read — further soften if striping still reads woodgrain; still no colour invent."""
import bpy, json, os
STASHP='/workspace/nj-scenes/montclair-state/data/vz/vz_polish_stash.json'
MAT='TR_Blanton_infill_cream_UNVERIFIED'
m=bpy.data.materials[MAT]; nt=m.node_tree
mp=nt.nodes['Mapping']; mp1=nt.nodes['Mapping.001']
nz3=nt.nodes['Noise Texture.003']; cr2=nt.nodes['Color Ramp.002']; mx8=nt.nodes['Mix.008']
stash={
 'Mapping_scale':[float(x) for x in mp.inputs['Scale'].default_value],
 'Mapping001_scale':[float(x) for x in mp1.inputs['Scale'].default_value],
 'Noise003_Detail':float(nz3.inputs['Detail'].default_value),
 'Mix008_fac':float(mx8.inputs[0].default_value),
 'CR002':[{'pos':float(e.position),'color':[float(x) for x in e.color]} for e in cr2.color_ramp.elements],
}
json.dump(stash, open(STASHP,'w'), indent=1)
# Extra soften: more isotropic Z + weaker multiply
mp.inputs['Scale'].default_value=(1.05,1.05,0.48)
mp1.inputs['Scale'].default_value=(0.60,0.60,0.32)
mx8.inputs[0].default_value=0.32
els=cr2.color_ramp.elements
els[0].color=(0.97,0.96,0.95,1.0)
els[0].position=0.22
els[1].position=0.78
m['vz_polish']=1
bpy.ops.wm.save_mainfile()
print('VZP saved', len(bpy.data.objects), 'Mix008', mx8.inputs[0].default_value,
      'Map', list(mp.inputs['Scale'].default_value))
