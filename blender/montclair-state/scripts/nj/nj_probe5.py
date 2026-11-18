import bpy, mathutils
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
def bb(o):
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
    return [round(min(c[i] for c in cs),2) for i in range(3)],[round(max(c[i] for c in cs),2) for i in range(3)]
for o in bpy.data.objects:
    if o.type=='MESH' and any(s.material and s.material.name in ('NG_red_wall','NH_entrance_glass_clear_thin_UNVERIFIED') for s in o.material_slots):
        print('OB|%s|%s|%d|%s|%s|hr%s'%(o.name,bb(o),len(o.data.polygons),[s.material.name for s in o.material_slots if s.material],[s.link for s in o.material_slots],o.hide_render))
m=bpy.data.materials['NG_wood_cladding']
for nd in m.node_tree.nodes: print('WOOD',nd.type,nd.name,[(i.name,tuple(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value) for i in nd.inputs if hasattr(i,'default_value') and not i.is_linked][:4])
for n in ('NG_terrazzo_1F_open_floor','NH_terrazzo_1F_tone_variation_UNVERIFIED'):
    for nd in bpy.data.materials[n].node_tree.nodes:
        if nd.type=='VALTORGB': print('RAMP',n,nd.name,[(round(e.position,2),tuple(round(c,3) for c in e.color)) for e in nd.color_ramp.elements])
for x in (-12.5,-8.0,-10.3):
    o=mathutils.Vector((x,6.6,138.6)); d=mathutils.Vector((0,-1,0))
    for k in range(6):
        hit,loc,n,i,ob,_=sc.ray_cast(dg,o,d)
        if not hit: print('RAY',x,'miss'); break
        print('RAY',x,ob.name,[round(v,2) for v in loc]); o=loc+d*0.003
        if loc.y<-12: break
g=bpy.data.objects['CCOM atrium glass (arched, 7x10 grid)']
print('GLASSN',[tuple(round(v,2) for v in (g.matrix_world.to_3x3()@p.normal)) for p in g.data.polygons][:6], len(g.data.polygons))
for o in bpy.data.objects:
    if o.type=='LIGHT' and o.name.startswith('NG '): print('LT',o.name,o.data.type,o.data.energy)
