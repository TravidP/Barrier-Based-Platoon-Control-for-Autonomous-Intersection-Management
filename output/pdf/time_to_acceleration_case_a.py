"""Reproduce the local Case A QP and sampled updates; Python standard library only.

Run beside the accompanying .tex file. This is a short positive-speed example,
not a full intersection simulator or a collision-safety certificate.
"""
import csv
import itertools
from pathlib import Path


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def solve_linear(matrix, rhs):
    n = len(rhs)
    a = [list(row) + [value] for row, value in zip(matrix, rhs)]
    for k in range(n):
        pivot = max(range(k, n), key=lambda i: abs(a[i][k]))
        if abs(a[pivot][k]) < 1e-11:
            return None
        a[k], a[pivot] = a[pivot], a[k]
        factor = a[k][k]
        a[k] = [v / factor for v in a[k]]
        for i in range(n):
            if i != k:
                factor = a[i][k]
                a[i] = [x - factor * y for x, y in zip(a[i], a[k])]
    return [a[i][-1] for i in range(n)]


def project_qp(nominal, rows, rhs):
    """Minimize 0.5 ||u-nominal||^2 subject to rows*u >= rhs.

    Enumerate independent active sets (at most n rows in R^n), and
    check primal feasibility plus nonnegative KKT multipliers.
    """
    best = None
    for size in range(len(nominal) + 1):
        for ids in itertools.combinations(range(len(rows)), size):
            active = [rows[i] for i in ids]
            multipliers = solve_linear(
                [[dot(a, b) for b in active] for a in active],
                [rhs[i] - dot(rows[i], nominal) for i in ids],
            ) if size else []
            if multipliers is None or any(v < -1e-9 for v in multipliers):
                continue
            u = [nominal[j] + sum(lam * row[j] for lam, row in zip(multipliers, active))
                 for j in range(len(nominal))]
            if any(dot(row, u) < b - 1e-9 for row, b in zip(rows, rhs)):
                continue
            objective = 0.5 * sum((x-y)**2 for x, y in zip(u, nominal))
            if best is None or objective < best[0]:
                best = (objective, u, ids, multipliers)
    if best is None:
        raise RuntimeError('QP infeasible: coordination / initial state must be reconsidered')
    return best


def main():
    # Distances: A to c1, A to c2, B to c1, C to c2.
    d = [50.0, 54.0, 28.0, 76.0]
    v = [10.0, 10.0, 10.0]
    desired = [12.0, 10.0, 12.0]
    dt = 0.1
    records = []
    min_sampled_h = float('inf')
    for k in range(11):
        ta1, ta2, tb, tc = d[0]/v[0], d[1]/v[0], d[2]/v[1], d[3]/v[2]
        h1, h2 = ta1-tb-2.0, tc-ta2-2.0
        nominal = [0.5*(target-speed) for target, speed in zip(desired, v)]
        rows = [
            [-d[0]/v[0]**2, d[2]/v[1]**2, 0.0],
            [d[1]/v[0]**2, 0.0, -d[3]/v[2]**2],
        ]
        rhs = [-h1, -h2]  # kappa = 1 s^-1
        for j in range(3):
            lower, upper = [0.0]*3, [0.0]*3
            lower[j], upper[j] = 1.0, -1.0
            rows.extend([lower, upper])
            rhs.extend([-3.0, -2.0])  # -3 <= u_j <= 2 m/s^2
        objective, u, active, multipliers = project_qp(nominal, rows, rhs)
        assert min(v) > 0 and min(d) > 0
        assert h1 >= 0 and h2 >= 0
        assert abs((d[1]-d[0])-4.0) < 1e-10
        if k == 0:
            assert active == (0, 1)
            assert all(abs(x-y)<1e-10 for x,y in zip(u, [
                0.5963529277149792, 0.35063022806246275, 0.6868823433764326]))
            print('Initial solution:', u, 'multipliers:', multipliers)
        records.append([k*dt, *d, *v, *nominal, h1, h2, *u])
        if k == 10:
            break
        # Fine replay checks time-margin values inside each held-input interval.
        # This finite numerical check is not a continuous-time proof.
        for substep in range(101):
            s = dt*substep/100
            vs = [x+s*a for x,a in zip(v,u)]
            ds = [x-v[j]*s-0.5*u[j]*s*s for x,j in zip(d,[0,0,1,2])]
            margins = [ds[0]/vs[0]-ds[2]/vs[1]-2,
                       ds[3]/vs[2]-ds[1]/vs[0]-2]
            min_sampled_h = min(min_sampled_h, *margins)
        d = [x-v[j]*dt-0.5*u[j]*dt**2 for x,j in zip(d,[0,0,1,2])]
        v = [x+a*dt for x,a in zip(v,u)]
    out = Path(__file__).resolve().parent
    with (out/'time_to_acceleration_case_a.csv').open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['t','d_A1','d_A2','d_B1','d_C2','v_A','v_B','v_C',
                         'nom_A','nom_B','nom_C','h_1','h_2','u_A','u_B','u_C'])
        writer.writerows(records)
    print('t, h1, h2, uA, uB, uC')
    for k in [0,1,2,5,10]:
        r = records[k]
        print(' '.join(f'{x:.6f}' for x in [r[0], *r[11:]]))
    print('Minimum time margin in 1 ms replay:', min_sampled_h)
    assert min_sampled_h > 0


if __name__ == '__main__':
    main()
