import bpy, math
from mathutils import Vector
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws166/hdr166.py').read())
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
def cast(cx,cy,ch,tx,ty,th,lens,pts,tag):
    c=Vector((cx,cy,dz(cx,cy)+ch)); t=Vector((tx,ty,dz(tx,ty)+th))
    f=(t-c).normalized(); r=f.cross(Vector((0,0,1))).normalized(); u=r.cross(f)
    tw=18/lens; th2=tw*9/16
    for (px,py) in pts:
        d=(f+r*((px/768-0.5)*2)*tw+u*((0.5-py/432)*2)*th2).normalized()
        hit,loc,nor,idx,ob,_=sc.ray_cast(dg,c,d)
        print('PROBE171c',tag,px,py,ob.name if hit else None,tuple(round(a,2) for a in loc) if hit else None,'dtm',round(dz(loc.x,loc.y),2) if hit else None,'nz',round(nor.z,2) if hit else None,flush=True)
cast(-312.5,-243.5,1.6,-301.5,-234.5,0.3,28,[(540,y) for y in range(158,200,4)],'close')
cast(-276.5,-274.0,1.7,-322,-262.5,6.0,26,[(355,312),(362,316),(368,318),(350,320),(300,290),(250,275),(150,282)],'eyeE')
cast(-344.0,-254.0,1.7,-300,-266.5,7.0,26,[(450,290),(520,289),(600,290),(660,291),(560,285)],'eyeW')
