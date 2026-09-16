#!/usr/bin/env python3
import csv
import hashlib
import math
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source_data"


def rows(name):
    with (SOURCE / name).open(newline="") as handle:
        return list(csv.DictReader(handle))


def one(table, **keys):
    found = [r for r in table if all(r[k] == v for k, v in keys.items())]
    if len(found) != 1:
        raise ValueError(f"expected one row for {keys}, got {len(found)}")
    return found[0]


def close(value, expected, tolerance=5e-9):
    if not math.isfinite(float(value)) or abs(float(value) - expected) > tolerance:
        raise ValueError(f"expected {expected}, got {value}")


manifest = rows("source_data_manifest.csv")
manifest_names = [item["source_file"] for item in manifest]
if len(manifest_names) != len(set(manifest_names)):
    raise ValueError("source-data manifest contains duplicate file names")
disk_names = {path.name for path in SOURCE.glob("SourceData_*.csv")} | {"round2_score_diagnostics.csv"}
if set(manifest_names) != disk_names:
    raise ValueError(f"source-data manifest mismatch: missing={disk_names - set(manifest_names)} "
                     f"extra={set(manifest_names) - disk_names}")
for item in manifest:
    path = SOURCE / item["source_file"]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != item["sha256"]:
        raise ValueError(f"hash mismatch for {path.name}: {digest}")
    with path.open(newline="") as handle:
        count = sum(1 for _ in csv.DictReader(handle))
    if count != int(item["rows"]):
        raise ValueError(f"row mismatch for {path.name}: {count}")

main_results = rows("SourceData_Figure2.csv")
routing = one(main_results, analysis="primary", outcome="far_to_near_routing")
total = one(main_results, analysis="primary", outcome="total_citations")
other = one(main_results, analysis="primary", outcome="far")
any_other = one(main_results, analysis="primary", outcome="any_far")
close(routing["estimate"], -0.096748438961938)
close(routing["ci_low"], -0.144336408333361)
close(routing["ci_high"], -0.0491604695905151)
close(total["estimate"], -0.665913644723499)
close(other["estimate"], -0.3954427902709403)
close(any_other["estimate"], -0.0057634037078854)
if (int(routing["n"]), int(routing["journals"])) != (3818173, 20203):
    raise ValueError("primary sample or journal count changed")

# Follow-up release: the whole-file lock covers every mean, interval, and provenance cell.
decomp = rows("SourceData_Decomposition.csv")
if hashlib.sha256((SOURCE / "SourceData_Decomposition.csv").read_bytes()).hexdigest() != \
        "1bbd2c95fb0f3e8c744876c21d0b5de7e8ab9d30c53d775cc067712044975f71":
    raise ValueError("frozen follow-up numbers or provenance changed")
if len(decomp) != 123 or len({(r["analysis"], r["outcome"], r["scale"]) for r in decomp}) != 123:
    raise ValueError("follow-up rows must have unique analysis/outcome/scale keys")
for r in decomp:
    for key in ("estimate", "mean_broad", "mean_specialized", "se", "ci_low", "ci_high",
                "bootstrap_ci_low", "bootstrap_ci_high", "n", "journals", "support"):
        if r[key] and not math.isfinite(float(r[key])):
            raise ValueError(f"non-finite follow-up {key}: {r}")
    if r["analysis"] in ("aipw", "ipw", "outcome_model_only", "aipw_modifiers", "aipw_scope_endpoints"):
        if (r["n"], r["journals"]) != ("3827491", "20215"):
            raise ValueError(f"follow-up result assigned to wrong population: {r}")
    for low, high in (("ci_low", "ci_high"), ("bootstrap_ci_low", "bootstrap_ci_high")):
        if bool(r[low]) != bool(r[high]) or (r[low] and float(r[low]) > float(r[high])):
            raise ValueError(f"invalid follow-up interval: {r}")
    if r["analysis"] == "ipw_2015" and (r["n"], r["journals"]) != ("596758", "11635"):
        raise ValueError("ten-year preview denominator changed")
for outcome, broad, specialized, estimate in (
        ("any_far_all32", 0.457967230464232, 0.4534833291600681, -0.0044839013041917735),
        ("far_all32", 2.876300766022177, 2.511252085894811, -0.36504868012741815),
        ("n_macros_other_named31", 1.0252661675871533, 0.9715587253730993, -0.05370744221405405),
        ("n_macros_cited_named31", 1.5201126725907763, 1.4777152522631443, -0.042397420327885314),
        ("far_given_any_far", 6.280582047554873, 5.537694385692442, -0.7428876618624318)):
    r = one(decomp, analysis="aipw", outcome=outcome, scale="absolute")
    close(r["mean_broad"], broad); close(r["mean_specialized"], specialized); close(r["estimate"], estimate)
    close(specialized - broad, estimate)
    logrow = one(decomp, analysis="aipw", outcome=outcome, scale="log_mean_ratio")
    close(logrow["estimate"], math.log(specialized / broad))
aliases = {"decomp_total": "far_all32", "decomp_entry": "any_far_all32",
           "decomp_intensity": "far_given_any_far", "decomp_contrast": "intensity_vs_probability"}
components = {}
for alias, original in aliases.items():
    r = one(decomp, analysis="aipw", outcome=alias)
    source = one(decomp, analysis="aipw", outcome=original, scale=r["scale"])
    if any(r[k] != source[k] for k in r if k != "outcome"):
        raise ValueError(f"plot alias differs from original: {alias}")
    components[alias] = float(r["estimate"])
close(components["decomp_total"], components["decomp_entry"] + components["decomp_intensity"], 1e-10)
close(components["decomp_contrast"], components["decomp_intensity"] - components["decomp_entry"], 1e-10)
close(components["decomp_contrast"], -0.11604529678380808)
if len([r for r in decomp if r["scale"] == "bh_q"]) != 10:
    raise ValueError("expected all ten modifier q values")


def check_time_windows(table):
    times = [r for r in table if r["analysis"] == "ipw_2015"]
    if len(times) != 13:
        raise ValueError("expected thirteen stored 2015-window estimates")
    for r in times:
        k = r["outcome"]
        if k == "theta_120_minus_60":
            expected = "theta_y1_10 minus theta_y1_5: [t0, t0+120 months) versus [t0, t0+60 months)"
        elif k == "theta_y6_10" or k.endswith("_late60_120"):
            expected = "[t0+60 months, t0+120 months)"
        elif k == "theta_y1_10" or k.endswith("_120"):
            expected = "[t0, t0+120 months)"
        elif k == "theta_y1_5" or k.endswith("_60"):
            expected = "[t0, t0+60 months)"
        else:
            raise ValueError(f"unknown 2015-window outcome: {k}")
        if r["window_definition"] != expected:
            raise ValueError(f"wrong window for {k}: {r['window_definition']}")
    early = one(times, outcome="theta_y1_5")
    late = one(times, outcome="theta_y6_10")
    cumulative = one(times, outcome="theta_y1_10")
    change = one(times, outcome="theta_120_minus_60")
    close(early["estimate"], -0.0804370370156886)
    close(late["estimate"], -0.1197628237771873)
    close(cumulative["estimate"], -0.1007728794927285)
    close(change["estimate"], float(cumulative["estimate"]) - float(early["estimate"]), 1e-12)


check_time_windows(decomp)

facts = rows("SourceData_ReportedFacts.csv")
expected_facts = {"complete_comparison_sets": 5872,
                  "scope_volume_within_set_rho": -0.04068635867596675,
                  "scope_prestige_within_set_rho": 0.08339060499968273,
                  "unique_citation_links": 74432171, "unique_citing_papers": 18788419,
                  "reference_ratio_change_percent": -4.302225240047779}
if len(facts) != len(expected_facts):
    raise ValueError(f"expected {len(expected_facts)} reported-fact rows, got {len(facts)}")
for key, expected in expected_facts.items():
    fact = one(facts, claim=key)
    close(fact["value"], expected)
    if not fact["origin"] or not fact["population"]:
        raise ValueError(f"missing reported-fact provenance: {fact}")
reference = one(rows("SourceData_Figure4_estimates.csv"), evidence="overall", test="primary",
                level="Published-reference distribution")
close(one(facts, claim="reference_ratio_change_percent")["value"],
      100 * math.expm1(float(reference["estimate"])))


def check_followup_denominators(text):
    """Guard new-result paragraphs/captions and explicitly named decomposition sections."""
    text = re.sub(r"(?m)(?<!\\)%.*$", "", text).replace("{,}", ",")
    blocks = re.split(r"\n\s*\n", text) + re.findall(r"\\begin\{figure\}.*?\\end\{figure\}", text, re.S)
    blocks += [b for b in re.split(r"(?=\\subsection\{)", text)
               if re.match(r"\\subsection\{[^}]*?(?:Test\s*2|decompos|entry|intensity)", b, re.I)]
    markers = r"decomp_(?:total|entry|intensity)|SourceData_Decomposition|n_macros_other_named31|Test\s*2|1\.025|0\.972|2\.876|2\.511|6\.28|5\.54|(?:12\.7|5\.2|11\.8)\s*\\?%"
    wrong = r"3,?818,?173|20,?203|3\.818\d*\s*(?:million|m\b)"
    for block in blocks:
        if re.search(markers, block, re.I) and re.search(wrong, block, re.I):
            raise ValueError("Test 2/follow-up result paired with primary N; use 3,827,491 papers and 20,215 journals")

annual = rows("SourceData_Figure2_Years.csv")
expected_annual = {
    "2015": (1.3384966209321065, 1.293148704051576, -0.034466959279304654),
    "2016": (1.3344500415313354, 1.2912891755212306, -0.03287817285265471),
    "2017": (1.430931799074527, 1.2704330181818613, -0.11896803825665425),
    "2018": (1.3676921344006296, 1.2565700847106924, -0.08473889175013483),
    "2019": (1.397127781791165, 1.2910895781561853, -0.07893204870375625),
    "2020": (1.5519279726571464, 1.404095301799428, -0.10010482923920283),
}
if len(annual) != 6 or {row["level"] for row in annual} != set(expected_annual):
    raise ValueError("expected exactly six annual Figure 2 rows for 2015-2020")
for row in annual:
    broad, narrow, estimate = expected_annual[row["level"]]
    close(row["far_near_broad"], broad)
    close(row["far_near_specialized"], narrow)
    close(row["estimate"], estimate)
    close(row["year_heterogeneity_p"], 0.6475732248022338)
    close(row["linear_trend_p"], 0.31736520251912625)
    if float(row["estimate"]) >= 0:
        raise ValueError(f"annual contrast changed direction for {row['level']}")

rerun = one(rows("round2_score_diagnostics.csv"), population="all_support", estimator="aipw")
close(rerun["estimate"], -0.08245270348646416)
close(rerun["ci_low"], -0.1282409125520956)
close(rerun["ci_high"], -0.03666449442083273)

enrichment = rows("SourceData_Figure4_DistanceEnrichment.csv")
if len(enrichment) != 17 or enrichment[0]["same_topic"] != "True":
    raise ValueError("distance-enrichment table changed shape")
close(enrichment[0]["log2_ratio_narrow_over_broad"], 0.1511108351, tolerance=1e-6)
close(enrichment[1]["log2_ratio_narrow_over_broad"], 0.2808596545, tolerance=1e-6)
for index, expected in [(0, 11.0), (1, 21.5), (-3, -11.5), (-2, -16.4), (-1, -12.2)]:
    percentage = 100 * (float(enrichment[index]["share_narrow"]) / float(enrichment[index]["share_broad"]) - 1)
    close(round(percentage, 1), expected)
if not all(float(r["log2_ratio_narrow_over_broad"]) < 0 for r in enrichment[-3:]):
    raise ValueError("distant distance bins are no longer depleted under narrower-scope publication")

corridors = rows("SourceData_Figure2_Corridors.csv")
if len(corridors) != 8 or [r["case_rank"] for r in corridors] != [str(i) for i in range(1, 9)]:
    raise ValueError("expected eight outcome-blind corridors ranked 1-8")
cardio = one(corridors, case_rank="7")
if (cardio["display_label"], cardio["broad_name"], cardio["narrow_name"]) != \
        ("Cardiovascular medicine", "Internal Medicine", "Echocardiography"):
    raise ValueError("Figure 2 example corridor changed")
close(cardio["far_near_broad"], 1.20215, tolerance=5e-4)
close(cardio["far_near_specialized"], 1.06090, tolerance=5e-4)
flows = rows("SourceData_ED3_network_edges.csv")
if len(flows) != 1024:
    raise ValueError("expected 1,024 flow cells")
if {(int(r["source_internal_domain_id"]), int(r["citing_internal_domain_id"])) for r in flows} != \
        {(i, j) for i in range(32) for j in range(32)}:
    raise ValueError("flow table must contain every ordered area pair exactly once")
for arm in ("broad", "specialized"):
    close(sum(float(r[f"standardized_share_{arm}"]) for r in flows), 1)
    for area in range(32):
        close(sum(float(r[f"row_share_{arm}"]) for r in flows
                  if int(r["source_internal_domain_id"]) == area), 1)
for col, expected in (("standardized_share_broad", 0.4835), ("standardized_share_specialized", 0.4547)):
    total = sum(float(r[col]) for r in flows)
    off = sum(float(r[col]) for r in flows if r["source_internal_domain_id"] != r["citing_internal_domain_id"])
    close(off / total, expected, tolerance=5e-4)
row_cross = {}
for g, col in (("broad", "standardized_share_broad"), ("narrow", "standardized_share_specialized")):
    tot = {}; same = {}
    for r in flows:
        s_ = r["source_internal_domain_id"]
        tot[s_] = tot.get(s_, 0.0) + float(r[col])
        if s_ == r["citing_internal_domain_id"]:
            same[s_] = float(r[col])
    row_cross[g] = {s_: 1 - same[s_] / tot[s_] for s_ in tot}
if sum(1 for s_ in row_cross["broad"] if s_ != "18" and row_cross["narrow"][s_] < row_cross["broad"][s_]) != 27:
    raise ValueError("area-by-area cross-share count changed")
cloud_areas = rows("SourceData_Figure2_CloudAreas.csv")
if len(cloud_areas) != 32 or sum(int(r["n_sampled"]) for r in cloud_areas) != 1219650:
    raise ValueError("cloud display sample changed")
cloud_leaves = rows("SourceData_Figure2_CloudLeaves.csv")
if len(cloud_leaves) != 1000 or sum(int(r["n_excluded"]) + int(r["n_broad"]) + int(r["n_narrow"]) for r in cloud_leaves) != 7617662:
    raise ValueError("cloud leaf counts changed")
if not (ROOT / "figures" / "cloud_umap_points.npz").is_file():
    raise ValueError("missing figures/cloud_umap_points.npz")

area_year = rows("SourceData_Figure3_AreaYear.csv")
ay_est = [r for r in area_year if r["status"] == "estimated"]
if len(area_year) != 192 or len(ay_est) != 164:
    raise ValueError("area x year cell counts changed")
ay_named = [r for r in ay_est if r["display_label"] != "Mixed records"]
if len(ay_named) != 158 or sum(float(r["estimate"]) < 0 for r in ay_named) != 117 or \
        sum(float(r["ci_high"]) < 0 for r in ay_named) != 27 or \
        sum(float(r["ci_low"]) > 0 for r in ay_named) != 0:
    raise ValueError("area x year summary counts changed")
if [(r["qwen_macro"], r["publication_year"]) for r in ay_named if float(r["q_value_bh"]) < 0.05] != [("25", "2019")]:
    raise ValueError("Figure 4 must mark only the existing BH-significant cell")
if any("Editorial" in r["display_label"] for r in area_year):
    raise ValueError("area x year table uses the internal cluster label")

mixed = rows("SourceData_MixedRecordsDiagnostics.csv")
if int(one(mixed, diagnostic="title_audit_sample", group="all")["value"]) != 200:
    raise ValueError("mixed-record title audit sample changed")
if int(one(mixed, diagnostic="explicit_record_type_signal", group="all")["value"]) != 83:
    raise ValueError("mixed-record title audit count changed")
if int(one(mixed, diagnostic="mixed_cluster_population", group="all")["value"]) != 152090:
    raise ValueError("mixed-record population changed")
close(one(mixed, diagnostic="deterministic_theta", group="mixed_cluster_masked")["value"],
      -0.0841266175603677)

# sensitivity numbers printed in Results
sens = rows("SourceData_ED3_sensitivities.csv")
close(one(sens, panel="c", item="99.9% winsorized", statistic="estimate")["value"], -0.0917645392775518)
close(one(sens, panel="c", item="99.9% winsorized", statistic="ci_low")["value"], -0.1282981682733862)
close(one(sens, panel="c", item="99.9% winsorized", statistic="ci_high")["value"], -0.0552309102817173)
refadj = one(rows("SourceData_Figure4_estimates.csv"), evidence="overall", test="reference_adjusted")
close(refadj["estimate"], -0.0518761010657758)
close(refadj["ci_low"], -0.1040803596759921)
close(refadj["ci_high"], 0.0003281575444403)
if int(refadj["n"]) != 3782942:
    raise ValueError("reference-adjusted sample changed")
same = rows("SourceData_Figure4_same_author.csv")
for role, est, lo, hi in (("first", -0.0142806161819973, -0.1449669059495889, 0.1454876708181516),
                          ("last", -0.0269926133780529, -0.1115173774988909, 0.0707351506323603)):
    r = one(same, author_role=role)
    close(r["theta"], est); close(r["bootstrap_ci_low"], lo); close(r["bootstrap_ci_high"], hi)

# supplementary tables are generated from Source Data; check they exist and carry the locked values
tables = {name: (ROOT / "tables" / name).read_text() for name in
          ("table_s1_characteristics.tex", "table_s2_propensity.tex", "table_s3_sensitivity.tex")}
for name, needle in (("table_s1_characteristics.tex", "3,818,173 papers from 20,203 journals"),
                     ("table_s2_propensity.tex", "671,512 & 1,040,789 & 0.180"),
                     ("table_s3_sensitivity.tex", "$-0.097$ & $-0.144$ to $-0.049$"),
                     ("table_s3_sensitivity.tex", "$-0.052$ & $-0.104$ to $0.0003$")):
    if needle not in tables[name]:
        raise ValueError(f"supplementary table {name} lacks {needle!r}")
for name in ("figure1_measurement_design", "figure2_results", "figure3_mechanism", "figure4_generality",
             "supplementary_figure_s1_sample_construction", "supplementary_figure_s2_balance",
             "supplementary_figure_s3_journal_pairs", "supplementary_figure_s4_area_year",
             "supplementary_figure_s5_map", "supplementary_figure_s6_network"):
    if not (ROOT / "figures" / f"{name}.pdf").exists():
        raise ValueError(f"missing figure {name}")

areas = rows("SourceData_Figure4_Areas.csv")
if len(areas) != 31 or len({r["level"] for r in areas}) != 31 or sum(float(r["estimate"]) < 0 for r in areas) != 27:
    raise ValueError("expected 31 unique named areas, with 27 negative contrasts")

if sys.argv[1:] == ["--source-only"]:
    print(f"validated {len(manifest)} source tables and six reported facts; "
          f"primary theta={float(routing['estimate']):.7f}; n={routing['n']}; journals={routing['journals']}")
    raise SystemExit(0)
if sys.argv[1:]:
    raise ValueError(f"unsupported arguments: {sys.argv[1:]}")
main = (ROOT / "main.tex").read_text()
supp = (ROOT / "supplement.tex").read_text()
for snippet in ("5,872 sets", "$-0.041$", "$0.083$", "more than 74 million",
                "nearly 19 million", "4.3\\% lower"):
    if snippet not in main:
        raise ValueError(f"reported fact missing or changed in main text: {snippet}")
for snippet in ("74,432,171", "18,788,419"):
    if snippet not in supp:
        raise ValueError(f"citation count missing or changed in supplement: {snippet}")
check_followup_denominators(main)
check_followup_denominators(supp)
order = [main.index(f"\\section{{{name}}}") for name in
         ("Introduction", "Results", "Discussion", "Methods")]
if order != sorted(order):
    raise ValueError(f"incorrect section order: {order}")
result_order = [main.index(heading) for heading in
                ("\\subsection{Papers in narrower-scope journals reached",
                 "\\subsection{The largest shortfall was in how heavily other research areas drew",
                 "\\subsection{The direction was widespread and persisted into years six to ten}",
                 "\\subsection{Where the claim stops}")]
if result_order != sorted(result_order):
    raise ValueError(f"incorrect Results order: {result_order}")
if "\\withsupptrue" not in main.split("\\begin{document}", 1)[0].split("\\newif", 1)[1]:
    raise ValueError("default review build must append Supplementary Information")
if "\\includepdf[pages=-]{supplement.pdf}" not in main:
    raise ValueError("review build must include every page of supplement.pdf")
if "Supplementary Figure~S4" not in supp:
    raise ValueError("supplementary area-year reference must point to Figure S4")
cells = [r for r in rows("SourceData_Figure3_AreaYear.csv") if int(r["qwen_macro"]) != 18]
if len(cells) != 186 or len({(r["qwen_macro"], r["publication_year"]) for r in cells}) != 186:
    raise ValueError("expected 186 unique Figure 4 area-year cells")
if sum(r["status"] == "estimated" for r in cells) != 158:
    raise ValueError("expected 158 estimated cells and 28 gray cells in Figure 4")
if "Gray crosses mark 28 cells" not in main or "aligned with the\nheatmap columns" not in main:
    raise ValueError("Figure 4 caption must explain missing cells and aligned year summaries")
if not (ROOT / "figures/supplementary_figure_s4_area_year.pdf").is_file():
    raise ValueError("missing Supplementary Figure S4")
if "SPECTER2 used the hidden state at the first token" not in supp:
    raise ValueError("SI must distinguish SPECTER2 pooling from Qwen3 last-token pooling")
if "Reference entropy was also analyzed continuously" not in main:
    raise ValueError("continuous modifier description must match the implemented analysis")
required_main = ["the adjusted ratio was 9.2\\% lower",
                 "48\\% of\nclassified citations", "27\nof the 31 named research areas",
                 "\\emph{Internal Medicine}", "\\emph{Echocardiography}",
                 "11.0\\% higher", "21.5\\%", "11.5\\% to 16.4\\%",
                 "$\\theta=-0.092$", "$P=0.258$", "($P=0.097$)", "($P=0.687$)", "$\\theta=-0.052$", "3.78 million",
                 "0.05--0.95 were excluded", "Benjamini--Hochberg", "without using citation outcomes",
                 "The primary contrast does not rest on this",
                 "$\\theta=-0.097$", "3,818,173", "20,203 journals",
                 "Mixed records",
                 "the effect of narrower-scope publication among papers with\n"
                 "similar published content and measured journal attributes"]
required_supp = ["$\\theta=-0.097$ to $-0.082$", "-0.014", "-0.027",
                 "Reference-adjusted", "within-author analysis",
                 "The Mixed records cluster",
                 "\\renewcommand{\\thefigure}{S\\arabic{figure}}"]
for text, snippets in ((main, required_main), (supp, required_supp)):
    for snippet in snippets:
        if snippet.lower() not in text.lower():
            raise ValueError(f"missing required manuscript text: {snippet!r}")

for forbidden in ("Extended Data", "fixed-support IPW", "citation_dynamics",
                  "depended on adjustment", "prespecified", "pre-specified", "DuckDB hash",
                  "deepened with distance", "deepening as the distance grows",
                  "had not faded", "no catch-up", "classical multidimensional scaling",
                  "Editorial & miscellaneous", "editorial and miscellaneous",
                  "text map", "text model"):
    if forbidden.lower() in (main + supp + "".join(tables.values()) + str(manifest)).lower():
        raise ValueError(f"forbidden content remains: {forbidden}")
for text, snippet in ((main, "1.9\\% to 20.7\\% lower"),
                      (main, "Absolute differences, narrower minus broader scope"),
                      (supp, "displays 420,000 papers"), (supp, "Figure~2b"),
                      (supp, "49.3\\% of flow between")):
    if snippet not in text:
        raise ValueError(f"display correction missing: {snippet}")
if re.search(r"SHA-?256|BLAKE2|checksum|DuckDB|list\\_distinct", main + supp, re.I):
    raise ValueError("engineering identifiers belong in the repository, not the manuscript or SI")
for name, text in (("main", main), ("supplement", supp), *tables.items()):
    excessive = [v for v in re.findall(r"\b\d+\.\d{4,}\b", text) if v != "0.0003"]
    if excessive:
        raise ValueError(f"excessive displayed decimal precision in {name}: {excessive}")
main_prose = re.sub(r"\\begin\{figure\}.*?\\end\{figure\}", "", main, flags=re.S)
for label in ("fig:measurement", "fig:main", "fig:mechanism", "fig:generality"):
    if f"\\ref{{{label}}}" not in main_prose:
        raise ValueError(f"main figure lacks a running-text callout: {label}")
for label in ("S1", "S2", "S3", "S4"):
    if not re.search(r"Supplementary\s+Figure~" + label, main_prose):
        raise ValueError(f"supplementary figure lacks a main-text callout: {label}")
for definition in ("Let $n$ be", "The indicator", "denote the standardized"):
    if definition not in main:
        raise ValueError(f"missing mathematical definition: {definition}")
abstract = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", main, re.S).group(1)
results = main[main.index("\\section{Results}"):main.index("\\section{Discussion}")]
if re.search(r"\breduced\b", abstract + results, re.I):
    raise ValueError("abstract or Results uses reduced for the primary contrast")
if re.search(r"\bimprecise\b", abstract + results, re.I):
    raise ValueError("abstract or Results uses imprecise instead of interpreting the interval")

word_pattern = r"[A-Za-z]+(?:[-'][A-Za-z]+)*|\d+(?:\.\d+)?"
abstract_words = len(re.findall(word_pattern, abstract))
def prose_words(text):
    text = re.sub(r"\\begin\{figure\}.*?\\end\{figure\}", "", text, flags=re.S)
    text = re.sub(r"\\(?:cite\w*|ref|label)\{[^}]*\}", "", text)
    text = re.sub(r"\\[A-Za-z]+\*?(?:\[[^]]*\])?", "", text)
    return len(re.findall(word_pattern, text))

# Main-text counts exclude Abstract, Methods, References, and figure legends.
article_words = prose_words(main[order[0]:order[3]])
methods_words = prose_words(main[order[3]:main.index("\\section*{Data availability}")])
keywords = re.search(r"\\textbf\{Keywords:\}(.*?)(?:\n\n|\\section)", main, re.S).group(1)
keyword_count = len([x for x in keywords.split(";") if x.strip()])
title_words = len(re.findall(word_pattern, re.search(r"\\title\{([^}]+)\}", main).group(1)))
if abstract_words > 200 or title_words > 15:
    raise ValueError(f"manuscript limits: abstract={abstract_words}, title={title_words}")
if article_words > 5000 or methods_words > 3000:
    print(f"manuscript length guidance: main={article_words}/5000; Methods={methods_words}/3000")
if main.count("\\begin{figure}") != 4 or supp.count("\\begin{figure}") != 6:
    raise ValueError("expected 4 main figures and 6 supplementary figures")
if (main + supp).count("[super,comma,sort&compress]{natbib}") != 2 or main.count("\\bibliographystyle{naturemag}") != 1:
    raise ValueError("numerical superscript bibliography configuration missing")
for name in ("main.pdf", "supplement.pdf"):
    if (ROOT / name).stat().st_size <= 10_000:
        raise ValueError(f"missing or small PDF: {name}")

print(f"validated {len(manifest)} source tables; primary theta={float(routing['estimate']):.7f}; "
      f"n={routing['n']}; journals={routing['journals']}; abstract={abstract_words}; "
      f"keywords={keyword_count}; main={article_words}; Methods={methods_words}; "
      f"figures=4+6")
