"""Four directed lanes, four conflict points; local 1-second QP example.
Run with Python 3 beside time_to_acceleration_case_a.py. Standard library only.
"""
import csv
from pathlib import Path
from time_to_acceleration_case_a import project_qp, dot

# Variables: A(EW), B(SN), C(NS), D(WE). Each pair: leader, follower.
PAIRS = [(1, 0), (0, 2), (2, 3), (1, 3)]
# Entry distances and path offsets for c1,c2,c3,c4.
OFFSETS = [(4, 0), (4, 0), (4, 0), (0, 4)]


def constraints(d, v):
    rows, h, times = [], [], []
    for (i, j), (oi, oj) in zip(PAIRS, OFFSETS):
        di, dj = d[i] + oi, d[j] + oj
        ti, tj = di/v[i], dj/v[j]
        row = [0.0]*4
        row[i], row[j] = di/v[i]**2, -dj/v[j]**2
        rows.append(row)
        h.append(tj-ti-2.0)
        times.append((ti, tj))
    return rows, h, times


def main():
    # Distance to first conflict on each path; second conflict is 4 m farther.
    d, v = [50., 24., 76., 102.], [10.]*4
    desired, dt = [12., 10., 12., 12.], 0.1
    records, replay_min = [], float('inf')
    for k in range(11):
        rows, h, times = constraints(d, v)
        nom = [.5*(target-speed) for target, speed in zip(desired, v)]
        full_rows, rhs = list(rows), [-x for x in h]
        for i in range(4):
            lo, hi = [0.]*4, [0.]*4
            lo[i], hi[i] = 1., -1.
            full_rows.extend([lo, hi]); rhs.extend([-3., -2.])
        _, u, active, multipliers = project_qp(nom, full_rows, rhs)
        residual = [dot(row,u)+x for row,x in zip(rows,h)]
        assert min(h) >= 0 and min(residual) > -1e-9
        assert min(v)>0 and min(d)>0
        if k in (0, 1):
            print('t=',k*dt,'d=',d,'v=',v,'T=',times)
            print('nom=',nom,'rows=',rows,'h=',h)
            print('u=',u,'active=',active,'multipliers=',multipliers,'residual=',residual)
        if k == 0:
            assert active == (0,1,2)
        records.append([k*dt,*d,*v,*nom,*h,*u,*residual])
        if k==10:
            break
        for substep in range(101):
            s=dt*substep/100
            ds=[x-speed*s-.5*a*s*s for x,speed,a in zip(d,v,u)]
            vs=[speed+a*s for speed,a in zip(v,u)]
            replay_min=min(replay_min,*constraints(ds,vs)[1])
        d=[x-speed*dt-.5*a*dt*dt for x,speed,a in zip(d,v,u)]
        v=[speed+a*dt for speed,a in zip(v,u)]
    with Path(__file__).with_suffix('.csv').open('w',newline='') as f:
        w=csv.writer(f)
        w.writerow(['t'] + [f'{name}_{i}' for name in ['d_first','v','nom'] for i in ['A','B','C','D']]
                   + [f'h_{i}' for i in range(1,5)] + [f'u_{i}' for i in ['A','B','C','D']]
                   + [f'residual_{i}' for i in range(1,5)])
        w.writerows(records)
    print('Selected rows: t, h1..h4, uA..uD')
    for k in [0,1,2,5,10]:
        r=records[k]
        print(' '.join(f'{x:.6f}' for x in [r[0],*r[13:21]]))
    print('Minimum margin in 1 ms numerical replay:',replay_min)
    assert replay_min>0


if __name__=='__main__':
    main()
