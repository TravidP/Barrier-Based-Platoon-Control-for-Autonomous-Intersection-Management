"""Validate the proposed centerline; no CARLA or controller simulation.

Run in this directory: python3 geometry_check.py
Only overwrites the generated geometry_summary.json next to this script.
"""
import json
import math
from pathlib import Path


def derive(ratio, length=4694.8, samples=120000):
    step = 2 * math.pi / samples
    speeds = [math.hypot(ratio * math.sin(k * step),
                         3 * math.cos(3 * k * step))
              for k in range(samples + 1)]
    cumulative = [0.0]
    for k in range(samples):
        cumulative.append(cumulative[-1] + (speeds[k] + speeds[k + 1]) * step / 2)
    scale = length / cumulative[-1]
    R, H = ratio * scale, scale
    events = [math.pi / 3, 2 * math.pi / 3,
              4 * math.pi / 3, 5 * math.pi / 3]
    event_s = [cumulative[round(t / step)] * scale for t in events]
    legs = [event_s[k + 1] - event_s[k] for k in range(3)]
    legs.append(length + event_s[0] - event_s[-1])
    max_curvature = 0.0
    for k in range(samples):
        t = k * step
        dx, dy = -R * math.sin(t), 3 * H * math.cos(3 * t)
        ddx, ddy = -R * math.cos(t), -9 * H * math.sin(3 * t)
        assert dx * dx + dy * dy > 0
        curvature = abs(dx * ddy - dy * ddx) / (dx * dx + dy * dy) ** 1.5
        max_curvature = max(max_curvature, curvature)
    for first, second in [(0, 3), (1, 2)]:
        p = [(R * math.cos(events[j]), H * math.sin(3 * events[j]))
             for j in (first, second)]
        assert math.dist(*p) < 1e-8
    assert abs(sum(legs) - length) < 1e-7
    assert min(legs) > 2 * 60
    radius = 1 / max_curvature
    return {
        "aspect_ratio_R_over_H": ratio, "length_m": length,
        "R_m": R, "H_m": H,
        "intersection_centers_xy_m": [[-R / 2, 0], [R / 2, 0]],
        "event_ids": ["e1", "e2", "e3", "e4"],
        "event_junction_branch": ["J2/A", "J1/A", "J1/B", "J2/B"],
        "event_theta_rad": events, "event_arc_length_m": event_s,
        "consecutive_event_distances_m": legs,
        "nominal_event_travel_times_s": [d / (30 / 3.6) for d in legs],
        "minimum_centerline_radius_m": radius,
        "max_kinematic_lateral_acceleration_at_30kmh_mps2": (30 / 3.6) ** 2 / radius,
        "nominal_lap_time_s": length / (30 / 3.6),
        "arc_integration_samples": samples,
        "crossings_per_lap": 4,
        "proof_note": "Equal cosines give theta and 2pi-theta; equality in y gives sin(3theta)=0. Excluding closure, exactly two distinct crossings.",
    }


if __name__ == "__main__":
    config = json.loads(Path(__file__).with_name("proposed_config.json").read_text())
    reference_N = config["experiments"]["reference_counts"]
    doubled_N = config["experiments"]["double_counts"]
    for before, after in zip(reference_N, doubled_N):
        assert after == 2 * before
        assert abs(2347.4 / before - 4694.8 / after) < 1e-10
    output = {
        "status": "geometric_checks_only_not_CARLA_validated",
        "main": derive(2),
        "geometry_diagnostics": [derive(1.5), derive(3)],
        "matched_target_spacing_m": [2347.4 / n for n in reference_N],
        "checks": {
            "regular_centerline": True, "two_crossing_pairs": True,
            "arc_segments_sum_to_length": True,
            "approach_windows_20_40_60m_do_not_overlap": True,
            "reference_and_double_density_match": True,
        },
    }
    dest = Path(__file__).with_name("geometry_summary.json")
    dest.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n")
    print("Geometry checks passed; generated", dest.name)
    print("R=%.2f m H=%.2f m minimum radius=%.2f m" %
          (output["main"]["R_m"], output["main"]["H_m"],
           output["main"]["minimum_centerline_radius_m"]))
