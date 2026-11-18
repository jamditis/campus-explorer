# scan building shells for see-through holes: rays from 1.5 m outside each footprint segment, inward along -normal
import bpy, json, sys, mathutils
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
names=[a for a in sys.argv[sys.argv.index('--')+1:]] if '--' in sys.argv else ['Center for Environmental and Life Sciences walls']
ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']
res={}
for wn in names:
    w=bpy.data.objects[wn]; me=w.data; M=w.matrix_world; holes=[]
    for p in me.polygons:
        if abs(p.normal.z)>0.2: continue
        vs=[M@me.vertices[i].co for i in p.vertices]; n=(M.to_3x3()@p.normal); n.z=0; n.normalize()
        c=sum(vs,mathutils.Vector())/len(vs); ztop=max(v.z for v in vs)
        # ground at the segment
        h,gl,_,_,_,_=sc.ray_cast(dg,mathutils.Vector((c.x+n.x*0.8,c.y+n.y*0.8,400)),mathutils.Vector((0,0,-1)))
        zg=gl.z if h else min(v.z for v in vs)
        z=zg+0.3
        while z<ztop-0.2:
            for t in (0.2,0.5,0.8):
                a=vs[0].lerp(vs[1] if len(vs)>1 else vs[0],t) if len(vs)>=2 else c
                # use the two distinct-xy verts
                xy=sorted({(round(v.x,3),round(v.y,3)) for v in vs})
                if len(xy)<2: break
                p0=mathutils.Vector((xy[0][0],xy[0][1],z)); p1=mathutils.Vector((xy[-1][0],xy[-1][1],z))
                o=p0.lerp(p1,t)+n*1.5
                hit,loc,nor,idx,ob,_=sc.ray_cast(dg,o,-n,distance=6.0)
                d=(loc-o).length if hit else 99
                if d>2.2: holes.append((round(o.x,2),round(o.y,2),round(z,2),ob.name if hit else None,round(d,1),[round(v,2) for v in n[:2]]))
            z+=0.75
    res[wn]=holes; print('HOLES',wn,len(holes))
    for hh in holes[:60]: print(' H',hh)
json.dump(res,open('data/ov/holes.json','w'))
