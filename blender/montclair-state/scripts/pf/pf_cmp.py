import bpy,sys
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
names=sys.argv[sys.argv.index('--')+1].split(',')
obs=[bpy.data.objects[n] for n in names]
for o in obs: print('TER',o.name,len(o.data.vertices),[round(v,1) for v in o.dimensions],[m.name for m in o.modifiers])
for x,y in [(-100,0),(-50,50),(0,100),(-150,120),(-180,140),(-200,150),(-230,160),(-260,200),(-220,240),(-150,200),(-100,200),(0,200),(-190,100),(-240,130)]:
    out=[]
    for o in obs:
        oe=o.evaluated_get(dg); mi=o.matrix_world.inverted()
        import mathutils
        p=mi@mathutils.Vector((x,y,300)); d=(mi.to_3x3()@mathutils.Vector((0,0,-1))).normalized()
        h,loc,n,i=oe.ray_cast(p,d); out.append(round((o.matrix_world@loc).z,2) if h else None)
    print('Z',x,y,out)
