import bpy
for p in ('WS110_NormalAve_curb_W11p3','WS110_NormalAve_sidewalk_ws85','WS110_NormalAve_carriageway','WS179_'):
    for o in obs(p):
        mw=o.matrix_world; rows=[]
        for v in o.data.vertices:
            w=mw@v.co; s,t=st(w.x,w.y)
            if (0<t<6 or 16<t<23) and sf(t)-3<s<sf(t)+0.6:
                rows.append((round(t,2),round(s-sf(t),2),round(w.z-zroad(sf(t)+0.1,min(max(t,TW),TE)),3)))
        rows.sort()
        print('DBG',o.name[:50],len(rows),flush=True)
        for r in rows[:400]: print('DBG   ',r,flush=True)
