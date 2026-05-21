"""
stress_composite.py

Composite crypto/macro market stress indicator.

Combines:
- VIX
- Credit spreads
- Stablecoin dominance
- BTC volatility
- Funding rates

Outputs:
- Normalized component scores
- Composite stress index
- Regime classification
"""

import numpy as np
import pandas as pd

# -----------------------------------------------------------------------------
# NORMALIZATION HELPERS
# -----------------------------------------------------------------------------

def zscore(
    series: pd.Series,
    window: int = 90
) -> pd.Series:
    """
    Rolling z-score normalization.
    """

    rolling_mean = (
        series
        .rolling(window)
        .mean()
    )

    rolling_std = (
        series
        .rolling(window)
        .std()
    )

    rolling_std = rolling_std.replace(
        0,
        np.nan
    )

    return (
        (series - rolling_mean)
        / rolling_std
    )


def minmax_scale(
    series: pd.Series,
    window: int = 90,
    clip_min: float = 0,
    clip_max: float = 100
) -> pd.Series:
    """
    Rolling min-max scaling to 0-100.
    """

    rolling_min = (
        series
        .rolling(window)
        .min()
    )

    rolling_max = (
        series
        .rolling(window)
        .max()
    )

    denominator = (
        rolling_max - rolling_min
    )

    denominator = denominator.replace(
        0,
        np.nan
    )

    scaled = (
        100
        * (series - rolling_min)
        / denominator
    )

    scaled = scaled.clip(
        clip_min,
        clip_max
    )

    return scaled

# -----------------------------------------------------------------------------
# COMPONENT METRICS
# -----------------------------------------------------------------------------

def calculate_btc_volatility(
    btc_returns: pd.Series,
    window: int = 30
) -> pd.Series:
    """
    Annualized rolling BTC volatility.
    """

    vol = (
        btc_returns
        .rolling(window)
        .std()
        * np.sqrt(365)
    )

    return vol


def calculate_credit_stress(
    baa_aaa_spread: pd.Series
) -> pd.Series:
    """
    Credit market stress proxy.
    """

    return minmax_scale(
        baa_aaa_spread
    )


def calculate_vix_stress(
    vix: pd.Series
) -> pd.Series:
    """
    Equity volatility stress proxy.
    """

    return minmax_scale(vix)


def calculate_stablecoin_stress(
    stablecoin_dominance: pd.Series
) -> pd.Series:
    """
    Stablecoin flight-to-safety proxy.
    """

    return minmax_scale(
        stablecoin_dominance
    )


def calculate_funding_stress(
    funding_rate: pd.Series
) -> pd.Series:
    """
    Absolute funding rates indicate leverage crowding.
    """

    return minmax_scale(
        np.abs(funding_rate)
    )

# -----------------------------------------------------------------------------
# MAIN COMPOSITE
# -----------------------------------------------------------------------------

def build_stress_composite(
    vix: pd.Series,
    baa_aaa_spread: pd.Series,
    stablecoin_dominance: pd.Series,
    btc_returns: pd.Series,
    funding_rate: pd.Series,
    weights: dict | None = None
) -> pd.DataFrame:
    """
    Build composite market stress index.
    """

    if weights is None:

        weights = {
            "vix": 0.25,
            "credit": 0.25,
            "stablecoin": 0.20,
            "btc_vol": 0.20,
            "funding": 0.10
        }

    # -------------------------------------------------------------------------
    # VALIDATE WEIGHTS
    # -------------------------------------------------------------------------

    total_weight = sum(weights.values())

    if not np.isclose(total_weight, 1.0):

        raise ValueError(
            f"Weights must sum to 1.0 "
            f"(current={total_weight})"
        )

    # -------------------------------------------------------------------------
    # COMPONENT CALCULATIONS
    # -------------------------------------------------------------------------

    vix_score = calculate_vix_stress(vix)

    credit_score = calculate_credit_stress(
        baa_aaa_spread
    )

    stablecoin_score = (
        calculate_stablecoin_stress(
            stablecoin_dominance
        )
    )

    btc_vol = calculate_btc_volatility(
        btc_returns
    )

    btc_vol_score = minmax_scale(
        btc_vol
    )

    funding_score = calculate_funding_stress(
        funding_rate
    )

    # -------------------------------------------------------------------------
    # COMBINE INTO DATAFRAME
    # -------------------------------------------------------------------------

    df = pd.concat([
        vix_score.rename("vix_score"),
        credit_score.rename("credit_score"),
        stablecoin_score.rename(
            "stablecoin_score"
        ),
        btc_vol_score.rename(
            "btc_vol_score"
        ),
        funding_score.rename(
            "funding_score"
        )
    ], axis=1)

    df.sort_index(inplace=True)

    # -------------------------------------------------------------------------
    # HANDLE MISSING DATA
    # -------------------------------------------------------------------------

    df.replace(
        [np.inf, -np.inf],
        np.nan,
        inplace=True
    )

    df.ffill(inplace=True)

    df.dropna(inplace=True)

    # -------------------------------------------------------------------------
    # COMPOSITE SCORE
    # -------------------------------------------------------------------------

    df["stress_composite"] = (
        df["vix_score"]
        * weights["vix"]

        + df["credit_score"]
        * weights["credit"]

        + df["stablecoin_score"]
        * weights["stablecoin"]

        + df["btc_vol_score"]
        * weights["btc_vol"]

        + df["funding_score"]
        * weights["funding"]
    )

    # -------------------------------------------------------------------------
    # REGIME CLASSIFICATION
    # -------------------------------------------------------------------------

    conditions = [

        df["stress_composite"] < 25,

        (
            df["stress_composite"] >= 25
        )
        &
        (
            df["stress_composite"] < 50
        ),

        (
            df["stress_composite"] >= 50
        )
        &
        (
            df["stress_composite"] < 75
        ),

        df["stress_composite"] >= 75
    ]

    labels = [
        "Low Stress",
        "Moderate Stress",
        "High Stress",
        "Crisis"
    ]

    df["stress_regime"] = np.select(
        conditions,
        labels,
        default="Unknown"
    )

    return df

# -----------------------------------------------------------------------------
# SNAPSHOT HELPER
# -----------------------------------------------------------------------------

def latest_stress_snapshot(
    stress_df: pd.DataFrame
) -> dict:
    """
    Returns latest composite metrics.
    """

    if stress_df.empty:

        return {
            "stress_score": np.nan,
            "regime": "Unavailable",
            "vix_score": np.nan,
            "credit_score": np.nan,
            "stablecoin_score": np.nan,
            "btc_vol_score": np.nan,
            "funding_score": np.nan
        }

    latest = stress_df.iloc[-1]

    return {

        "stress_score": round(
            latest["stress_composite"],
            2
        ),

        "regime": latest[
            "stress_regime"
        ],

        "vix_score": round(
            latest["vix_score"],
            2
        ),

        "credit_score": round(
            latest["credit_score"],
            2
        ),

        "stablecoin_score": round(
            latest["stablecoin_score"],
            2
        ),

        "btc_vol_score": round(
            latest["btc_vol_score"],
            2
        ),

        "funding_score": round(
            latest["funding_score"],
            2
        )
    }
