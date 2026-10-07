# Double figure-eight research design

English prose source; shared LaTeX equations, tables and TikZ blocks are retained.


# Abstract and research objective

The reference BSc report evaluates distance-barrier control against a fully actuated signal controller (FAS) on a single-intersection figure-eight track in CARLA. It reports better throughput, delay and energy performance for barrier control, but also transient safety violations at high density. This proposal retains the distance-based speed correction and extends the road to one closed route with two planar intersections. The central question is whether a locally formed platoon remains compatible with a second conflict point after repeated circulation.

The proposed contribution is a controlled study of inter-junction coupling, phase compatibility and transient behavior, rather than a claim of a new safety theorem. The document specifies geometry, event indexing, feedback updates, configuration and matched experiments. All new parameters are design defaults; no new simulation outcomes are presented.


> Three evidence levels are kept separate: reported BSc observations, derived geometric facts, and proposed experimental hypotheses. ``Closed loop'' means both a closed road and repeated state feedback, not online parameter learning.



# Reference report: outline and method


## How the original report is organized

\begin{tabularx}{\linewidth}{P{.26\linewidth}Y}
\toprule
Original section & Role in the argument\\
\midrule
Abstract; Introduction & Motivation, autonomous intersection management and the comparison question.\\
System Overview; Methodology & CARLA map, initialization, vehicle dynamics, controllers, energy model, experimental design and KPI definitions.\\
Results & Validation, individual trajectories, barrier activations and aggregate comparison.\\
Discussion; Conclusion & Platoon explanation, transient safety limitations and future extensions.\\
References; Appendix & Sources, disclosure and configuration table.\\
\bottomrule
\end{tabularx}

The original main file includes Introduction, System Overview, Methodology, Results, Discussion and Conclusion. FigureEight and Barrier Control are methodological source components, not separate top-level chapters. A standalone file named EV Energy USage is effectively empty; the energy model is actually in Methodology. The new report should organize substantive content rather than copy the directory listing.


## Single-intersection model

The reference path is
\[
 x(t)=-R\sin t,\qquad y(t)=-R\sin(2t),\qquad t\in[0,2\pi).
\]
The physical intersection has two route occurrences, at $t=0$ and $t=\pi$. Parametric position is converted to longitudinal arc length using 100,000 samples and interpolation. Vehicles are placed around the route with target spacing $L/N$ and randomized offsets; the intersection is excluded from spawning. The fleet contains Tesla Model 3 and Audi e-tron models, with one extra Tesla for odd $N$.

The headway controller uses an EMA-filtered spatial gap error and a PD speed correction. A longitudinal PID converts speed error into throttle/brake, while look-ahead lateral control follows the route. For two approaching candidates, distances to their respective route occurrences of the crossing are $d_1,d_2$. The report gives
\[
 \Delta d=d_1-d_2,\qquad \nabla=-\frac{1}{\Delta d},\qquad
 u_{b,1}=-\frac{K_b}{\Delta d},\quad u_{b,2}=+\frac{K_b}{\Delta d}.
\]
Corrections activate when both candidates are in the approach window and $|\Delta d|$ is below the activation distance. The nearer candidate accelerates and the farther candidate decelerates. This separates distances, not explicitly predicted arrival times: equal distances with different speeds need not mean equal arrival times. The report does not provide an implementation resolving the singularity at zero.

If the correction is expressed in km/h and distance in metres, $K_b$ must carry units of $(\mathrm{km/h})\,\mathrm{m}$. The original prose labels some gains and even a speed with inconsistent units. Preserve reported numerical settings but correct dimensional notation in this document; do not infer the actual code's internal units.

FAS alternates the two conflict branches, extends green according to detection and gap-out rules, and uses the same vehicle dynamics. Battery energy integrates a mechanical force/power model and approximate motor-efficiency maps. These models are useful comparison tools, but shared approximations do not guarantee that relative energy errors cancel.


# Reported findings and limits

\begin{tabularx}{\linewidth}{P{.25\linewidth}Y}
\toprule
Metric & Original report's observations; not new results\\
\midrule
Throughput & Barrier approximately 0.36--0.57 veh/s across $N=51$--81; FAS approximately 0.32 veh/s at the higher densities.\\
Energy & Reported reductions of 20.12\%, 22.85\%, 39.97\% and 44.81\% for $N=51,61,71,81$.\\
Delay & Reported maximum reduction of 98.86\% at $N=81$, using cumulative lap-delay accounting.\\
Safety violations & Reported mean violations per run: 1.9 at $N=71$ and 21.13 at $N=81$; absent after the reported steady platoon forms.\\
\bottomrule
\end{tabularx}

All values above come from the BSc Results and Discussion \cite{baip}; raw run data and controller scripts were not found in the supplied report directory. A lack of violations after convergence is an empirical observation, not evidence of safety from every initial condition. The 5 m violation criterion is also not identical to a geometric collision. Perfect state estimation, one crossing, no turning choices and simplified energy modeling limit transfer to a larger network.

The report cites Soltani et al. for communication-free intersection management. The verified article describes a dynamic resource acquisition graph, priority function and adaptive tolerance \cite{soltani}. It supports related-work context but does not establish that the report's inverse-distance correction is a formally proven instance of that algorithm.


# Double figure-eight geometry and layout


## One closed route, exactly two intersections

Use a three-lobed planar curve as a precise realization of the requested double figure-eight twist:
\[
 x(\theta)=R\cos\theta,\qquad y(\theta)=H\sin(3\theta),\qquad R,H>0.
\]
Because equal $x$ coordinates imply equal parameters or the pair $\theta,2\pi-\theta$, distinct points coincide only when $\sin(3\theta)=0$. Excluding the ordinary closure, the two crossings are $J_1=(-R/2,0)$ and $J_2=(R/2,0)$. The path is regular everywhere: the two components of its tangent never vanish simultaneously.

\begin{figure}[htbp]
\centering
\begin{tikzpicture}[x=2.35cm,y=2.35cm,>=Latex]
 \draw[gray!18,line width=8pt,samples=501,domain=0:360,smooth,variable=\t] plot ({2*cos(\t)},{sin(3*\t)});
 \draw[navy,line width=.8pt,samples=501,domain=0:360,smooth,variable=\t] plot ({2*cos(\t)},{sin(3*\t)});
 \foreach \a in {18,85,155,198,265,335}{
  \draw[teal,very thick,->] ({2*cos(\a)},{sin(3*\a)}) -- ({2*cos(\a+3)},{sin(3*(\a+3))});}
 \foreach \x/\n in {-1/1,1/2}{
  \draw[amber,dashed,thick] (\x,0) circle (.14);
  \fill[amber] (\x,0) circle (.025);
  \node[fill=white,inner sep=2pt] at (\x,-.30) {$J_{\n}$};}
 \node[font=\small,fill=white] at (0,1.24) {single directed route; arrows show increasing $\theta$};
 \node[font=\small,fill=white] at (0,-1.25) {two planar crossings; no merging or extra junction};
\end{tikzpicture}
\caption{Double figure-eight layout ($R/H=2$). Road width and dashed conflict regions are schematic, not to scale.}
\end{figure}

The schematic has three enclosed lobes; it is not two independent original figure-eights joined by a merge. It expresses the agreed one-route, two-crossing topology. A physical crossing shares road space, but route branches remain fixed: vehicles cannot turn onto another branch. Build in RoadRunner as two fixed crossing junctions with branch-preserving connections and external longitudinal control.


## Scale, curvature and event coordinates

\[
 s(\theta)=\int_0^\theta\sqrt{R^2\sin^2\xi+9H^2\cos^2(3\xi)}\,d\xi,
 \qquad L=s(2\pi).
\]
For $R/H=2$ and $L=4694.8$ m, numerical integration gives $R\approx613.70$ m and $H\approx306.85$ m. The minimum centerline radius is approximately 32.31 m. At 30 km/h, the corresponding kinematic lateral acceleration is approximately 2.15 m/s$^2$; vehicle tracking must still be calibrated. The lane width is a proposed 4 m. These are new design values, not original-report parameters.

\begin{center}
\begin{tabular}{llll}
\toprule
Event & Parameter & Junction / branch & $s$ (m)\\
\midrule
$e_1$ & $\pi/3$ & $J_2/A$ & 722.67\\
$e_2$ & $2\pi/3$ & $J_1/A$ & 1624.73\\
$e_3$ & $4\pi/3$ & $J_1/B$ & 3070.07\\
$e_4$ & $5\pi/3$ & $J_2/B$ & 3972.13\\
\bottomrule
\end{tabular}
\end{center}

\begin{figure}[htbp]
\centering
\begin{tikzpicture}[>=Latex]
 \draw[navy,thick,->] (0,0)--(13,0);
 \foreach \x/\e/\j in {1.7/1/{J_2/A},4.0/2/{J_1/A},7.7/3/{J_1/B},10.0/4/{J_2/B}}{
  \fill[teal] (\x,0) circle (2pt);
  \node[above=3pt] at (\x,0) {$e_{\e}$};
  \node[below=5pt] at (\x,0) {$\j$};}
 \node[above] at (0,0) {$0$};\node[above] at (12.3,0) {$L$};
 \draw[teal,thick,->] (12.3,-.9)--(12.3,-1.35)--(0,-1.35)--(0,-.2);
 \node[fill=white,font=\small] at (6.1,-1.35) {next lap; unwrapped $S$ continues to increase};
\end{tikzpicture}
\caption{Route event order, not a physical map. Each lap has four crossing events.}
\end{figure}

Consecutive event distances are approximately 902.06, 1445.34, 902.06 and 1445.34 m, including wraparound. A geometric junction separation of 613.70 m must not replace these longitudinal distances. At nominal speed, the corresponding travel times are approximately 108.25 and 173.44 s. Event order is $J_2,J_1,J_1,J_2$, not strict alternation.

For every branch, obtain conflict-region entry and exit from the overlapping lane footprints, vehicle dimensions and an explicit margin. Keep these separately from the center-crossing distance used by the barrier. Do not draw a circular region and then assume it defines a validated safety threshold.


# Feedback control at two junctions


## State and event interfaces

Use wrapped position $s_i\in[0,L)$ and unwrapped position $S_i=s_i+n_iL$. Each encounter has an event ID, junction ID, branch ID and lap index. Track route progress using the previous branch and a local projection window; nearest Euclidean point alone is ambiguous at a crossing. Center-crossing distance is the signed difference between the encounter coordinate and $S_i$.

\begin{tabularx}{\linewidth}{P{.23\linewidth}Y}
\toprule
Module & Minimum interface\\
\midrule
State mapping & Vehicle ID, timestamp, $S_i$, $v_i$, branch/event ID, measured body dimensions.\\
Local candidate selection & For each junction: nearest approaching candidate per branch within $D_a$; occupied branches logged separately.\\
Speed correction & Two distances, gain, activation and saturation; output signed correction and activation flag.\\
Execution and logging & Target and actual speed, throttle/brake, saturation, event crossing, rear clearance, collision and proximity records.\\
\bottomrule
\end{tabularx}

The simulator may provide complete state for experiment orchestration. The barrier's decision input remains local own/conflicting-vehicle state, route geometry and a fixed branch tie rule; it does not use downstream queues or a central schedule. Ideal availability of local measurements is assumed first. This is not a demonstrated onboard perception system.


## An explicit engineering variant

Because original code is unavailable, label the following as a regularized distance-barrier baseline, not exact reproduction. Set $\varepsilon=0.1$ m as a numerical design default. If $|\Delta d|\ge\varepsilon$, use $\widehat{\Delta d}=\Delta d$. Otherwise set its magnitude to $\varepsilon$ with the observed sign; at exact equality, assign branch A to pass first, hence $\widehat{\Delta d}=-\varepsilon$.
\[
 u_{b,1}=\operatorname{clip}\!\left(-K_b/\widehat{\Delta d},-7,7\right),\quad
 u_{b,2}=-u_{b,1}\quad (\mathrm{km/h}).
\]
For a non-candidate or inactive pair, $u_b=0$. Compute one command per vehicle:
\[
 v_i^{cmd}=\operatorname{clip}\!\left(30+u_{h,i}+u_{b,i},0,40\right)\quad(\mathrm{km/h}),
 \qquad |u_{h,i}|\le10\ \mathrm{km/h}.
\]
The 40 km/h command ceiling and additive fusion are proposed choices, not confirmed original settings. Retain the report's PD/PID numbers initially, declare gap error as actual minus target spacing, and use metres/seconds for gap derivatives. Convert explicitly when entering a km/h speed loop. EMA is defined here as filtered error $\bar e_k=0.9\bar e_{k-1}+0.1e_k$; the original alpha convention is unknown.

Do not claim that a nominal barrier gain ``dominates'' headway control: saturation and opposite corrections may cancel it. Log the two components before fusion and the final clipped speed. The tie rule, reciprocal regularization and nearest-candidate reduction are heuristics, not collision-avoidance proofs. Downstream occupants remain in the occupancy ledger until their rear clears, but that ledger alone does not change the distance law or guarantee safe release.


## Update order and propagation mechanism

\begin{figure}[htbp]
\centering
\begin{tikzpicture}[>=Latex,node distance=5mm,
 box/.style={draw=navy,rounded corners=2pt,align=center,font=\small,text width=31mm,minimum height=15mm},
 arr/.style={->,thick,teal}]
 \node[box] (state) {Measured states\\route mapping};
 \node[box,right=of state] (local) {$J_1$, $J_2$\\local candidates};
 \node[box,right=of local] (speed) {Headway + barrier\\one speed command};
 \node[box,right=of speed] (plant) {PID + CARLA\\advance 0.05 s};
 \draw[arr] (state)--(local);\draw[arr] (local)--(speed);\draw[arr] (speed)--(plant);
 \draw[arr] (plant.south)--++(0,-.7)-|(state.south);
 \node[font=\small,fill=white] at ($(local.south)!0.5!(speed.south)+(0,-.7)$) {remeasure, do not reuse stale state};
\end{tikzpicture}
\caption{Synchronous state feedback; junction computations use the same snapshot.}
\end{figure}

\begin{enumerate}
\item Read one snapshot; update unwrapped progress, predecessor gaps and encounter/occupancy records.
\item Select local candidates independently at both junctions from that snapshot.
\item Compute headway and local barrier corrections, fuse once and execute throttle/brake commands.
\item Advance the physics by one step; detect crossing and rear-clearance transitions without resetting the same encounter prematurely.
\item Record actual response and safety events, then repeat using newly measured states.
\end{enumerate}

With 20--60 m windows, consecutive events are separated by much more than twice the window length in the proposed geometry. A vehicle therefore receives at most one local barrier correction at a time. Long-range effects arise through changed travel times and predecessor gaps, not simultaneous summation of junction commands. Any enlarged-window case that violates this separation is outside the present baseline.

A correction at $J_1$ changes speed and spacing before a later $J_2$ encounter; repeated circulation returns those changes to $J_1$. Consecutive visits to the same junction also matter. Hypotheses are: compatible phases permit low-intervention circulation; incompatible phases cause recurring interventions; higher density or asymmetric path lengths amplify the coupling. All three must be tested, not asserted.

\Needspace{16\baselineskip}

# Configuration and matched experiments


## Parameter register

\begin{longtable}{P{.34\linewidth}P{.33\linewidth}P{.23\linewidth}}
\toprule
Parameter & Value & Status\\
\midrule\endhead
Reference track length & 2347.4 m & BSc report\\
Double track length; width & 4694.8 m; 4 m & Proposed\\
$R/H$ & 2; diagnostics: 1.5, 3 & Proposed\\
Target speed; timestep & 30 km/h; 0.05 s & BSc report\\
Duration; preparation; ramp & 1800 s; 5 s; 12.5 s & BSc report\\
Single-junction counts & 51, 61, 71, 81 & BSc report\\
Double-junction counts & 102, 122, 142, 162 & Density matched\\
Spawn noise; repetitions & $\pm20\%$; 30 & BSc report\\
$K_b$; $D_{activation}$; $D_a$ & 25; 10 m; 20 m & Appendix B\\
Barrier correction limit & $\pm7$ km/h & BSc Discussion\\
Headway PD; EMA & 3.5, 1.0; 0.9 & Numbers from Appendix\\
Longitudinal PID & 0.5, 0.25, 0.02 & Numbers from Appendix\\
Regularization; speed ceiling & 0.1 m; 40 km/h & Engineering variant\\
Command units, EMA convention & Explicit variant definitions & Original code unknown\\
\bottomrule
\end{longtable}

FAS defaults from the original Appendix B are: stop line 12 m upstream, approach window 50 m, reaction time 1 s, assumed deceleration 2.5 m/s$^2$, minimum/maximum green 12/45 s, yellow 4 s, gap-out 3.4 s, upstream detector offset 30 m, request loop length 10 m and discharge loop length 5 m. Appendix B also lists a ``maximum yellow time'' of 1 s, inconsistent with yellow 4 s. Use 4 s in the declared engineering baseline and retain the 1 s entry as an unresolved source discrepancy. Apply the same independent FAS to each junction; no green-wave offsets.

Freeze the installed CARLA/RoadRunner versions, map export settings, vehicle blueprints and physics parameters after a smoke test. The original report does not identify a CARLA version. Keep throttle/brake mutually exclusive and avoid velocity overrides after initialization. Record simulator collision protection, intervention, removal and respawn behavior rather than attributing it to the controller.


## Experiment stages and controls

\begin{enumerate}
\item Reference check: rebuild the original single-junction geometry and run the regularized barrier and FAS at the four original counts. Compare qualitative trajectories; exact numeric reproduction remains unclaimed without original code.
\item Primary double-junction experiment: compare regularized barrier and independent FAS at the four doubled counts. Use 30 paired seeds (0--29), with identical spawn/type assignments within each comparison. Use separate tuning seeds 100--109.
\item Geometry diagnostic: hold $L$, density and controller fixed; vary $R/H$ over 1.5, 2, 3. At 1.5 the minimum radius is about 20.21 m, so tracking and lateral acceleration are a confound. Calibrate before use; if the common speed is infeasible, classify it as a geometry stress case, not a clean coupling comparison.
\item Control-window diagnostic: vary $D_a=20,40,60$ m at fixed geometry and density, leaving gain and activation distance unchanged. Repeat at $N-1$ and $N+1$ to examine initialization phase/parity, separately from the matched-density main experiment.
\end{enumerate}

At doubled $L$ and $N$, target center spacing $L/N$ remains the original value. Even counts use equal type numbers. Odd diagnostics use one extra Tesla. Treat spacing as center-to-center unless explicitly converting to bumper gap. Use safe spawn screening outside both conflict regions with full vehicle footprints; do not snap several vehicles to the same safe waypoint. Reject and resample an entire infeasible placement with deterministic attempt indexing, recording every rejection.

Primary runs last 1800 s. Report initialization/ramp separately, the early transient through 600 s, and the later 600--1800 s window, without automatically calling it steady state. A declared non-convergence follow-up may extend every seed of an affected condition to 3600 s; do not extend only favorable runs.


# Metrics, analysis and acceptance tests


## Comparable network accounting

Count passage once per vehicle/event/lap using a signed-distance transition, rather than counting frames spent near a crossing. Report each $Q_j=C_j/T$ separately, plus route lap completions $Q_{lap}$. A lap has two crossing events in the original geometry and four in the new one. Consequently the sum $Q_1+Q_2$ cannot alone demonstrate a throughput improvement over the single intersection. At uniform target speed the kinematic references are $Q_{lap}=Nv^*/L$ and total crossing rate $4Nv^*/L$ for the new path. They are nominal-speed references, not strict upper bounds when commanded speeds exceed $v^*$.

Delay is actual completed-lap time minus a one-vehicle free-flow lap time on the same geometry and tracking setup. Also report incomplete laps and elapsed time; clipping negative delay to zero must not be silently introduced. Energy is total battery kWh divided by actual traveled kilometres, with type-stratified results. Report collision contacts, overlapping occupancy of conflicting branches and the original-style 5 m proximity threshold separately. Because the source does not define its exact proximity implementation, use a declared new criterion: at one candidate's center crossing, count an event if the opposite approaching candidate is less than 5 m from its center crossing, deduplicated by vehicle pair and encounter. This is a proximity event, not a reproduced original collision count.

Track activation frequency, headway RMS error, minimum body clearance, speed/acceleration variability, command saturation and stops (speed below 0.1 m/s for at least 1 s). Operational convergence means all center-spacing errors stay within 2.5 m and no barrier activation occurs for at least one nominal full-lap duration. This is a measured criterion, not stability proof. Use cross-correlation or event-aligned changes in speed/gap between junctions to estimate propagation delay; distinguish association from causality.

Compute metrics per seed first. Report means and paired method differences with seed-level bootstrap 95\% intervals (10,000 resamples, fixed analysis seed 20261007). Do not treat vehicle observations as independent experimental repetitions. Preserve all failed runs, controller interventions and uncompleted trajectories.


## Required scenarios before batch experiments

\begin{tabularx}{\linewidth}{P{.35\linewidth}Y}
\toprule
Scenario & Acceptance observation\\
\midrule
One vehicle, multiple laps & Exactly four events per lap; no false pairs or progress jumps.\\
Equal distance; unequal speeds & Finite deterministic commands; differing behavior is logged, not declared safe.\\
Crossing and lap boundary & Correct branch IDs, one crossing count and rear-clearance retention.\\
Two followers and a crossing car & Headway/barrier cancellation, saturation and collisions remain visible.\\
Dense randomized initialization & Safe spawning; transient violations and rejected placements reported.\\
One-junction speed perturbation & Follow perturbation through downstream visits and back around the loop.\\
0.05 s versus 0.025 s replay & Check sampling sensitivity and independent body/occupancy events.\\
\bottomrule
\end{tabularx}

\clearpage

# Implementation roadmap and decision boundary

\begin{enumerate}
\item Geometry milestone: generate the curve and arc-length table, verify exactly two crossings, four encounters, curvature and branch connections; calibrate one vehicle.
\item Control milestone: implement the declared regularized baseline and independent FAS, verify state/event bookkeeping, then test transient failure cases.
\item Experiment milestone: freeze configuration and tuning, execute paired seeds, analyze efficiency together with safety and convergence.
\item Extension milestone: only after diagnosing the coupling, consider local adaptive gain or occupancy-aware release as separately named variants. Shared-state junction coordination and acceleration-QP filtering remain outside the present method.
\end{enumerate}

A useful study may discover a failure boundary rather than improved performance. The main deliverable is an auditable relationship between geometry, density, local interventions and global circulation. If repeated interventions persist or transient safety worsens, report those outcomes and narrow the operating domain before adding more junctions.


# Appendix: files, pseudocode and open items

\begingroup\small
The editable package includes the main file (main.tex), bilingual body (report\_body.tex), bibliography (references.bib), design register (proposed\_config.json), geometry results (geometry\_summary.json), and checker (geometry\_check.py). The body is rendered twice with one language switch, sharing formulas and TikZ geometry. Build with \texttt{latexmk -xelatex main.tex}.

\begin{quote}\small
Initialize map, vehicles, event ledger and logs. For each synchronous tick: snapshot state; map route progress; update predecessor and occupancy records; select the two local pairs; calculate PD and active regularized corrections; fuse/clamp the speed once; execute PID throttle/brake; advance CARLA; record actual response and events. After each run: preserve failures and unfinished laps; aggregate per seed.
\end{quote}

Open items before executable experiments: original controller code and signal phase details; speed-loop units and PID discretization; EMA convention; handling of rear occupancy; original proximity counter; map export/version compatibility; blueprint dimensions and per-type braking/tracking calibration. No executable API is added to the project by this document. The JSON is a design register, not a working CARLA configuration.
\endgroup
