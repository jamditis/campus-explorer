# ws76c: the OSM footway drawn diagonally across the accessible lot (2020 ortho shows paving there, no walk) -> delete those Footpaths_OSM faces
import bpy,bmesh,numpy as np
D='/workspace/nj-scenes/montclair-state/scripts/ws76/'
M=np.load(D+'mask76.npy'); X0,X1,Y0,Y1,S=np.load(D+'mask76_grid.npy')
o=bpy.data.objects['Footpaths_OSM']; mw=o.matrix_world
def inm(x,y):
    i=int((x-X0)/S); j=int((y-Y0)/S); return 0<=i<M.shape[1] and 0<=j<M.shape[0] and M[j,i]
kill=[p.index for p in o.data.polygons if -256<(mw@p.center).x<-236 and -92<(mw@p.center).y<-68 and inm((mw@p.center).x,(mw@p.center).y)]
bm=bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[bm.faces[i] for i in kill],context='FACES'); bm.to_mesh(o.data); bm.free(); o.data.update()
print('WS76c Footpaths_OSM faces deleted',len(kill),flush=True)
