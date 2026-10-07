# Decision-barrier framework

## 01. Decision-barrier framework
Barrier-Based Platoon Control for Autonomous Intersection Management.
How are crossing order and speed correction connected?
Idea Note: 2026-07-08. Method explanation and proposed experiments.

## 02. Two layers, one feedback loop
Observe position, speed, lane, and intended path. Keep vehicles inside the approach window whose paths share a conflict. The decision layer determines crossing order. The barrier layer computes the margin and correction. Add the correction to nominal headway control, execute for one sample, and observe again. The approach window is a spatial filter; the activation threshold is a time-margin test.

## 03. Arrival time contains information that distance misses
Two vehicles can each be 30 m from a conflict point. At 10 m/s and 6 m/s, their arrival-time estimates are 3 s and 5 s. Equal distance does not imply simultaneous arrival. Measure distance along the planned path. T=d/max(v,v_min) is a current-speed extrapolation, not collision TTC or a guarantee about vehicle occupancy.

## 04. The decision layer selects a crossing order
For each conflict point, compute T_i^m=d_i^m/max(v_i,v_min). The draft allows a score J_i^m=lambda_1 T_i^m+lambda_2 Q_l+lambda_3 P_l+lambda_4 R_i. Q is queue length, P road priority, and R maneuver priority. Start with J=T: the smallest predicted arrival time goes first. Example: A at 3 s, B at 5 s, C at 7 s. Tie-breaking and order retention remain implementation choices, not established guarantees in the draft.

## 05. Safety margin and activation threshold
The symmetric margin is h_sym=|T_i-T_j|-T_safe. After choosing a before b, the ordered margin is h_ord=T_b-T_a-T_safe. The latter represents both separation and the selected order. h>=h_act: correction off. 0<h<h_act: positive margin, correction active. h<=0: boundary or violation; the original inverse formula is not a recovery rule. The activation test applies only after conflict-relevance filtering.

## 06. Smaller positive margins produce larger corrections
Keep the draft's expression: phi(h)=-1/h for h<h_act, and 0 otherwise. On the positive active branch, approaching zero makes the negative correction stronger. The formula is undefined at zero, changes sign for negative h, and jumps at h_act. Plot only h>0 with h_act=1 s as an illustrative threshold. This is a heuristic response curve.

## 07. From pairwise terms to vehicle control
u_i=u_i^headway+u_i^barrier, with u_i^barrier=sum over m in C_i and j in N_i^m of w_ij^m phi(h_ij^m). C_i contains the relevant conflict points; N_i^m contains the conflicting vehicles at point m. Compute a correction per active pair, then aggregate for vehicle i. The decision layer determines which vehicle yields. In the worked example, only the later vehicle receives a nonzero weight. If u is acceleration, phi has unit s^-1 and w includes a gain with unit m/s.

## 08. Worked example: prediction and correction
Illustrative parameters only. Vehicle A: d=30 m, v=10 m/s, T=3 s. Vehicle B: d=50 m, v=10 m/s, T=5 s. Select A before B. Set T_safe=1.5 s and h_act=1 s. h=5-3-1.5=0.5 s, so the margin is positive but active. phi=-1/0.5=-2 s^-1. Assume zero nominal acceleration, w_A=0, and w_B=0.5 m/s. Then u_A=0 and u_B=-1 m/s^2.

## 09. One feedback step increases the predicted margin
Apply the illustrative accelerations for dt=0.1 s, holding them constant within the sample. d^+=d-v dt-0.5 u dt^2 and v^+=v+u dt. A: d^+=29 m, v^+=10 m/s, T^+=2.9 s. B: d^+=49.005 m, v^+=9.9 m/s, T^+=4.95 s. Recompute h^+=4.95-2.9-1.5=0.55 s. B's deceleration increases the predicted arrival-time gap. The correction is still active; this one step is not a safety proof.

## 10. Boundaries of the original expression
At h=0 the inverse formula is undefined; h<0 reverses its sign. A lower speed bound avoids division by zero but does not validate a stopped vehicle's arrival prediction. Input limits and switching can change the intended correction. Point arrival times do not describe front entry and rear clearance of finite vehicles. Keeping only lane leaders is a proposed simplification that needs verification. The manuscript proposes CBF-QP as a later safety-filter direction; feasibility and model assumptions still need analysis.

## 11. Case A: three directed lanes
A north-south bidirectional road crosses one east-to-west lane. Use separate NS and SN lanes. Two path intersections c1 and c2 connect EW with NS and SN respectively. The movement graph has three nodes and two edges. NS and SN have no crossing conflict with each other under the separated straight-lane assumption. Same-lane following is handled separately.

## 12. Case A: two checks for the EW vehicle
Use EW's path distance to each point, not one common center distance. At c1 evaluate the EW-NS pair; at c2 evaluate the EW-SN pair. Sum the active, priority-weighted corrections. If both are signed braking requests of -1 and -3 m/s^2, their sum is -4 m/s^2, while the strongest individual braking is min(-1,-3)=-3 m/s^2. max(-1,-3)=-1 is weaker braking. These are aggregation illustrations, not bounded safe control laws. Priority consistency across points still needs design.

## 13. Case B: four directed lanes
Order the lanes as NS, SN, EW, WE. The conflict matrix has rows [0,0,1,1], [0,0,1,1], [1,1,0,0], [1,1,0,0]. There are four unique crossing-conflict edges; the symmetric matrix lists each edge twice. Show c1=NS-EW, c2=SN-EW, c3=NS-WE, c4=SN-WE. Turning movements require a new conflict map.

## 14. Case B: candidate selection and online calculation
Select the closest approaching vehicle on each nonempty lane. Draw leaders as filled vehicles and following vehicles as outlines. Use the conflict matrix to select the four unique pairs. For each pair, estimate arrival times, select order, and test the margin. Aggregate active terms for each vehicle, apply the input, and update. Re-select candidates after clearance; an occupying vehicle must remain represented until its rear clears. This occupancy retention is an implementation requirement beyond a literal nearest-approaching-only rule.

## 15. Five experimental stages
S1: reproduce the figure-eight closed-loop reference. S2: open-road Case A, testing stochastic arrivals and two simultaneous conflicts. S3: open-road Case B, testing four interacting approach directions. S4: two-intersection corridor, testing downstream capacity and platoon propagation. S5: multi-intersection network, testing route demand and computational scale. Each stage expands the interaction structure. These are planned tests, not completed results.

## 16. Open-road single-intersection tests
S2 has three incoming directions and S3 has four. Supply matched arrival and route files to every controller. Sweep demand, first with balanced flows, then with an imbalanced dominant approach. Add near-simultaneous arrivals, bursts, and low-speed queues as deterministic stress cases. Observe margins, physical conflicts, delay, stops, and residual queues. Use paired random seeds and report variability. Count requested, admitted, and completed vehicles to avoid hiding unfinished or uninserted demand.

## 17. Corridor and network tests
S4: connect two intersections with a finite-storage link. Track platoon discharge at the first junction, travel to the second, and a queue that can spill back upstream. Test whether local decisions respect downstream capacity. S5: use a small multi-intersection network, with routes crossing several junctions and uneven demand. Increase network size and active conflicts; observe trip delay, queues, deadlock, and computation time. Downstream admission and inter-junction coordination remain future design tasks.

## 18. Baselines and key performance indicators
Baselines: fully actuated signal control; unsignalized priority control; original distance-difference barrier, only where its source and assumptions support reproduction. Ablations: weighted sum, strongest signed braking, and CBF-QP, with the same order rule where feasible.
Efficiency: throughput (veh/h), mean delay (s/veh), total delay (s). Energy: per-vehicle energy using a specified model (Wh/veh). Comfort: acceleration RMS (m/s^2), jerk RMS (m/s^3), and stops per vehicle. Safety: collisions, occupancy conflicts, and minimum arrival-time margin (s). Robustness and cost: deadlock count and computation time (ms). Predicted arrival time is not collision TTC. Match geometry, demand, vehicle limits, and seeds. All performance outcomes remain to be measured.
