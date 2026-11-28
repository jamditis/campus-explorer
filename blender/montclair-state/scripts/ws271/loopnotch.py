import numpy as np
def loops_and_notches(V,F,FM,FN,maxA=1.0):
    E={}
    for fi,f in enumerate(F):
        f=[i for i in f if i>=0]
        if FN[fi][2]<=0.3 or FM[fi]!=0: continue
        for a,b in zip(f,f[1:]+f[:1]):
            k=(min(a,b),max(a,b)); E[k]=E.get(k,0)+1
    bd=[k for k,c in E.items() if c==1]
    adj={}
    for a,b in bd: adj.setdefault(a,[]).append(b); adj.setdefault(b,[]).append(a)
    s=bd[0][0]; L=[s]; prev=None; cur=s
    while True:
        nx=[n for n in adj[cur] if n!=prev]
        n=nx[0]
        if n==s: break
        prev,cur=cur,n; L.append(n)
    P=V[L][:,:2]; A=0.5*(np.dot(P[:,0],np.roll(P[:,1],-1))-np.dot(P[:,1],np.roll(P[:,0],-1)))
    if A<0: L=L[::-1]
    out=[]; n=len(L)
    for k in range(n):
        a,b,c=L[k-1],L[k],L[(k+1)%n]
        u=V[b,:2]-V[a,:2]; w=V[c,:2]-V[b,:2]; cr=u[0]*w[1]-u[1]*w[0]
        if cr<0 and 0.5*abs(cr)<maxA: out.append((a,b,c,0.5*abs(cr)))
    return L,out
