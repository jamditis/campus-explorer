import bpy
from mathutils import Vector
g=bpy.data.materials['OH_Schmitt_door_glass_clear_UNVERIFIED'].node_tree.nodes['Principled BSDF']
print('glass',[ (i.name,tuple(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value) for i in g.inputs if i.name in('Base Color','Roughness','Transmission Weight','IOR','Alpha','Metallic')])
m=bpy.data.materials['OH_Schmitt_stucco_block_base_UNVERIFIED']
for n in m.node_tree.nodes:
    if n.type in('TEX_BRICK','BUMP','TEX_WHITE_NOISE','MIX') or n.name.startswith('Principled'):
        print(n.name,[(i.name,tuple(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value, i.is_linked) for i in n.inputs if hasattr(i,'default_value')][:12])
        print('   out->',[(l.to_node.name,l.to_socket.name) for o in n.outputs for l in o.links])
fr=bpy.data.objects['OG_Schmitt_E_entrance_storefront_frame']; la=bpy.data.objects['OG_Schmitt_E_entrance_landing']
fv=[fr.matrix_world@v.co for v in fr.data.vertices]; lb=[la.matrix_world@v.co for v in la.data.vertices]
cen=sum(fv,Vector())/len(fv); lc=sum(lb,Vector())/len(lb)
OUT=Vector(((lc-cen).x,(lc-cen).y,0)).normalized(); AL=Vector((-OUT.y,OUT.x,0)); cen.z=0
print('cen',cen,'OUT',OUT,'landing hidden',la.hide_render, [round(x,2) for x in (min(v.z for v in lb),max(v.z for v in lb))])
def loc(v): d=v-cen; return round(d.dot(AL),2), round(d.dot(OUT),2), round(v.z,2)
p=bpy.data.objects['Footpaths_OSM']; mw=p.matrix_world
for f in p.data.polygons:
    c=mw@f.center; a,o,z=loc(c)
    if abs(a)<8 and -1<o<14: print('pf',f.index,a,o,z,round(f.normal.z,2),round(f.area,2),[loc(mw@p.data.vertices[i].co)[:2] for i in f.vertices][:6])
ch=bpy.data.objects['OH_Schmitt_entrance_walk_cheek_wall_UNVERIFIED']; print('cheek',[loc(ch.matrix_world@Vector(b)) for b in ch.bound_box][::3])
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; mi=t.matrix_world.inverted()
for a,o in((0,2),(0,5),(0,8),(3,4),(-3,4)):
    q=cen+AL*a+OUT*o; h,l,n,i=t.ray_cast(mi@Vector((q.x,q.y,400)),mi.to_3x3()@Vector((0,0,-1))); print('terrain',a,o,round((t.matrix_world@l).z,2))
