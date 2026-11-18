# ws75d: (1) last 7 Roads_OSM stubs (centres just under the ground, edges poking out = the remaining dark bar) at x -256..-244, y -126..-110;
# (2) fn_lot_asphalt (cogen + new Sprague lot) darkened: HSV Value 0.74 inserted before Base Color (was much paler than College Ave asphalt).
import bpy,bmesh
o=bpy.data.objects['Roads_OSM']; mw=o.matrix_world
kill=[p.index for p in o.data.polygons if -256<(mw@p.center).x<-244 and -126<(mw@p.center).y<-110]
bm=bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[bm.faces[i] for i in kill],context='FACES'); bm.to_mesh(o.data); bm.free(); o.data.update()
print('WS75d roads stubs deleted',len(kill),flush=True)
m=bpy.data.materials['fn_lot_asphalt']; nt=m.node_tree
b=[n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'][0]; bc=b.inputs['Base Color']
print('WS75d users',m.users,'basecolor linked',bc.is_linked, [l.from_node.name for l in bc.links], tuple(bc.default_value) if not bc.is_linked else '',flush=True)
if 'WS75_darken' not in nt.nodes:
    h=nt.nodes.new('ShaderNodeHueSaturation'); h.name='WS75_darken'; h.inputs['Value'].default_value=0.74; h.inputs['Saturation'].default_value=0.9
    if bc.is_linked:
        fs=bc.links[0].from_socket; nt.links.new(fs,h.inputs['Color'])
    else:
        h.inputs['Color'].default_value=bc.default_value
    nt.links.new(h.outputs['Color'],bc); h.location=(b.location.x-200,b.location.y+200)
print('WS75d done',flush=True)
