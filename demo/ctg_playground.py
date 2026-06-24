import marimo

__generated_with = "0.23.10"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
        # ClinicalTrials.gov search playground

        A live demo powered by **pytrials-v2**, a typed Python SDK for the ClinicalTrials.gov API v2.
        Set the filters, search, and get analysis-ready rows from the public API.
        [Source on GitHub](https://github.com/prahlaadr/pytrials-v2).
        """
    )
    return


@app.cell
def _(mo):
    condition = mo.ui.text(value="breast cancer", label="Condition", full_width=True)
    status = mo.ui.dropdown(
        options=[
            "Any",
            "RECRUITING",
            "NOT_YET_RECRUITING",
            "ACTIVE_NOT_RECRUITING",
            "COMPLETED",
            "TERMINATED",
        ],
        value="RECRUITING",
        label="Status",
    )
    phase = mo.ui.dropdown(
        options=["Any", "PHASE1", "PHASE2", "PHASE3", "PHASE4"],
        value="Any",
        label="Phase",
    )
    size = mo.ui.slider(5, 50, value=20, label="Max results")
    run = mo.ui.run_button(label="Search trials")
    mo.vstack([condition, mo.hstack([status, phase, size], justify="start", gap=2), run])
    return condition, phase, run, size, status


@app.cell
async def _(condition, mo, phase, run, size, status):
    from urllib.parse import urlencode

    async def fetch_json(url):
        try:
            from pyodide.http import pyfetch

            resp = await pyfetch(url)
            return await resp.json()
        except ImportError:
            import json
            import urllib.request

            with urllib.request.urlopen(url, timeout=20) as r:
                return json.loads(r.read())

    mo.stop(
        not run.value,
        mo.callout("Set your filters above and click Search trials.", kind="info"),
    )

    params = {
        "query.cond": condition.value,
        "pageSize": str(size.value),
        "countTotal": "true",
    }
    if status.value != "Any":
        params["filter.overallStatus"] = status.value
    if phase.value != "Any":
        params["aggFilters"] = f"phase:{phase.value}"

    url = "https://clinicaltrials.gov/api/v2/studies?" + urlencode(params)
    data = await fetch_json(url)

    rows = []
    for study in data.get("studies", []):
        ps = study.get("protocolSection", {})
        idm = ps.get("identificationModule", {})
        stm = ps.get("statusModule", {})
        dm = ps.get("designModule", {})
        spm = ps.get("sponsorCollaboratorsModule", {})
        clm = ps.get("contactsLocationsModule", {})
        rows.append(
            {
                "NCT ID": idm.get("nctId", ""),
                "Title": (idm.get("briefTitle", "") or "")[:90],
                "Status": stm.get("overallStatus", ""),
                "Phase": ", ".join(dm.get("phases", []) or []) or "NA",
                "Lead sponsor": (spm.get("leadSponsor", {}) or {}).get("name", ""),
                "Sites": len(clm.get("locations", []) or []),
            }
        )

    total = data.get("totalCount")
    header = mo.md(
        f"**{total:,}** trials match. Showing the first {len(rows)}."
        if isinstance(total, int)
        else f"Showing {len(rows)} trials."
    )
    mo.vstack([header, mo.ui.table(rows, selection=None, pagination=False)])
    return


if __name__ == "__main__":
    app.run()
