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
        **pytrials-v2**) and industry-to-physician payments (CMS Open Payments, the Sunshine Act),
        for program years 2023 and 2024. [Back to the SDK demo](https://pytrials.pyaarproject.org).
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
        "records_2023": 152463,
        "payments_2024": 42732549,
        "records_2024": 154259
    },
    {
        "company": "Novartis",
        "trials": 5043,
        "payments_2023": 16700900,
        "records_2023": 92161,
        "payments_2024": 18147983,
        "records_2024": 87103
    },
    {
        "company": "GSK",
        "trials": 4921,
        "payments_2023": 35368480,
        "records_2023": 101475,
        "payments_2024": 25259587,
        "records_2024": 88768
    },
    {
        "company": "AstraZeneca",
        "trials": 4755,
        "payments_2023": 85953802,
        "records_2023": 127643,
        "payments_2024": 79390401,
        "records_2024": 144882
    },
    {
        "company": "Merck",
        "trials": 4256,
        "payments_2023": 22268979,
        "records_2023": 102856,
        "payments_2024": 21019991,
        "records_2024": 99180
    },
    {
        "company": "Sanofi",
        "trials": 3410,
        "payments_2023": 12149319,
        "records_2023": 45983,
        "payments_2024": 11586594,
        "records_2024": 34980
    },
    {
        "company": "Bristol-Myers Squibb",
        "trials": 2908,
        "payments_2023": 31717900,
        "records_2023": 58502,
        "payments_2024": 31473489,
        "records_2024": 68066
    },
    {
        "company": "Eli Lilly",
        "trials": 2884,
        "payments_2023": 44462969,
        "records_2023": 110676,
        "payments_2024": 50805500,
        "records_2024": 126428
    },
    {
        "company": "Boehringer Ingelheim",
        "trials": 2649,
        "payments_2023": 22594681,
        "records_2023": 78369,
        "payments_2024": 21981721,
        "records_2024": 77230
    },
    {
        "company": "Johnson & Johnson (Janssen)",
        "trials": 2535,
        "payments_2023": 51245750,
        "records_2023": 132066,
        "payments_2024": 57917637,
        "records_2024": 129049
    },
    {
        "company": "Takeda",
        "trials": 1976,
        "payments_2023": 55483057,
        "records_2023": 51258,
        "payments_2024": 71616187,
        "records_2024": 53653
    },
    {
        "company": "Genentech (Roche)",
        "trials": 1653,
        "payments_2023": 67904429,
        "records_2023": 23864,
        "payments_2024": 67717073,
        "records_2024": 24783
    },
    {
        "company": "Amgen",
        "trials": 1584,
        "payments_2023": 26813868,
        "records_2023": 103985,
        "payments_2024": 44726300,
        "records_2024": 122086
    },
    {
        "company": "AbbVie",
        "trials": 1435,
        "payments_2023": 188514343,
        "records_2023": 250846,
        "payments_2024": 156382683,
        "records_2024": 240166
    },
    {
        "company": "Gilead Sciences",
        "trials": 1247,
        "payments_2023": 36066175,
        "records_2023": 30998,
        "payments_2024": 37366614,
        "records_2024": 32323
    }
]
    return (DATA,)


@app.cell
def _(mo):
    year = mo.ui.dropdown(options=["2023", "2024"], value="2024", label="Payment year")
    rank = mo.ui.dropdown(
        options=["Clinical trials", "Physician payments", "Physician payment records"],
        value="Physician payments",
        label="Rank by",
    )
    mo.hstack([year, rank], justify="start", gap=2)
    return rank, year


@app.cell
def _(DATA, mo, rank, year):
    y = year.value
    key = {
        "Clinical trials": "trials",
        "Physician payments": f"payments_{y}",
        "Physician payment records": f"records_{y}",
    }[rank.value]
    ranked = sorted(DATA, key=lambda c: -(c.get(key) or 0))
    rows = [
        {
            "Company": c["company"],
            "Clinical trials": f"{c['trials']:,}",
            f"{y} physician payments": f"${c['payments_' + y]:,}",
            f"{y} payment records": f"{c['records_' + y]:,}",
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
        payment footprint on relatively few trials, or the reverse. Switch the year to see how the
        payment side shifts (for example, AbbVie fell from about 189M to 156M, while Amgen and Takeda rose).

        ### Method and caveats

        - Clinical trials: count of studies by lead/sponsor name on ClinicalTrials.gov (a current snapshot).
        - Payments: CMS Open Payments general payments for the selected program year, summed per reporting
          entity. These are legally disclosed payments (research, consulting, speaking, travel, meals), not wrongdoing.
        - Company names are matched with a curated map across the two datasets (for example, Bristol
          Myers Squibb reports largely under E.R. Squibb & Sons). Matching is approximate at the edges.
        - A per-physician leaderboard is a planned next step; the public API does not aggregate
          server-side, so it needs a batch job.
        """
    )
    return


if __name__ == "__main__":
    app.run()
