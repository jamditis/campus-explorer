# ws250: W63 LiDAR snap target (JSON V/F/W, box only), ground between Feliciano's east face, Dickson's north end and the
# lawn S of University Hall (UH footprint x -199..-116, y 221..308 from north/montclair_north.blend; box stays y<=214).
# 2023 J5D5 class-2 1 m grid (ws248 g1m_23), 2017 fallback (+0.12 m = the 2023-2017 median offset here); 3x3 nanmean, gaps filled;
# vertices at cell CENTRES (ws249f lesson); weight 1 in the core, linear 4 m feather to 0 at the box edge. Attr w250.
import numpy as np, json
exec(open('scripts/ws249/t249.py').read().split('Gw=np.load')[0].replace("D='scripts/ws249/'","D='scripts/ws250/'"))
G23=np.load('scripts/ws248/g1m_23.npy'); G17=np.load('scripts/ws248/g1m_17.npy')
G=np.where(np.isfinite(G23),G23,G17+0.12)
box=(-196,-142,142,214); x0,x1,y0,y1=box
H=fill(nanmean3(G)); X0,Y0=-320.,-20.
xs=np.arange(x0,x1+0.01,1.0); ys=np.arange(y0,y1+0.01,1.0); V=[];W=[]
for y in ys:
    for x in xs:
        z=H[int(y-Y0),int(x-X0)]
        V.append((float(x)+0.5,float(y)+0.5,float(z)))
        e=min(x-x0,x1-x,y-y0,y1-y); W.append(float(np.clip(e/4.0,0,1)))
nx=len(xs); F=[(j*nx+i,j*nx+i+1,(j+1)*nx+i+1,(j+1)*nx+i) for j in range(len(ys)-1) for i in range(nx-1)]
json.dump({'V':V,'F':F,'W':W},open('scripts/ws250/t250.json','w')); print('t250',len(V),len(F),'z %.2f..%.2f'%(min(v[2] for v in V),max(v[2] for v in V)))
