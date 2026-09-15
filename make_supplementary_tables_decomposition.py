#!/usr/bin/env python3
"""Supplementary Tables S4 and S5, built from source_data/SourceData_Decomposition.csv.

S4: the three measures of reach and their decomposition, under three adjustment methods.
S5: the ten pre-specified effect modifiers with unadjusted and Benjamini-Hochberg q values.
"""
import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
rows = list(csv.DictReader((ROOT / "source_data" / "SourceData_Decomposition.csv").open()))


def one(**keys):
    hits = [r for r in rows if all(r[k] == v for k, v in keys.items())]
    if len(hits) != 1:
        raise SystemExit(f"expected one row for {keys}, found {len(hits)}")
    return hits[0]


def pct(x):
    return (math.exp(float(x)) - 1.0) * 100.0


def cell(r):
    """relative difference with its analytic interval where one was estimated"""
    est = f"{pct(r['estimate']):.1f}"
    if r["ci_low"] in ("", None) or r["ci_high"] in ("", None):
        return est
    return f"{est} ({pct(r['ci_low']):.1f} to {pct(r['ci_high']):.1f})"


# ---------------- S4 ----------------
MEASURES = [
    ("any_far_all32", "Cited by any other research area"),
    ("n_macros_other_named31", "Number of other named research areas citing"),
    ("far_all32", "Citations from other research areas"),
    ("far_given_any_far", "Citations from other areas, among papers receiving any"),
]
METHODS = [("ipw", "Weighted"), ("outcome_model_only", "Outcome model"), ("aipw", "Augmented")]

s4 = [r"\begin{table}[H]", r"\centering",
      r"""\caption{\textbf{Three measures of reach and their dependence on the adjustment method.}
Each entry is the percentage difference under narrower-scope relative to broader-scope
publication, with its journal-clustered analytic 95\% interval. Weighted estimates use the
saved propensity weights alone; outcome-model estimates standardize the fitted
journal-group-specific models to the common covariate distribution and their intervals
condition on those fitted predictions, so they are descriptive rather than a claim of greater
precision; augmented estimates combine both and are the values reported in the main text. The
final row is a conditional mean and compares the papers that received such citations under each
journal group, not one fixed population. All rows use the separately regenerated comparison
sample of 3,827,491 papers from 20,215 journals.}""",
      r"\label{tab:decomposition}", r"\footnotesize",
      r"\setlength{\tabcolsep}{5pt}",
      r"\begin{tabular}{lrrr}", r"\toprule",
      r"Measure & Weighted & Outcome model & Augmented \\", r"\midrule"]
for key, label in MEASURES:
    cells = [cell(one(analysis=a, outcome=key, scale="log_mean_ratio")) for a, _ in METHODS]
    s4.append(f"{label} & " + " & ".join(cells) + r" \\")
s4 += [r"\midrule",
       r"\multicolumn{4}{l}{\textit{Decomposition of the citation shortfall}} \\"]
for key, label in (("decomp_entry", "\\quad Entry component"),
                   ("decomp_intensity", "\\quad Intensity component")):
    r = one(analysis="aipw", outcome=key, scale="log_mean_ratio")
    s4.append(f"{label} & \\multicolumn{{3}}{{r}}{{{cell(r)}}} \\\\")
c = one(analysis="aipw", outcome="decomp_contrast", scale="log_ratio_contrast")
s4.append(r"\quad Intensity minus entry & \multicolumn{3}{r}{" + cell(c) + r"} \\")
s4 += [r"\bottomrule", r"\end{tabular}", r"\end{table}", ""]
(ROOT / "tables" / "table_s4_decomposition.tex").write_text("\n".join(s4))

# ---------------- S5 ----------------
LABELS = {
    "reference_entropy_quartile": "Paper reference breadth",
    "author_breadth_quartile": "First- and last-author prior content breadth",
    "author_works_quartile": "Author prior publication count",
    "qwen_macro": "Research area",
    "publication_year": "Publication year",
    "author_citations_quartile": "Author prior citations",
    "institution_citations_quartile": "Institution prior citations",
    "institution_works_quartile": "Institution prior works",
    "team_size_quartile": "Team size",
    "journal_prestige_quartile": "Publishing journal prior prestige",
}
s5 = [r"\begin{table}[H]", r"\centering",
      r"""\caption{\textbf{Ten pre-specified effect modifiers of the primary contrast.}
The modifier list was fixed before estimation. Each row is a global test of whether the
other-area-to-same-topic citation contrast differs across groups of the modifier; $q$ values are
Benjamini--Hochberg adjusted across all ten tests. No test showed clear differences between
groups. Journal prior prestige is a property of the publishing venue, not a measure of author
standing. These tests ask whether the contrast is concentrated in particular papers, authors, or
journals; they do not address whether confounding is present, which can be common to every
group.}""",
      r"\label{tab:modifiers}", r"\footnotesize",
      r"\setlength{\tabcolsep}{6pt}",
      r"\begin{tabular}{lrr}", r"\toprule",
      r"Modifier & $P$ & Benjamini--Hochberg $q$ \\", r"\midrule"]
qs = []
for key, label in LABELS.items():
    p = float(one(analysis="aipw_modifiers", outcome=key, scale="p_value")["estimate"])
    q = float(one(analysis="aipw_modifiers", outcome=key, scale="bh_q")["estimate"])
    qs.append(q)
    s5.append(f"{label} & {p:.3f} & {q:.3f} " + r"\\")
s5 += [r"\bottomrule", r"\end{tabular}", r"\end{table}", ""]
assert min(qs) >= 0.46, f"minimum q changed: {min(qs)}"
(ROOT / "tables" / "table_s5_modifiers.tex").write_text("\n".join(s5))

print(f"wrote tables/table_s4_decomposition.tex and tables/table_s5_modifiers.tex "
      f"(min BH q = {min(qs):.4f})")
