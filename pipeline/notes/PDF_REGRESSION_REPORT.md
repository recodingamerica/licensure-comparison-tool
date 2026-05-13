# Podiatry regression — extraction vs human-verified PDF

Comparing 10 hand-transcribed states from the Utah-DPM Westlaw PDF

## AL

| Field | PDF (ground truth) | Ours | Status |
|---|---|---|---|
| `license_required` | `True` | `True` | ✓ |
| `amputation_authorized` | `True` | `chopart_joint_and_below` | ✓ (more specific) — we have more specific enum value |
| `ankle_surgery_authorized` | `True` | `True` | ✓ |
| `anatomical_scope_upper_boundary` | `tibial_tuberosity` | `foot_and_ankle` | ⚠ DIFF |

## AR

| Field | PDF (ground truth) | Ours | Status |
|---|---|---|---|
| `license_required` | `True` | `True` | ✓ |
| `amputation_authorized` | `False` | `foot_entirety_excluded` | ✓ (more specific) — we have more specific enum value |
| `ankle_surgery_authorized` | `False` | `True` | ⚠ DIFF |
| `anatomical_scope_upper_boundary` | `ankle` | `foot_and_ankle` | ✓ |

## AZ

| Field | PDF (ground truth) | Ours | Status |
|---|---|---|---|
| `license_required` | `True` | `True` | ✓ |
| `amputation_authorized` | `False` | `toes_and_parts_of_foot` | ⚠ DIFF |
| `ankle_surgery_authorized` | `True` | `None` | ∅ NULL |
| `anatomical_scope_upper_boundary` | `ankle` | `foot_ankle_and_leg_below_knee` | ✓ |

## CA

| Field | PDF (ground truth) | Ours | Status |
|---|---|---|---|
| `license_required` | `True` | `True` | ✓ |
| `amputation_authorized` | `True` | `chopart_joint_and_below` | ✓ (more specific) — we have more specific enum value |
| `ankle_surgery_authorized` | `True` | `True` | ✓ |
| `anatomical_scope_upper_boundary` | `tibial_tuberosity` | `foot_ankle_and_tendons_inserting_into_foot` | ⚠ DIFF |

## CO

| Field | PDF (ground truth) | Ours | Status |
|---|---|---|---|
| `license_required` | `True` | `True` | ✓ |
| `amputation_authorized` | `False` | `foot_entirety_excluded` | ✓ (more specific) — we have more specific enum value |
| `ankle_surgery_authorized` | `True` | `True` | ✓ |
| `anatomical_scope_upper_boundary` | `tibial_tuberosity` | `foot_ankle_and_soft_tissue_below_mid_calf` | ⚠ DIFF |

## CT

| Field | PDF (ground truth) | Ours | Status |
|---|---|---|---|
| `license_required` | `True` | `True` | ✓ |
| `amputation_authorized` | `True` | `transmetatarsal_and_below` | ✓ (more specific) — we have more specific enum value |
| `ankle_surgery_authorized` | `True` | `True` | ✓ |
| `anatomical_scope_upper_boundary` | `lower_leg` | `foot_ankle_and_soft_tissue_to_myotendinous_junction_triceps_surae` | ⚠ DIFF |

## DE

| Field | PDF (ground truth) | Ours | Status |
|---|---|---|---|
| `license_required` | `True` | `True` | ✓ |
| `amputation_authorized` | `True` | `toes_and_parts_of_foot` | ✓ (more specific) — we have more specific enum value |
| `ankle_surgery_authorized` | `True` | `True` | ✓ |
| `anatomical_scope_upper_boundary` | `tibial_tuberosity` | `foot_and_ankle` | ⚠ DIFF |

## GA

| Field | PDF (ground truth) | Ours | Status |
|---|---|---|---|
| `license_required` | `True` | `True` | ✓ |
| `amputation_authorized` | `True` | `transmetatarsal_and_below` | ✓ (more specific) — we have more specific enum value |
| `ankle_surgery_authorized` | `True` | `True` | ✓ |
| `anatomical_scope_upper_boundary` | `tibial_tuberosity` | `foot_ankle_and_leg_below_knee` | ⚠ DIFF |

## TN

| Field | PDF (ground truth) | Ours | Status |
|---|---|---|---|
| `license_required` | `True` | `True` | ✓ |
| `amputation_authorized` | `False` | `foot_entirety_excluded` | ✓ (more specific) — we have more specific enum value |
| `ankle_surgery_authorized` | `True` | `True` | ✓ |
| `anatomical_scope_upper_boundary` | `distal_tibial_metaphyseal_flair` | `foot_ankle_and_soft_tissue_to_distal_tibial_metaphyseal_flare` | ⚠ DIFF |

## TX

| Field | PDF (ground truth) | Ours | Status |
|---|---|---|---|
| `license_required` | `True` | `True` | ✓ |
| `amputation_authorized` | `False` | `not_authorized` | ✓ (more specific) — we have more specific enum value |
| `ankle_surgery_authorized` | `True` | `None` | ∅ NULL |
| `anatomical_scope_upper_boundary` | `tibial_tuberosity` | `foot_only` | ⚠ DIFF |

## Summary

- **match**: 19 (48%)
- **match_precise**: 9 (22%)
- **diff**: 10 (25%)
- **null**: 2 (5%)

**Agreement rate: 28/40 = 70%**
