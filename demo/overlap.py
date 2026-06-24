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
        # Trials x Open Payments overlap

        Which companies rank high on **both** clinical-trial volume and payments to physicians?
        This mixes two public datasets: clinical-trial counts by sponsor (ClinicalTrials.gov, via
        **pytrials-v2**) and 2023 industry-to-physician payments (CMS Open Payments, the Sunshine Act).
        [Back to the SDK demo](https://pytrials.pyaarproject.org).
        """
    )
    return


@app.cell
def _():
    DATA = [
    {
        "company": "Pfizer",
        "trials": 6047,
        "payments_2023": 36898273,
        "payment_records": 152463
    },
    {
        "company": "Novartis",
        "trials": 5043,
        "payments_2023": 16700900,
        "payment_records": 92161
    },
    {
        "company": "GSK",
        "trials": 4921,
        "payments_2023": 35368480,
        "payment_records": 101475
    },
    {
        "company": "AstraZeneca",
        "trials": 4755,
        "payments_2023": 85953802,
        "payment_records": 127643
    },
    {
        "company": "Merck",
        "trials": 4256,
        "payments_2023": 22268979,
        "payment_records": 102856
    },
    {
        "company": "Sanofi",
        "trials": 3410,
        "payments_2023": 12149319,
        "payment_records": 45983
    },
    {
        "company": "Bristol-Myers Squibb",
        "trials": 2908,
        "payments_2023": 31717900,
        "payment_records": 58502
    },
    {
        "company": "Eli Lilly",
        "trials": 2884,
        "payments_2023": 44462969,
        "payment_records": 110676
    },
    {
        "company": "Boehringer Ingelheim",
        "trials": 2649,
        "payments_2023": 22594681,
        "payment_records": 78369
    },
    {
        "company": "Johnson & Johnson (Janssen)",
        "trials": 2535,
        "payments_2023": 51245750,
        "payment_records": 132066
    },
    {
        "company": "Takeda",
        "trials": 1976,
        "payments_2023": 55483057,
        "payment_records": 51258
    },
    {
        "company": "Genentech (Roche)",
        "trials": 1653,
        "payments_2023": 67904429,
        "payment_records": 23864
    },
    {
        "company": "Amgen",
        "trials": 1584,
        "payments_2023": 26813868,
        "payment_records": 103985
    },
    {
        "company": "AbbVie",
        "trials": 1435,
        "payments_2023": 188514343,
        "payment_records": 250846
    },
    {
        "company": "Gilead Sciences",
        "trials": 1247,
        "payments_2023": 36066175,
        "payment_records": 30998
    }
]
    return (DATA,)


@app.cell
def _(DATA, mo):
    sort_by = mo.ui.dropdown(
        options=["Clinical trials", "2023 physician payments", "Physician payment records"],
        value="Clinical trials",
        label="Rank by",
    )
    sort_by
    return (sort_by,)


@app.cell
def _(DATA, mo, sort_by):
    key = {
        "Clinical trials": "trials",
        "2023 physician payments": "payments_2023",
        "Physician payment records": "payment_records",
    }[sort_by.value]
    ranked = sorted(DATA, key=lambda c: -(c.get(key) or 0))
    rows = [
        {
            "Company": c["company"],
            "Clinical trials": f"{c['trials']:,}",
            "2023 physician payments": f"${c['payments_2023']:,}",
            "Physician payment records": f"{c['payment_records']:,}",
        }
        for c in ranked
    ]
    mo.ui.table(rows, selection=None, pagination=False)
    return


@app.cell
def _(mo):
    mo.md(
        """
        ### How to read it

        High on both axes (many trials and large physician payments) signals a company with broad
        clinical activity and deep field relationships. Some companies invert the pattern: a large
        payment footprint on relatively few trials, or the reverse.

        ### Method and caveats

        - Clinical trials: count of studies by lead/sponsor name on ClinicalTrials.gov.
        - Payments: 2023 CMS Open Payments general payments, summed per reporting entity. These are
          legally disclosed payments (research, consulting, speaking, travel, meals), not wrongdoing.
        - Company names are matched with a curated map across the two datasets (for example, Bristol
          Myers Squibb reports largely under E.R. Squibb & Sons). Matching is approximate at the edges.
        - A per-physician leaderboard is a planned next step; the public API does not aggregate
          server-side, so it needs a batch job.
        """
    )
    return


if __name__ == "__main__":
    app.run()
