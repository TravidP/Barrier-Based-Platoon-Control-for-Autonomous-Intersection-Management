"""Offline trefoil geometry and distance-conflict demand; standard library only.

No TTC criterion, CARLA connection, XODR export or convergence claim.
Run from any directory: python3 'barrier 2vs1/scripts/analyze_design.py'
"""
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PI = math.pi


class Route:
    def __init__(self, width):
        self.x, self.y, self.heading = width/2, 0.0, PI
        self.s, self.parts = 0.0, []

    def add(self, length, curvature, name):
        p = dict(x=self.x, y=self.y, heading=self.heading, s=self.s,
                 length=length, curvature=curvature, name=name)
        self.parts.append(p)
        self.x, self.y, self.heading = point(p, length)
        self.s += length

    def line(self, length, name):
        self.add(length, 0.0, name)

    def turn(self, radius, angle, name):
        self.add(abs(angle)*radius, math.copysign(1/radius, angle), name)

    def sample(self, step):
        samples = []
        for idx, p in enumerate(self.parts):
            n = max(1, math.ceil(p['length']/step))
            for k in range(n):
                q = p['length']*k/n
                x, y, h = point(p, q)
                samples.append([p['s']+q, x, y, h, p['curvature'], idx])
        samples.append([self.s,self.x,self.y,self.heading,0.0,len(self.parts)-1])
        return samples


def point(p, q):
    x,y,h,k = p['x'],p['y'],p['heading'],p['curvature']
    if abs(k)<1e-15:
        return x+q*math.cos(h),y+q*math.sin(h),h
    h2=h+k*q
    return x+(math.sin(h2)-math.sin(h))/k, y+(math.cos(h)-math.cos(h2))/k,h2


def build(width, radius, straight):
    theta=math.acos(.5+width/(4*radius))
    leg=2*straight+radius*(PI+4*theta)
    rnw=(leg-width)/(2+1.5*PI)
    rne=leg/(2+1.5*PI)
    r=Route(width)
    r.line(width,'central_EW_c1_c2')
    r.line(rnw,'NW_depart_W')
    r.turn(rnw,-1.5*PI,'NW_outer_270')
    r.line(rnw,'NW_approach_NS')
    r.line(straight,'south_depart_NS')
    r.turn(radius,-theta,'south_flare_R')
    r.turn(radius,PI+2*theta,'south_bulb_L')
    r.turn(radius,-theta,'south_return_R')
    r.line(straight,'south_approach_SN')
    r.line(rne,'NE_depart_N')
    r.turn(rne,-1.5*PI,'NE_outer_270')
    r.line(rne,'NE_approach_EW')
    events=[dict(reference='C',branch='EW',s=width/2),
            dict(reference='C',branch='NS',s=leg),
            dict(reference='C',branch='SN',s=2*leg)]
    return r,events,dict(leg_m=leg,theta_rad=theta,NW_radius_m=rnw,NE_radius_m=rne)


def cross(a,b):
    return a[0]*b[1]-a[1]*b[0]


def sub(a,b):
    return (a[0]-b[0],a[1]-b[1])


def intersection(a,b,c,d):
    u,v=sub(b,a),sub(d,c)
    den=cross(u,v)
    if abs(den)<1e-12:
        return None
    t=cross(sub(c,a),v)/den
    q=cross(sub(c,a),u)/den
    if -1e-9<=t<=1+1e-9 and -1e-9<=q<=1+1e-9:
        return (a[0]+t*u[0],a[1]+t*u[1])
    return None


def point_dist(p,a,b):
    v=sub(b,a)
    den=v[0]*v[0]+v[1]*v[1]
    t=max(0.0,min(1.0,((p[0]-a[0])*v[0]+(p[1]-a[1])*v[1])/den))
    return math.hypot(p[0]-a[0]-t*v[0],p[1]-a[1]-t*v[1])


def geometry_check(route,samples,width):
    # Hash expanded segment bounding boxes. Nearby samples on the same route
    # are excluded by cyclic arc distance, not by Cartesian distance.
    bins=defaultdict(list)
    pairs=set()
    cell=10.0
    for i in range(len(samples)-1):
        a,b=samples[i][1:3],samples[i+1][1:3]
        for xx in range(math.floor((min(a[0],b[0])-width)/cell), math.floor((max(a[0],b[0])+width)/cell)+1):
            for yy in range(math.floor((min(a[1],b[1])-width)/cell), math.floor((max(a[1],b[1])+width)/cell)+1):
                for j in bins[(xx,yy)]:
                    pairs.add((j,i))
                bins[(xx,yy)].append(i)
    hits=set(); overlaps=[]; minimum=1e99
    for i,j in pairs:
        delta=abs((samples[i][0]+samples[i+1][0]-samples[j][0]-samples[j+1][0])/2)
        if min(delta,route.s-delta)<10.0:
            continue
        a,b=samples[i][1:3],samples[i+1][1:3]
        c,d=samples[j][1:3],samples[j+1][1:3]
        hit=intersection(a,b,c,d)
        if hit:
            hits.add((round(hit[0],5),round(hit[1],5)))
        # Only exempt prescribed perpendicular branches within central box.
        central=all(abs(p[0])<=8 and abs(p[1])<=8 for p in [a,b,c,d])
        if central:
            continue
        dist=0.0 if hit else min(point_dist(a,c,d),point_dist(b,c,d),point_dist(c,a,b),point_dist(d,a,b))
        minimum=min(minimum,dist)
        if dist<width-.005:
            overlaps.append([i,j,dist])
    closure=math.hypot(route.x-width/2,route.y)
    heading_error=abs(math.atan2(math.sin(route.heading-PI),math.cos(route.heading-PI)))
    expected={(-width/2,0.0),(width/2,0.0)}
    assert hits==expected, ('unexpected intersections',hits)
    assert not overlaps, ('road strips overlap away from junction',overlaps[:3])
    assert closure<1e-8 and heading_error<1e-8
    return dict(closure_error_m=closure,heading_error_rad=heading_error,
                crossings_xy=sorted(hits),nonlocal_strip_overlap_count=len(overlaps),
                min_nonlocal_centerline_distance_outside_junction_m=minimum,
                strip_test_tolerance_m=.005,method='sampled segments; 10 m local arc exclusion; central 16x16 m junction exclusion',
                curvature_continuous=False,continuity='G1: exact position and heading continuity, curvature jumps at primitive joins')


def csv_write(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)


def tex_macro(name,value):
    return '\\newcommand{\\'+name+'}{'+str(value)+'}\n'


def map_fig(route,width,filename,zoom=False,vehicles=0):
    data=route.sample(2.0)
    groups=[(0,4,'orange!85!black'),(4,9,'teal!80!black'),(9,12,'blue!65!black')]
    # Standalone SVG and embeddable TikZ are both vector outputs from same samples.
    bounds=(-10,10,-10,10) if zoom else (min(p[1] for p in data)-12,max(p[1] for p in data)+12,min(p[2] for p in data)-12,max(p[2] for p in data)+12)
    xmin,xmax,ymin,ymax=bounds
    scale=(10.0 if zoom else 14.0)/(xmax-xmin)
    tik=['\\begin{tikzpicture}[x='+str(scale)+'cm,y='+str(scale)+'cm,>=Latex]',
         f'\\clip ({xmin},{ymin}) rectangle ({xmax},{ymax});']
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{xmin} {-ymax} {xmax-xmin} {ymax-ymin}">',
         f'<rect x="{xmin}" y="{-ymax}" width="{xmax-xmin}" height="{ymax-ymin}" fill="white"/>']
    colors=['#b67615','#007e87','#326fc0']
    for gi,(lo,hi,col) in enumerate(groups):
        pts=[p for p in data if lo<=p[5]<hi]
        # Include exact endpoint of this group.
        end=route.parts[hi-1];x,y,_=point(end,end['length'])
        coords=[(p[1],p[2]) for p in pts]+[(x,y)]
        points=' '.join(f'{x:.3f},{-y:.3f}' for x,y in coords)
        svg.append(f'<polyline points="{points}" fill="none" stroke="#e7ecef" stroke-width="{width}"/>')
        svg.append(f'<polyline points="{points}" fill="none" stroke="{colors[gi]}" stroke-width="{.25 if zoom else .8}"/>')
        path=' -- '.join(f'({x:.3f},{y:.3f})' for x,y in coords)
        tik.append(f'\\draw[draw=gray!18,line width={width*scale*28.45274:.3f}pt] '+path+';')
        tik.append(f'\\draw[draw={col},line width=.7pt] '+path+';')
    for x,name in [(0.,'C')]:
        tik.append(f'\\fill[red!75!black] ({x},0) circle[radius={.15 if zoom else 1.5}];')
        if zoom:
            tik.append(f'\\node[above,font=\\small,fill=white,inner sep=1pt] at ({x},.5) {{$'+name+'$};')
        svg.append(f'<circle cx="{x}" cy="0" r="{.15 if zoom else 1.5}" fill="#b63e4a"/>')
    if zoom:
        tik.extend([f'\\draw[<->] ({-width/2},-5) -- ({width/2},-5) node[midway,below,font=\\small] {{{width} m}};',
                    '\\draw[->,thick] (8,0)--(5,0);',
                    f'\\draw[->,thick] ({-width/2},7)--({-width/2},4);',
                    f'\\draw[->,thick] ({width/2},-7)--({width/2},-4);'])
    else:
        tik.append('\\node[right,font=\\small,fill=white,inner sep=1pt] at (12,-12) {中央路口};')
        for partidx,label in [(2,'西北叶瓣'),(6,'南侧叶瓣'),(10,'东北叶瓣')]:
            p=route.parts[partidx];x,y,h=point(p,p['length']/2)
            tik.append(f'\\node[fill=white,inner sep=2pt,font=\\small] at ({x},{y}) {{{label}}};')
        # Arrows on straight branches are exact heading indicators.
        for partidx in [1,3,4,8,9,11]:
            p=route.parts[partidx];x,y,h=point(p,p['length']/2)
            xe,ye=x+9*math.cos(h),y+9*math.sin(h)
            tik.append(f'\\draw[->,thick] ({x},{y})--({xe},{ye});')
        if vehicles:
            for i in range(vehicles):
                q=(i+.3)*route.s/vehicles
                p=next(p for p in route.parts if p['s']<=q<p['s']+p['length'])
                x,y,h=point(p,q-p['s'])
                tik.append(f'\\fill[black] ({x},{y}) circle[radius=2];')
                if vehicles<=12 and math.hypot(x,y)>15:
                    tik.append(f'\\node[above,font=\\tiny] at ({x},{y+2}) {{{i+1}}};')
        bx,by=xmin+10,ymin+10
        tik.append(f'\\draw[|-|,thick] ({bx},{by})--({bx+50},{by}) node[midway,above,font=\\small] {{50 m}};')
        if filename=='map_baseline':
            for idx in [2,10]:
                p=route.parts[idx];k=p['curvature'];radius=abs(1/k)
                cx=p['x']-math.sin(p['heading'])/k
                cy=p['y']+math.cos(p['heading'])/k
                ex=cx+(-radius if idx==2 else radius)
                tik.append(f'\\draw[<->,gray!70] ({cx},{cy})--({ex},{cy}) node[midway,above,font=\\scriptsize,fill=white,inner sep=1pt] {{$R={radius:.1f}$ m}};')
            straight=route.parts[4]['length']
            tik.append(f'\\draw[<->,gray!70] (-12,0)--(-12,{-straight}) node[midway,left,font=\\scriptsize] {{{straight:.0f} m}};')
        svg.append(f'<path d="M {bx} {-by} h 50" stroke="black" stroke-width="0.7"/>')
        svg.append(f'<text x="{bx+25}" y="{-by-3}" font-size="5" text-anchor="middle">50 m</text>')
        for xx,yy,label in [(-80,100,'NW'),(80,100,'NE'),(0,-160,'SOUTH'),(25,-12,'JUNCTION')]:
            svg.append(f'<text x="{xx}" y="{-yy}" font-size="5" text-anchor="middle">{label}</text>')
    tik.append('\\end{tikzpicture}\n');svg.append('</svg>')
    (ROOT/'figures'/f'{filename}.tex').write_text('\n'.join(tik))
    (ROOT/'figures'/f'{filename}.svg').write_text('\n'.join(svg))


def at_length(target,width):
    lo,hi=2.,200.
    for _ in range(70):
        radius=(lo+hi)/2
        route,events,shape=build(width,radius,1.2*radius)
        if route.s<target:lo=radius
        else:hi=radius
    radius=(lo+hi)/2
    route,events,shape=build(width,radius,1.2*radius)
    return route,events,shape,radius


def approach_lists(positions,length,width,window):
    targets=[width/2,length/3,2*length/3]
    lists=[]
    for target in targets:
        lists.append([(i,(target-s)%length) for i,s in enumerate(positions)
                      if 0<(target-s)%length<=window])
    return lists  # signed longitudinal distances to common center C


def demand(length,width,n,window,threshold,samples=1200):
    spacing=length/n
    double_window=double_active=any_active=two_on_lane=0
    min_gap1=min_gap2=float('inf')
    for k in range(samples):
        offset=(k+.5)*spacing/samples
        pos=[(offset+i*spacing)%length for i in range(n)]
        ew,ns,sn=approach_lists(pos,length,width,window)
        both=active=one=False
        for i,de in ew:
            n1=[(j,d) for j,d in sn if j!=i]
            n2=[(j,d) for j,d in ns if j!=i]
            near1=any(abs(d-de)<threshold for _,d in n1)
            near2=any(abs(d-de)<threshold for _,d in n2)
            both |= bool(n1 and n2)
            active |= near1 and near2
            one |= near1 or near2
            for _,d in n1:min_gap1=min(min_gap1,abs(d-de))
            for _,d in n2:min_gap2=min(min_gap2,abs(d-de))
        double_window+=both;double_active+=active;any_active+=one
        two_on_lane+=any(len(ls)>=2 for ls in [ew,ns,sn])
    return dict(length_m=length,N=n,spacing_m=spacing,window_m=window,
                mean_vehicles_in_three_windows=3*window*n/length,
                same_EW_two_windows_pct=100*double_window/samples,
                same_EW_two_distance_triggers_pct=100*double_active/samples,
                at_least_one_distance_trigger_pct=100*any_active/samples,
                any_lane_two_candidates_pct=100*two_on_lane/samples,
                min_distance_difference_EW_SN_m=None if math.isinf(min_gap1) else min_gap1,
                min_distance_difference_EW_NS_m=None if math.isinf(min_gap2) else min_gap2)


def fixture(length,width,n):
    # Replace nearest uniform-grid members to make a deliberate local 3-car encounter.
    targets=[(width/2-42)%length,length/3-28,2*length/3-55]
    pos=[(i+.5)*length/n for i in range(n)]
    ids=[]
    for target in targets:
        choices=[i for i in range(n) if i not in ids]
        j=min(choices,key=lambda i:abs((pos[i]-target+length/2)%length-length/2))
        ids.append(j);pos[j]=target
    return pos,ids


def main():
    cfg=json.loads((ROOT/'config/map.json').read_text())
    for name in ['results','figures']:(ROOT/name).mkdir(exist_ok=True)
    w=cfg['lane_width_m']; W=cfg['coordination_window_m']
    sep=cfg['distance_separation_m'];trigger=sep+cfg['distance_activation_margin_m']
    route,events,shape,radius=at_length(cfg['target_length_m'],w)
    samples=route.sample(cfg['sample_step_m'])
    checks=geometry_check(route,samples,w)
    fine=geometry_check(route,route.sample(cfg['sample_step_m']/2),w)
    assert radius>=50 and 1.2*radius>=60
    assert math.hypot(route.x-w/2,route.y)<1e-8
    counts=[demand(route.s,w,n,W,trigger) for n in cfg['vehicle_count_sweep']]
    windows=[demand(route.s,w,24,ww,trigger) for ww in [40.,60.,80.]]
    lengths=[]
    for target in cfg['length_sweep_m']:
        rr,ee,ss,rad=at_length(target,w)
        row=demand(rr.s,w,24,W,trigger)
        row.update(radius_m=rad,straight_m=1.2*rad,geometry_pass=rad>=50 and 1.2*rad>=60)
        lengths.append(row);map_fig(rr,w,f'map_{target}')
    # Convergence in spatial sweep discretization, not a dynamic simulation.
    coarse=next(x for x in counts if x['N']==24)
    refined=demand(route.s,w,24,W,trigger,2400)
    assert abs(coarse['same_EW_two_distance_triggers_pct']-refined['same_EW_two_distance_triggers_pct'])<.2
    assert coarse['same_EW_two_distance_triggers_pct']>85
    assert next(x for x in counts if x['N']==10)['same_EW_two_distance_triggers_pct']==0
    pos,ids=fixture(route.s,w,24)
    ew,ns,sn=approach_lists(pos,route.s,w,W)
    assert len(ew)==len(ns)==len(sn)==1
    de,dn,ds=ew[0][1],ns[0][1],sn[0][1]
    h1=de-dn-sep;h2=ds-de-sep
    assert abs(h1-2)<1e-8 and abs(h2-1)<1e-8
    sortedpos=sorted(pos)
    mingap=min([(sortedpos[(i+1)%24]-sortedpos[i])%route.s for i in range(24)])
    assert mingap>25
    # Analytic projection of nom=(1,0,2) onto the two distance-HOCBF halfspaces.
    # u_E,u_NS,u_SN; both speeds 10 initially, k1=k2=.5.
    uE=(3+.25*h1-.25*h2)/3
    u=[uE,uE-.25*h1,uE+.25*h2]
    lam1=u[1];lam2=2-u[2]
    assert lam1>=0 and lam2>=0
    assert abs((u[0]-1)-(-lam1+lam2))<1e-10
    assert abs(u[1]-u[0]+.25*h1)<1e-9
    assert abs(u[0]-u[2]+.25*h2)<1e-9
    assert min(u)>=-3 and max(u)<=2
    # Check first held-input interval numerically; no global safety claim.
    for tick in range(51):
        t=tick*.001
        dE=42-10*t-.5*u[0]*t*t;dN=28-10*t-.5*u[1]*t*t;dS=55-10*t-.5*u[2]*t*t
        assert dE-dN-sep>=0 and dS-dE-sep>=0
    rows=[dict(vehicle_id=i,route_s_m=s,speed_mps=10.,local_role=('EW' if i==ids[0] else 'NS' if i==ids[1] else 'SN' if i==ids[2] else 'background')) for i,s in enumerate(pos)]
    cluster=[k*187.5+j*20 for k in range(8) for j in range(3)]
    spatial_gaps=[]
    for e1,e2 in [(w/2,1000.),(w/2,500.)]:
        gaps=[]
        for i,si in enumerate(cluster):
            for j,sj in enumerate(cluster):
                if i==j:continue
                delta=(e2-sj-e1+si)%route.s
                gaps.append(min(delta,route.s-delta))
        spatial_gaps.append(min(gaps))
    assert all(abs(x-y)<1e-8 for x,y in zip(spatial_gaps,[20.75,24.25]))
    assert min(spatial_gaps)>sep
    csv_write(ROOT/'results/cluster_target.csv',[dict(vehicle_id=i,route_s_m=s,speed_mps=10.,group=i//3) for i,s in enumerate(cluster)])
    summary=dict(revision='common_junction_center_distance_barrier',status='offline geometry + spatial demand sweep + local HOCBF algebra; no CARLA simulation',
                 analytic_length_m=route.s,shape=shape,min_radius_m=radius,min_straight_m=1.2*radius,
                 geometry=checks,refined_geometry=fine,events=events,primitives=route.parts,
                 cluster_target=dict(groups=8,group_size=3,intra_group_spacing_m=20.,inter_group_spacing_m=147.5,min_spatial_offset_by_pair_EW_SN_EW_NS_m=spatial_gaps,status='equal-speed spatial construction; not a convergence result'),
                 baseline=dict(N=24,speed_mps=10.,spacing_m=route.s/24,window_m=W,geometry_stress=coarse),
                 fixture=dict(role_ids=ids,min_route_spacing_m=mingap,h1_m=h1,h2_m=h2,psi1_mps=[.5*h1,.5*h2],nominal_acceleration_mps2=[1,0,2],optimal_acceleration_mps2=u,kkt_multipliers=[lam1,lam2]))
    (ROOT/'results/design_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    csv_write(ROOT/'results/count_sweep.csv',counts);csv_write(ROOT/'results/length_sweep.csv',lengths)
    csv_write(ROOT/'results/window_sweep.csv',windows);csv_write(ROOT/'results/initial_positions.csv',rows)
    csv_write(ROOT/'results/route_samples.csv',[dict(zip(['s_m','x_m','y_m','heading_rad','curvature_per_m','primitive_id'],p)) for p in samples])
    def table(name,lines):
        (ROOT/'results'/name).write_text('\n'.join(line+' '+chr(92)*2 for line in lines)+'\n\\bottomrule\n')
    table('count_table.tex',[f"{r['N']} & {r['spacing_m']:.2f} & {r['mean_vehicles_in_three_windows']:.2f} & {r['same_EW_two_windows_pct']:.1f} & {r['same_EW_two_distance_triggers_pct']:.1f}" for r in counts])
    table('length_table.tex',[f"{r['length_m']:.0f} & {r['radius_m']:.2f} & {r['straight_m']:.2f} & {r['same_EW_two_distance_triggers_pct']:.1f} & {'通过' if r['geometry_pass'] else '不满足'}" for r in lengths])
    table('window_table.tex',[f"{r['window_m']:.0f} & {r['same_EW_two_windows_pct']:.1f} & {r['same_EW_two_distance_triggers_pct']:.1f} & {r['any_lane_two_candidates_pct']:.1f}" for r in windows])
    values=dict(RouteLength=route.s,LegLength=route.s/3,NorthWestRadius=shape['NW_radius_m'],NorthEastRadius=shape['NE_radius_m'],SouthRadius=radius,SouthStraight=1.2*radius,LapTime=route.s/10,FleetSpacing=route.s/24,SouthAngle=shape['theta_rad']*180/PI,DualDemand=coarse['same_EW_two_distance_triggers_pct'])
    (ROOT/'results/numbers.tex').write_text(''.join(tex_macro(k,f'{v:.3f}') for k,v in values.items()))
    map_fig(route,w,'map_baseline',vehicles=24);map_fig(route,w,'junction_detail',zoom=True)
    # Distance-only annotated triple encounter (schematic, not to-scale).
    (ROOT/'figures/distance_fixture.tex').write_text(r'''\begin{tikzpicture}[x=.8cm,y=.55cm,>=Latex]
\draw[->,very thick,orange!80!black](5,0)--(-4,0);
\draw[->,very thick,blue!70!black](-.15,4)--(-.15,-4);
\draw[->,very thick,teal](.15,-4)--(.15,4);
\node[fill=orange!80!black,text=white]at(4,0){E};
\node[fill=blue!70!black,text=white]at(-.15,3){NS};
\node[fill=teal,text=white]at(.15,-3){SN};
\fill[red!75!black](0,0)circle[radius=.12];
\node[above left,fill=white]at(-.25,.1){$C=(0,0)$};
\node[above]at(2.5,0){$d_E=42$ m};
\node[left]at(-.15,1.7){$d_{NS}=28$ m};
\node[right]at(.15,-1.7){$d_{SN}=55$ m};
\node[below]at(0,-4.3){$NS\prec E\qquad E\prec SN$};
\end{tikzpicture}''')
    print(json.dumps(summary['baseline'],indent=2));print(json.dumps(summary['fixture'],indent=2))
    print('PASS geometry, spatial sweep refinement, safe initial distance margins, QP KKT and local 50 ms distance replay.')


if __name__=='__main__':main()
