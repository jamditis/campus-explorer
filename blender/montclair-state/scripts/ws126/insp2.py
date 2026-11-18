import bpy
seen=set()
for o in bpy.data.objects:
    if o.name.startswith(('WS125_bed_shrub_','WS126_bed_shrub_')) and o.data.name not in seen:
        seen.add(o.data.name)
        area=sum(p.area for p in o.data.polygons)
        print('SH',o.name,o.data.name,tuple(round(s,3) for s in o.scale),'localdims',tuple(round(d/s,2) for d,s in zip(o.dimensions,o.scale)),'area',round(area,2))
        for m in o.modifiers:
            if m.type=='NODES':
                ng=m.node_group
                for n in ng.nodes:
                    if n.type=='DISTRIBUTE_POINTS_ON_FACES': print('  dens',n.inputs['Density'].default_value if 'Density' in n.inputs else '', n.distribute_method, [ (l.from_node.name) for l in n.inputs['Density'].links] if 'Density' in n.inputs else '')
                for k,v in m.items(): print('  modin',k,v if not hasattr(v,'name') else v.name)
            if m.type=='DISPLACE': print('  disp',m.strength, m.texture.name if m.texture else None)
