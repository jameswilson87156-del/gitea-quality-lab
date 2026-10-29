"""Build a self-contained, responsive run report from measured JSON evidence."""

from __future__ import annotations

from collections import defaultdict
from html import escape


OUTCOMES = ("passed", "failed", "errors", "skipped")
OUTCOME_LABELS = {
    "passed": "Passed",
    "failed": "Failed",
    "error": "Error",
    "skipped": "Skipped",
}


def _text(value: object) -> str:
    return escape(str(value if value is not None else "—"), quote=True)


def _duration(value: object) -> str:
    try:
        return f"{float(value):.2f}s"
    except (TypeError, ValueError):
        return "—"


def build_html_report(report: dict) -> str:
    """Render report fields without recalculating the recorded outcomes."""
    summary = report.get("summary", {})
    cases = report.get("cases", [])
    categories: dict[str, dict[str, int]] = defaultdict(
        lambda: {outcome: 0 for outcome in OUTCOMES} | {"tests": 0}
    )
    for case in cases:
        category = str(case.get("category") or "unclassified")
        outcome = case.get("outcome")
        if outcome not in OUTCOME_LABELS:
            outcome = "error"
        categories[category]["tests"] += 1
        categories[category][outcome if outcome != "error" else "errors"] += 1

    total = max(int(summary.get("tests", 0)), 0)
    passed = max(int(summary.get("passed", 0)), 0)
    failed = max(int(summary.get("failed", 0)), 0)
    errors = max(int(summary.get("errors", 0)), 0)
    skipped = max(int(summary.get("skipped", 0)), 0)
    pass_width = (passed / total * 100) if total else 0
    fail_width = (failed / total * 100) if total else 0
    error_width = (errors / total * 100) if total else 0
    skip_width = (skipped / total * 100) if total else 0

    category_rows = []
    for category, counts in sorted(categories.items()):
        category_rows.append(
            "<tr>"
            f"<th scope=\"row\">{_text(category)}</th>"
            f"<td>{counts['tests']}</td><td class=\"ok\">{counts['passed']}</td>"
            f"<td class=\"bad\">{counts['failed']}</td>"
            f"<td class=\"warn\">{counts['errors']}</td>"
            f"<td>{counts['skipped']}</td></tr>"
        )

    case_rows = []
    for case in cases:
        case_id = str(case.get("id") or "unknown")
        category = str(case.get("category") or "unclassified")
        outcome = case.get("outcome")
        outcome = outcome if outcome in OUTCOME_LABELS else "error"
        node_id = str(case.get("node_id") or "")
        failure = case.get("failure")
        search_text = f"{case_id} {category} {node_id}".lower()
        failure_block = (
            f"<pre class=\"failure-output\">{_text(failure)}</pre>"
            if failure
            else "<p class=\"no-failure\">No failure detail was captured.</p>"
        )
        case_rows.append(
            f"<details class=\"case-row\" data-outcome=\"{_text(outcome)}\" "
            f"data-category=\"{_text(category)}\" data-search=\"{_text(search_text)}\">"
            "<summary>"
            f"<span class=\"case-id\">{_text(case_id)}</span>"
            f"<span class=\"case-category\">{_text(category)}</span>"
            f"<span class=\"case-name\">{_text(node_id)}</span>"
            f"<span class=\"case-time\">{_text(_duration(case.get('duration_seconds')))}</span>"
            f"<span class=\"status {outcome}\">{OUTCOME_LABELS[outcome]}</span>"
            "</summary><div class=\"case-detail\">"
            f"<p><span>Pytest node</span><code>{_text(node_id)}</code></p>"
            f"{failure_block}</div></details>"
        )

    category_options = "".join(
        f"<option value=\"{_text(category)}\">{_text(category)}</option>"
        for category in sorted(categories)
    )
    target = report.get("target", {})
    report_state = report.get("execution_state", "unknown")
    empty_cases = not cases
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <title>Run {_text(report.get('run_id'))} · Gitea Quality Lab</title>
  <style>
    :root {{ color-scheme: light; --ink:#172333; --muted:#68788b; --line:#dce3eb; --paper:#fff; --canvas:#f3f6f9; --blue:#2859c5; --teal:#147b67; --red:#b83849; --amber:#a96512; --mono:"Cascadia Code",Consolas,monospace; --sans:Inter,"Segoe UI","Microsoft YaHei",sans-serif; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:var(--canvas); color:var(--ink); font:14px/1.55 var(--sans); }}
    a {{ color:var(--blue); }}
    .shell {{ max-width:1440px; margin:0 auto; padding:28px clamp(16px,4vw,52px) 48px; }}
    .topbar {{ display:flex; align-items:center; justify-content:space-between; gap:16px; min-height:52px; border-bottom:1px solid var(--line); }}
    .brand {{ display:flex; align-items:center; gap:12px; font-weight:750; letter-spacing:-.02em; }}
    .brand-mark {{ display:grid; place-items:center; width:34px; height:34px; border-radius:9px; background:#173252; color:#fff; font-size:12px; letter-spacing:.08em; }}
    .brand small {{ display:block; color:var(--muted); font-size:10px; font-weight:700; letter-spacing:.16em; text-transform:uppercase; }}
    .local-tag,.state-tag {{ display:inline-flex; align-items:center; gap:7px; padding:6px 10px; border:1px solid #cbd8e5; border-radius:999px; background:#fff; color:#41556d; font-size:11px; font-weight:700; }}
    .dot {{ width:7px; height:7px; border-radius:50%; background:#158a70; }}
    .hero {{ display:flex; justify-content:space-between; align-items:flex-end; gap:24px; padding:34px 0 22px; }}
    .eyebrow {{ margin:0 0 7px; color:var(--blue); font-size:10px; font-weight:800; letter-spacing:.16em; text-transform:uppercase; }}
    h1 {{ margin:0; font-size:clamp(26px,4vw,36px); line-height:1.15; letter-spacing:-.045em; }}
    .subtitle {{ margin:9px 0 0; color:var(--muted); }}
    .run-id {{ max-width:100%; padding:9px 12px; border:1px solid var(--line); border-radius:8px; background:#fff; font:11px/1.5 var(--mono); overflow-wrap:anywhere; }}
    .scope-note {{ margin:0 0 18px; padding:12px 15px; border-left:3px solid #5280d3; background:#eaf0fa; color:#364d70; font-size:12px; }}
    .metrics {{ display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); border:1px solid var(--line); border-radius:12px; background:var(--paper); overflow:hidden; }}
    .metric {{ min-height:105px; padding:17px 19px; border-right:1px solid var(--line); }}
    .metric:last-child {{ border-right:0; }}
    .metric span {{ display:block; color:var(--muted); font-size:11px; }}
    .metric strong {{ display:block; margin-top:8px; font-size:28px; line-height:1; letter-spacing:-.04em; font-variant-numeric:tabular-nums; }}
    .metric .ok {{ color:var(--teal); }} .metric .bad {{ color:var(--red); }} .metric .warn {{ color:var(--amber); }}
    .section-grid {{ display:grid; grid-template-columns:minmax(250px,.78fr) minmax(0,1.55fr); gap:18px; margin-top:20px; align-items:start; }}
    .panel {{ min-width:0; border:1px solid var(--line); border-radius:12px; background:var(--paper); }}
    .panel-head {{ padding:18px 20px 13px; border-bottom:1px solid #e8edf2; }}
    h2 {{ margin:0; font-size:16px; letter-spacing:-.02em; }}
    .panel-head p {{ margin:4px 0 0; color:var(--muted); font-size:11px; }}
    .category-wrap {{ padding:8px 18px 17px; }}
    table {{ width:100%; border-collapse:collapse; font-size:12px; }}
    th,td {{ padding:10px 7px; border-bottom:1px solid #edf0f4; text-align:right; white-space:nowrap; }}
    th:first-child,td:first-child {{ text-align:left; }}
    thead th {{ color:var(--muted); font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:.06em; }}
    tbody tr:last-child th,tbody tr:last-child td {{ border-bottom:0; }}
    td.ok {{ color:var(--teal); font-weight:700; }} td.bad {{ color:var(--red); font-weight:700; }} td.warn {{ color:var(--amber); font-weight:700; }}
    .filters {{ display:flex; gap:9px; padding:14px 18px; border-bottom:1px solid #e8edf2; }}
    input,select {{ min-width:0; height:38px; padding:0 11px; border:1px solid #cfd8e3; border-radius:7px; background:#fff; color:var(--ink); font:inherit; outline:none; }}
    input {{ flex:1; }} input:focus,select:focus {{ border-color:#6288d8; box-shadow:0 0 0 3px #dce7fc; }}
    .list-head,.case-row summary {{ display:grid; grid-template-columns:100px 145px minmax(130px,1fr) 66px 76px; align-items:center; gap:10px; }}
    .list-head {{ padding:9px 18px; color:var(--muted); background:#f8fafc; font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:.06em; }}
    .case-list {{ padding:0 10px 10px; }}
    .case-row {{ border-bottom:1px solid #edf0f4; }}
    .case-row:last-child {{ border-bottom:0; }}
    .case-row summary {{ min-height:48px; padding:7px 8px; cursor:pointer; list-style:none; font-size:11px; }}
    .case-row summary::-webkit-details-marker {{ display:none; }}
    .case-row summary::after {{ content:"+"; grid-column:5; grid-row:1; display:none; }}
    .case-row[open] summary {{ background:#f8fafc; }}
    .case-id {{ font:11px var(--mono); color:#294b84; font-weight:700; }}
    .case-category,.case-name {{ overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:#536579; }}
    .case-time {{ text-align:right; color:var(--muted); font-variant-numeric:tabular-nums; }}
    .status {{ justify-self:end; padding:3px 8px; border-radius:999px; font-size:10px; font-weight:800; }}
    .status.passed {{ color:#116a56; background:#e5f4ef; }} .status.failed {{ color:#a92e40; background:#fbe9ec; }} .status.error {{ color:#8c570e; background:#fff1d7; }} .status.skipped {{ color:#586779; background:#edf1f5; }}
    .case-detail {{ padding:13px 18px 16px; background:#f8fafc; border-top:1px solid #e8edf2; font-size:11px; }}
    .case-detail p {{ margin:0 0 8px; }} .case-detail p span {{ margin-right:10px; color:var(--muted); }}
    code,pre {{ font-family:var(--mono); }} .case-detail code {{ overflow-wrap:anywhere; }}
    .failure-output {{ max-height:300px; overflow:auto; margin:10px 0 0; padding:12px; border:1px solid #f0d4d9; border-radius:8px; background:#fff7f8; color:#7d2635; white-space:pre-wrap; overflow-wrap:anywhere; }}
    .no-failure {{ color:var(--muted); }}
    .empty {{ padding:26px 18px; color:var(--muted); text-align:center; }}
    .run-meta {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:1px; margin-top:18px; overflow:hidden; border:1px solid var(--line); border-radius:10px; background:var(--line); }}
    .run-meta div {{ min-width:0; padding:12px 15px; background:#fff; }} .run-meta span {{ display:block; color:var(--muted); font-size:10px; }} .run-meta strong {{ display:block; margin-top:3px; font-size:11px; overflow-wrap:anywhere; }}
    footer {{ display:flex; justify-content:space-between; gap:12px; padding-top:22px; color:var(--muted); font-size:10px; }}
    @media(max-width:900px) {{ .metrics {{ grid-template-columns:repeat(3,1fr); }} .metric:nth-child(3) {{ border-right:0; }} .metric:nth-child(n+4) {{ border-top:1px solid var(--line); }} .section-grid {{ grid-template-columns:1fr; }} }}
    @media(max-width:760px) {{ .shell {{ padding:16px 12px 30px; }} .topbar {{ align-items:flex-start; }} .hero {{ display:block; padding-top:25px; }} .run-id {{ margin-top:16px; }} .metrics {{ grid-template-columns:repeat(2,1fr); }} .metric {{ min-height:88px; padding:14px; border-top:1px solid var(--line); }} .metric:nth-child(odd) {{ border-right:1px solid var(--line); }} .metric:nth-child(even) {{ border-right:0; }} .metric:first-child,.metric:nth-child(2) {{ border-top:0; }} .metric strong {{ font-size:24px; }} .filters {{ flex-direction:column; }} .filters input,.filters select {{ width:100%; flex:auto; }} .list-head {{ display:none; }} .case-list {{ padding:8px; }} .case-row summary {{ grid-template-columns:minmax(0,1fr) auto; gap:5px 10px; padding:10px; }} .case-id {{ grid-column:1; }} .status {{ grid-column:2; grid-row:1; }} .case-name {{ grid-column:1; grid-row:2; }} .case-category {{ grid-column:1; grid-row:3; }} .case-time {{ grid-column:2; grid-row:2; }} .case-detail {{ padding:12px; }} .run-meta {{ grid-template-columns:1fr 1fr; }} footer {{ flex-direction:column; }} }}
    @media(prefers-reduced-motion:no-preference) {{ .case-row summary {{ transition:background .16s ease; }} .case-row summary:hover {{ background:#f5f8fc; }} }}
  </style>
</head>
<body>
  <main class="shell">
    <header class="topbar">
      <div class="brand"><span class="brand-mark">QA</span><span>Gitea Quality Lab<small>Run report</small></span></div>
      <span class="local-tag"><span class="dot"></span>Local system test · no production target</span>
    </header>
    <section class="hero">
      <div><p class="eyebrow">Execution evidence / {_text(report_state)}</p><h1>Test run report</h1><p class="subtitle">A case-level view of the recorded API, browser and persistence checks.</p></div>
      <div class="run-id" aria-label="Run ID">Run ID&nbsp; {_text(report.get('run_id'))}</div>
    </section>
    <p class="scope-note">This run measures the pinned local Gitea instance and synthetic test accounts. A passing case means its recorded assertion matched this local run; it is not a production reliability or capacity claim.</p>
    <section class="metrics" aria-label="Run summary">
      <div class="metric"><span>Measured cases</span><strong>{total}</strong></div>
      <div class="metric"><span>Passed</span><strong class="ok">{passed}</strong></div>
      <div class="metric"><span>Failed</span><strong class="bad">{failed}</strong></div>
      <div class="metric"><span>Errors</span><strong class="warn">{errors}</strong></div>
      <div class="metric"><span>Skipped</span><strong>{skipped}</strong></div>
    </section>
    <section class="section-grid">
      <article class="panel">
        <header class="panel-head"><p class="eyebrow">Coverage by category</p><h2>Observed outcomes</h2><p>Counts are calculated from the individual case rows.</p></header>
        <div class="category-wrap"><table><thead><tr><th scope="col">Category</th><th scope="col">Total</th><th scope="col">Pass</th><th scope="col">Fail</th><th scope="col">Error</th><th scope="col">Skip</th></tr></thead><tbody>{''.join(category_rows) if category_rows else '<tr><td colspan="6" class="empty">No measured cases.</td></tr>'}</tbody></table></div>
      </article>
      <article class="panel">
        <header class="panel-head"><p class="eyebrow">Case explorer</p><h2>Individual test results</h2><p id="visible-count" role="status" aria-live="polite">{len(cases)} cases shown</p></header>
        <div class="filters"><input id="case-search" type="search" aria-label="Search test cases" placeholder="Search case ID or pytest node"><select id="outcome-filter" aria-label="Filter by outcome"><option value="">All outcomes</option><option value="passed">Passed</option><option value="failed">Failed</option><option value="error">Error</option><option value="skipped">Skipped</option></select><select id="category-filter" aria-label="Filter by category"><option value="">All categories</option>{category_options}</select></div>
        <div class="list-head"><span>Case ID</span><span>Category</span><span>Test</span><span>Duration</span><span>Outcome</span></div>
        <div class="case-list">{''.join(case_rows) if not empty_cases else '<p class="empty">No measured cases were recorded.</p>'}</div>
      </article>
    </section>
    <section class="run-meta" aria-label="Run target metadata">
      <div><span>Target</span><strong>{_text(target.get('name'))} {_text(target.get('version'))}</strong></div>
      <div><span>Mode</span><strong>{_text(target.get('mode'))}</strong></div>
      <div><span>Base URL</span><strong>{_text(target.get('base_url'))}</strong></div>
      <div><span>Started</span><strong>{_text(report.get('started_at'))}</strong></div>
      <div><span>Finished</span><strong>{_text(report.get('finished_at'))}</strong></div>
      <div><span>Execution state</span><strong>{_text(report_state)}</strong></div>
    </section>
    <footer><span>Gitea Quality Lab · generated from the run-scoped JSON snapshot</span><span>Local Compose + SQLite evidence</span></footer>
  </main>
  <script>
    const rows = [...document.querySelectorAll('.case-row')];
    const search = document.getElementById('case-search');
    const outcome = document.getElementById('outcome-filter');
    const category = document.getElementById('category-filter');
    const counter = document.getElementById('visible-count');
    function filterRows() {{
      const query = search.value.trim().toLowerCase();
      let visible = 0;
      for (const row of rows) {{
        const matches = (!query || row.dataset.search.includes(query))
          && (!outcome.value || row.dataset.outcome === outcome.value)
          && (!category.value || row.dataset.category === category.value);
        row.hidden = !matches;
        if (matches) visible += 1;
      }}
      counter.textContent = `${{visible}} of ${{rows.length}} cases shown`;
    }}
    search.addEventListener('input', filterRows);
    outcome.addEventListener('change', filterRows);
    category.addEventListener('change', filterRows);
  </script>
</body>
</html>
"""
