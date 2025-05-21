# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo",
#     "matplotlib==3.10.3",
#     "numpy==2.2.6",
#     "polars==1.30.0",
#     "seaborn==0.13.2",
# ]
# ///

import marimo

__generated_with = "0.13.11"
app = marimo.App(width="medium")


@app.cell
def _():
    import polars as pl
    import marimo as mo
    return mo, pl


@app.cell
def _(pl):
    df = pl.read_csv("data.csv")
    df
    return (df,)


@app.cell
def _(df, pl):
    import random

    def simulate_lottery(df) -> pl.DataFrame:
        return (
            df.group_by("year")
            .agg(
                pl.map_groups(
                    exprs=["odds"],
                    function=lambda series: random.choices(
                        series[0], weights=series[0], k=1
                    )[0],
                )
            )
            .sort(by="year", descending=False)
            .select("year", pl.col("odds").list.first().log().alias("log_odds"))
            .get_column("log_odds")
            .sum()
        )


    random.seed(42)
    sims = [simulate_lottery(df) for _ in range(10_000)]
    return (sims,)


@app.cell
def _(df, mo, pl):
    actual = (
        df.filter(pl.col("pick") == 1)
        .select(["year", "team", "odds"])
        .with_columns(pl.col("odds").log().alias("log_odds"))
        .get_column("log_odds")
        .sum()
    )
    mo.md(f"The actual log odds of the draft are: **{actual:.4}**")
    return (actual,)


@app.cell
def _(actual, pl, sims):
    import seaborn as sns
    import matplotlib.pyplot as plt

    sns.ecdfplot(data=pl.DataFrame({"log_odds": sims}), x="log_odds")
    plt.axvline(actual, color="red", linestyle="--", label="actual")
    plt.legend()
    plt.title("ECDF of Simulated Log-Likelihoods")
    plt.xlabel("Log-Likelihood")
    plt.ylabel("P(X ≤ x)")
    plt.show()
    return


if __name__ == "__main__":
    app.run()
