#!/usr/bin/env python3
"""Supplementary Tables S1-S3 as LaTeX (booktabs), generated from source_data/.

S1  characteristics of the two journal groups in the primary comparison sample, before and after weighting
S2  propensity-model candidates: support, effective sample size, balance, weights
S3  sensitivity and identification-boundary estimates
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "source_data"
OUT = ROOT / "tables"
OUT.mkdir(exist_ok=True)


def read(name):
    with (DATA / name).open(newline="") as handle:
        return list(csv.DictReader(handle))


def one(rows, **keys):
    hit = [r for r in rows if all(r[k] == v for k, v in keys.items())]
    if len(hit) != 1:
        raise SystemExit(f"expected one row for {keys}, got {len(hit)}")
    return hit[0]


def esc(s):
    return s.replace("&", "\\&").replace("%", "\\%")


# ------------------------------------------------------------------ Table S1
bal = [r for r in read("SourceData_ED2_balance.csv") if r["candidate"] == "primary_leaves_63"]
B = {(r["stage"], r["covariate"]): r for r in bal}


def cell(stage, cov):
    return B[(stage, cov)]


# (label, covariate, stage pair, formatter)
def pct(v):
    return f"{100 * float(v):.1f}"


def dec(k):
    return lambda v: f"{float(v):.{k}f}"


def num(v):
    x = float(v)
    return f"{x:,.0f}" if x >= 100 else f"{x:.1f}"


NAT = ("raw_scale_raw", "raw_scale_weighted")
STD = ("raw", "weighted")
rows_spec = [
    ("\\emph{Paper}", None, None, None),
    ("References, count", "reference_count", NAT, num),
    ("Distinct OpenAlex fields among references, count", "reference_fields", STD, dec(2)),
    ("Reference-field entropy", "reference_entropy", STD, dec(2)),
    ("Authors, count", "authors_count", STD, dec(2)),
    ("Countries, count", "countries_count", STD, dec(2)),
    ("Institutions, count", "institutions_count", STD, dec(2)),
    ("International collaboration, \\%", "international", STD, pct),
    ("\\emph{Authors, history through $t-1$}", None, None, None),
    ("Prior works per author, mean", "author_mean_prior_works", NAT, num),
    ("Prior works per author, maximum", "author_max_prior_works", NAT, num),
    ("Prior citations per author, mean", "author_mean_prior_citations", NAT, num),
    ("Prior citations per author, maximum", "author_max_prior_citations", NAT, num),
    ("First- and last-author prior venue scope", "lead_prior_venue_specialization", STD, dec(3)),
    ("First- and last-author prior content breadth", "lead_prior_embedding_breadth", STD, dec(3)),
    ("Author history unavailable, \\%", "lead_prior_venue_missing", STD, pct),
    ("\\emph{Institutions, history through $t-1$}", None, None, None),
    ("Prior works per institution, mean", "institution_mean_prior_works", NAT, num),
    ("Prior works per institution, maximum", "institution_max_prior_works", NAT, num),
    ("Prior citations per institution, mean", "institution_mean_prior_citations", NAT, num),
    ("Prior citations per institution, maximum", "institution_max_prior_citations", NAT, num),
    ("\\emph{Publishing journal, $t-3$ through $t-1$}", None, None, None),
    ("Articles published, count", "history_n", NAT, num),
    ("Prior prestige, mean citations per article", "prior_prestige", NAT, dec(2)),
    ("Open-access share, \\%", "prior_oa_share", STD, pct),
    ("English-language share, \\%", "prior_english_share", STD, pct),
    ("Share of comparison set in narrower-scope journals", "choice_prevalence", STD, dec(3)),
    ("\\emph{Publication year, \\%}", None, None, None),
] + [(str(y), f"publication_year={y}", STD, pct) for y in range(2015, 2021)] + [
    ("\\emph{Lead-author country, \\%}", None, None, None),
    ("United States", "lead_country=US", STD, pct),
    ("China", "lead_country=CN", STD, pct),
    ("India", "lead_country=IN", STD, pct),
    ("Japan", "lead_country=JP", STD, pct),
    ("United Kingdom", "lead_country=GB", STD, pct),
    ("Russia", "lead_country=RU", STD, pct),
    ("Germany", "lead_country=DE", STD, pct),
    ("Not recorded", "lead_country=__MISSING__", STD, pct),
]

lines = [
    "\\begin{table}[H]",
    "\\centering",
    "\\caption{\\textbf{Characteristics of papers in the two journal groups, before and after weighting.}",
    "Primary comparison sample of 3,818,173 papers from 20,203 journals. Unweighted columns describe the",
    "papers as published; weighted columns apply the inverse-probability weights of the selected 63-leaf",
    "propensity model (effective sample sizes 671,512 broader-scope and 1,040,789 narrower-scope). SMD,",
    "standardized mean difference, narrower minus broader, on the scale used in the propensity model",
    "(heavy-tailed counts entered as $\\log(1+x)$); means are shown on the natural scale. All variables",
    "were recorded no later than publication. The 32 SPECTER2 and 32 Qwen3 title-content components,",
    "the 1,000 topic-group indicators, and the remaining lead-country indicators are in the data repository.}",
    "\\label{tab:characteristics}",
    "\\scriptsize",
    "\\renewcommand{\\arraystretch}{0.92}",
    "\\setlength{\\tabcolsep}{4pt}",
    "\\begin{tabular}{@{}lrrrrrr@{}}",
    "\\toprule",
    " & \\multicolumn{3}{c}{Unweighted} & \\multicolumn{3}{c}{Weighted} \\\\",
    "\\cmidrule(lr){2-4}\\cmidrule(l){5-7}",
    " & Broader & Narrower & SMD & Broader & Narrower & SMD \\\\",
    "\\midrule",
]
for label, cov, stages, fmt in rows_spec:
    if cov is None:
        lines.append(f"\\addlinespace[3pt]{label} & & & & & & \\\\")
        continue
    r0, r1 = cell(stages[0], cov), cell(stages[1], cov)
    logcov = f"log1p_{cov}" if stages == NAT else cov
    smd0, smd1 = float(cell("raw", logcov)["smd"]), float(cell("weighted", logcov)["smd"])
    lines.append(f"\\quad {label} & {fmt(r0['mean_broad'])} & {fmt(r0['mean_specialized'])} & {smd0:+.3f}"
                 f" & {fmt(r1['mean_broad'])} & {fmt(r1['mean_specialized'])} & {smd1:+.3f} \\\\")
lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
(OUT / "table_s1_characteristics.tex").write_text("\n".join(lines) + "\n")

# ------------------------------------------------------------------ Table S2
cand = read("SourceData_ED2_propensity_candidates.csv")
names = {"primary_leaves_63": "63 leaves (selected; primary)", "primary_leaves_255": "255 leaves",
         "reference_adjusted": "63 leaves, reference-adjusted", "downstream_deterministic": "63 leaves, regenerated fit"}
lines = [
    "\\begin{table}[H]",
    "\\centering",
    "\\caption{\\textbf{Propensity-model candidates: common support, effective sample size, balance, and weights.}",
    "Candidates were compared without using outcomes; the model with the smaller maximum weighted absolute",
    "standardized mean difference was selected, with the 63-leaf model preferred when the difference was no",
    "more than 0.005. Support is the share of eligible papers with an estimated probability of narrower-scope",
    "publication within 0.05--0.95. Weights are inverse-probability weights within support. The",
    "reference-adjusted model adds the classified final reference list to the adjustment set and defines its",
    "own support; the regenerated fit repeats the primary specification a second time to store",
    "paper-level scores.}",
    "\\label{tab:propensity}",
    "\\footnotesize",
    "\\setlength{\\tabcolsep}{4pt}",
    "\\begin{tabular}{@{}lrrrrrrrr@{}}",
    "\\toprule",
    " & & & \\multicolumn{2}{c}{Effective sample size} & Max. weighted & \\multicolumn{3}{c}{Weight percentile} \\\\",
    "\\cmidrule(lr){4-5}\\cmidrule(l){7-9}",
    "Propensity model & Support, \\% & Papers & Broader & Narrower & abs. SMD & 50th & 95th & 99th \\\\",
    "\\midrule",
]
for key in ("primary_leaves_63", "primary_leaves_255", "reference_adjusted", "downstream_deterministic"):
    r = one(cand, candidate=key)
    lines.append(f"{names[key]} & {100 * float(r['support']):.1f} & {int(r['support_n']):,} & "
                 f"{float(r['ess_broad']):,.0f} & {float(r['ess_specialized']):,.0f} & {float(r['max_weighted_abs_smd']):.3f} & "
                 f"{float(r['weight_p50']):.2f} & {float(r['weight_p95']):.2f} & {float(r['weight_p99']):.2f} \\\\")
lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
(OUT / "table_s2_propensity.tex").write_text("\n".join(lines) + "\n")

# ------------------------------------------------------------------ Table S3
sens = read("SourceData_ED3_sensitivities.csv")
est = read("SourceData_Figure4_estimates.csv")
same = read("SourceData_Figure4_same_author.csv")


def sv(item, stat):
    return float(one(sens, panel="c" if item in ("Primary", "99.9% winsorized") else "d", item=item, statistic=stat)["value"])


def fmt_ci(e, lo, hi):
    return f"${e:.4f}$ & ${lo:.4f}$ to ${hi:.4f}$"


prim = one(est, evidence="overall", test="primary", level="Later citation distribution")
refd = one(est, evidence="overall", test="primary", level="Published-reference distribution")
refa = one(est, evidence="overall", test="reference_adjusted")
first, last = one(same, author_role="first"), one(same, author_role="last")
rows = [
    ("\\emph{Primary and computational checks}", None),
    ("Primary AIPW estimate (frozen)", (float(prim["estimate"]), float(prim["ci_low"]), float(prim["ci_high"]), f"{int(prim['n']):,} papers, {int(prim['journals']):,} journals")),
    ("Citation counts capped at the 99.9th percentile", (sv("99.9% winsorized", "estimate"), sv("99.9% winsorized", "ci_low"), sv("99.9% winsorized", "ci_high"), "primary sample")),
    ("Regenerated fit (second fit of the same specification)", (sv("Deterministic rerun", "estimate"), sv("Deterministic rerun", "ci_low"), sv("Deterministic rerun", "ci_high"), "3,827,491 papers, 20,215 journals")),
    ("\\emph{Identification boundary}", None),
    ("Same contrast in the published reference lists", (float(refd["estimate"]), float(refd["ci_low"]), float(refd["ci_high"]), "primary sample")),
    ("Citation estimate after adding the reference list to the adjustment set", (float(refa["estimate"]), float(refa["ci_low"]), float(refa["ci_high"]), f"{int(refa['n']):,} papers, {int(refa['journals']):,} journals")),
    ("Same first author, both journal types in the same year and topic group", (float(first["theta"]), float(first["bootstrap_ci_low"]), float(first["bootstrap_ci_high"]), f"{int(first['strata']):,} strata, {int(first['papers']):,} papers")),
    ("Same last author, both journal types in the same year and topic group", (float(last["theta"]), float(last["bootstrap_ci_low"]), float(last["bootstrap_ci_high"]), f"{int(last['strata']):,} strata, {int(last['papers']):,} papers")),
]
lines = [
    "\\begin{table}[H]",
    "\\centering",
    "\\caption{\\textbf{Sensitivity and identification-boundary estimates of the primary contrast.}",
    "$\\theta$ is the log ratio-of-ratios (other-area to same-topic citations, narrower-scope minus",
    "broader-scope journals); the primary value corresponds to a ratio 9.2\\% lower. Intervals are",
    "journal-clustered analytic 95\\% confidence intervals, except the same-author rows, which use 500",
    "author-clustered bootstrap draws. The reference-list row applies the primary estimator to the",
    "classified final reference list instead of later citations. The same-author rows are conditional",
    "Poisson contrasts within author--year--topic-group strata that contained both journal types; they",
    "cover 1.1\\% and 2.0\\% of the regenerated comparison sample. Restoring non-self citations from the",
    "publishing journal and the 1 January date diagnostic are reported in the text.}",
    "\\label{tab:sensitivity}",
    "\\footnotesize",
    "\\setlength{\\tabcolsep}{5pt}",
    "\\begin{tabular}{@{}p{7.3cm}rlp{3.6cm}@{}}",
    "\\toprule",
    "Analysis & $\\theta$ & 95\\% CI & Sample \\\\",
    "\\midrule",
]
for label, val in rows:
    if val is None:
        lines.append(f"\\addlinespace[3pt]{label} & & & \\\\")
    else:
        e, lo, hi, n = val
        lines.append(f"\\quad {label} & {fmt_ci(e, lo, hi)} & {n} \\\\")
lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
(OUT / "table_s3_sensitivity.tex").write_text("\n".join(lines) + "\n")
print("wrote", sorted(p.name for p in OUT.glob("*.tex")))
