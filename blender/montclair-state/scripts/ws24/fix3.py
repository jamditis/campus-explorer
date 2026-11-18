import bpy
nt=bpy.data.materials['WS24_asphalt_weathered_JoePhoto'].node_tree
vo=[n for n in nt.nodes if n.type=='TEX_VORONOI'][0]; vo.inputs['Scale'].default_value=0.16
mr=[n for n in nt.nodes if n.type=='MAP_RANGE'][0]; mr.inputs['From Max'].default_value=0.005; mr.inputs['To Min'].default_value=0.62
mx=[n for n in nt.nodes if n.type=='MIX' and n.data_type=='VECTOR'][0]; mx.inputs['Factor'].default_value=0.35
bpy.ops.wm.save_mainfile(); print('SAVED')
