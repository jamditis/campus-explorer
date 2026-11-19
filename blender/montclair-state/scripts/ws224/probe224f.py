import bpy,json
out={}
for name,n,b,f in (('WS220_CollegeAve_curb_jog_return_UNVERIFIED',5,3,1),('WS27_CollegeAve_curb_left_UNVERIFIED',6,3,1)):
    o=bpy.data.objects[name]; M=o.matrix_world; nr=len(o.data.vertices)//n
    out[name]=[(k,tuple(M@o.data.vertices[n*k+b].co),tuple(M@o.data.vertices[n*k+f].co)) for k in range(nr)]
    print('P224',name,'rings',nr,len(o.data.vertices))
json.dump(out,open('/tmp/ws224_curb.json','w'))
