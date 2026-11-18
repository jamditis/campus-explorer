import bpy
for mn in ('Roof_tile_or_membrane','Eave_tile_top_soffit_under','Roof_barrel_tile_course'):
    m=bpy.data.materials[mn]; print('MAT',mn,m.users)
    for n in m.node_tree.nodes:
        extra=''
        if n.type in ('MATH','MAP_RANGE','VALTORGB','SEPXYZ','SEPARATE_XYZ','NEW_GEOMETRY','MIX','ATTRIBUTE'):
            extra=[(i.name,getattr(i,'default_value',None)) for i in n.inputs if not i.is_linked][:4]
            if n.type=='MATH': extra=(n.operation,extra)
        print('  ',n.type,n.name,extra)
