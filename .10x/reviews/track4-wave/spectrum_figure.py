import sys,numpy as np
S=sys.argv[1]
d=np.genfromtxt(S+'/telemetry.csv',delimiter=',',names=True);x=d['gauge1eta'];x=x-x.mean()
fs=10;N=1024;w=np.hanning(N);segs=[x[i:i+N]*w for i in range(0,len(x)-N+1,N//2)];K=len(segs)
P=np.mean([abs(np.fft.rfft(s))**2 for s in segs],0)/(fs*(w**2).sum());P[1:-1]*=2
f=np.fft.rfftfreq(N,1/fs)
nu=2*K*0.9/ (1+2*(0.167)**2)  # Welch Hann 50% overlap equivalent dof (approx)
def chi2q(p,v):  # Wilson-Hilferty
    from statistics import NormalDist;z=NormalDist().inv_cdf(p);return v*(1-2/(9*v)+z*np.sqrt(2/(9*v)))**3
lo=nu*P/chi2q(.95,nu);hi=nu*P/chi2q(.05,nu)
fp=1/9;s=np.where(f<=fp,.07,.09);ff=np.where(f>0,f,1e-9)
J=ff**-5*np.exp(-1.25*(fp/ff)**4)*3.3**np.exp(-(ff-fp)**2/(2*s**2*fp**2));J[f==0]=0
J*=(2.5/4)**2/np.trapezoid(J,f)
m0=np.trapezoid(P,f);hm0=4*np.sqrt(m0)
sel=(f>=0.03)&(f<=0.30);f,P,lo,hi=f[sel],P[sel],lo[sel],hi[sel]
fj=np.linspace(0.03,0.30,541);sj=np.where(fj<=fp,.07,.09)
J=fj**-5*np.exp(-1.25*(fp/fj)**4)*3.3**np.exp(-(fj-fp)**2/(2*sj**2*fp**2));fa=np.linspace(1e-3,2,20000);sa=np.where(fa<=fp,.07,.09);Ja=fa**-5*np.exp(-1.25*(fp/fa)**4)*3.3**np.exp(-(fa-fp)**2/(2*sa**2*fp**2));J*=(2.5/4)**2/np.trapezoid(Ja,fa)
print('K',K,'nu',round(nu,1),'Hm0',round(hm0,3),'ratio m0',round(m0/(2.5/4)**2,3))
W,H=760,440;L,R,T,B=64,24,92,58;pw,ph=W-L-R,H-T-B
ymax=np.ceil(max(hi.max(),J.max())/5)*5
X=lambda v:L+(v-0.03)/(0.27)*pw;Y=lambda v:T+ph-(v/ymax)*ph
def line(xs,ys):return 'M'+' L'.join(f'{X(a):.1f} {Y(b):.1f}' for a,b in zip(xs,ys))
band=line(f,hi)+' L'+' L'.join(f'{X(a):.1f} {Y(b):.1f}' for a,b in zip(f[::-1],lo[::-1]))+' Z'
g=[]
for yv in np.arange(0,ymax+0.01,5):
    g.append(f'<line class="grid" x1="{L}" x2="{L+pw}" y1="{Y(yv):.1f}" y2="{Y(yv):.1f}"/><text class="tick" x="{L-8}" y="{Y(yv)+4:.1f}" text-anchor="end">{yv:g}</text>')
for xv in (0.05,0.1,0.15,0.2,0.25,0.3):
    g.append(f'<text class="tick" x="{X(xv):.1f}" y="{T+ph+20}" text-anchor="middle">{xv:.2f}</text>')
ip=np.argmax(P);jp=np.argmax(J)
svg=f'''<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d" xmlns="http://www.w3.org/2000/svg">
<title id="t">Measured wave spectrum at the gauge against the requested JONSWAP spectrum</title>
<desc id="d">Line chart of spectral density against frequency. The measured spectrum, from a {len(x)/10:.0f}-second gauge record, peaks near 0.107 hertz like the requested JONSWAP curve, but holds about {round((m0/(2.5/4)**2-1)*100)} percent more energy: its significant wave height is {hm0:.2f} metres against the 2.50 metres requested.</desc>
<text class="title" x="{L-40}" y="30">The gauge peaks where the requested sea does, but holds about {round((m0/(2.5/4)**2-1)*100)}% more energy</text>
<text class="sub" x="{L-40}" y="52">Wave Laboratory, “Moderate sea” preset · gauge at (−120, 60) m · {len(x)/10:.0f} s at 10 Hz · Welch, Hann, 1,024 points, 50 % overlap</text>
<g class="legend" transform="translate({L-40} 72)"><line class="m" x1="0" x2="22" y1="-4" y2="-4"/><text x="28" y="0">Measured · Hm0 {hm0:.2f} m (band: 90 % interval)</text>
<line class="j" x1="330" x2="352" y1="-4" y2="-4"/><text x="358" y="0">Requested JONSWAP · Hs 2.50 m, Tp 9 s, γ 3.3</text></g>
{''.join(g)}
<line class="axis" x1="{L}" x2="{L+pw}" y1="{T+ph}" y2="{T+ph}"/>
<text class="label" x="{L+pw/2}" y="{H-12}" text-anchor="middle">Frequency (Hz)</text>
<text class="label" transform="translate(16 {T+ph/2}) rotate(-90)" text-anchor="middle">Spectral density (m²/Hz)</text>
<path class="band" d="{band}"/>
<path class="j" d="{line(fj,J)}"/>
<path class="m" d="{line(f,P)}"/>
<circle class="mdot" cx="{X(f[ip]):.1f}" cy="{Y(P[ip]):.1f}" r="4"/>
<text class="direct" x="{X(f[ip])+10:.1f}" y="{Y(P[ip])-4:.1f}">Measured peak {1/f[ip]:.1f} s</text>
<line class="axis" x1="{X(fj[jp])+6:.1f}" x2="{X(fj[jp])+56:.1f}" y1="{Y(J[jp]):.1f}" y2="{Y(J[jp]):.1f}"/><text class="direct" x="{X(fj[jp])+62:.1f}" y="{Y(J[jp])+4:.1f}">Requested peak 9.0 s</text>
</svg>'''
css='''body{margin:0;padding:24px;font-family:Inter,system-ui,sans-serif;background:var(--paper)}
:root{--paper:#fff;--ink:#1b2428;--muted:#5b6970;--rule:#e2e8eb;--c1:#008b9a;--c2:#4f5fc4}
.dark{--paper:#0f1a1e;--ink:#e6eef0;--muted:#9aaab0;--rule:#24353b;--c1:#2aa3b0;--c2:#7c86f0}
svg text{fill:var(--muted);font-size:12px}.title{fill:var(--ink)!important;font-size:17px!important;font-weight:600}.sub{font-size:12px}
.legend text{fill:var(--ink);font-size:12.5px}.direct{fill:var(--ink)!important;font-size:12px}
.grid{stroke:var(--rule);stroke-width:1}.axis{stroke:var(--muted);stroke-width:1}
.m{stroke:var(--c1);stroke-width:2;fill:none;stroke-linejoin:round}.band{fill:var(--c1);opacity:.16}
.j{stroke:var(--c2);stroke-width:2;fill:none;stroke-dasharray:6 4}.mdot{fill:var(--c1);stroke:var(--paper);stroke-width:2}'''
for mode in ('light','dark'):
    open(f'{S}/spec-{mode}.html','w').write(f'<!doctype html><meta charset=utf-8><style>{css}</style><body class="{"dark" if mode=="dark" else ""}">{svg}')
open(f'{S}/spec.svg','w').write(svg)
