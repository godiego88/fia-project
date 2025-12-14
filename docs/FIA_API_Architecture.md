# FIA API Architecture (Final, Cost-Free Design)

## Stage 1 --- Broad, Fast, Free Intelligence

Uses ONLY APIs that are fully free, high-quota, and safe for continuous
scanning.

### APIs Used:

-   **yfinance** -- unlimited historical price data\
-   **Twelve Data** -- \~800 free calls/day, real-time last price\
-   **Finnhub (Free Tier)** -- news presence check, lightweight
    fundamentals\
-   **FRED** -- unlimited macroeconomic indicators\
-   **Google Sheets API** -- ticker lists, overrides, config

### Purpose:

Stage 1 builds trigger context using the maximum amount of cost-free intelligence available.

------------------------------------------------------------------------

## Stage 2 --- Deep, Heavy, Selective Research

Uses APIs with limited quotas or computationally heavy data.

### APIs Used:

-   **yfinance** -- long-term historical windows (1m--5y)\
-   **Finnhub** -- analyst ratings, insider transactions, deeper news\
-   **Polygon.io (Free Tier)** -- tick-level data, option chains, minute
    aggregates\
-   **Alpha Vantage** -- full technical indicators (TA model)\
-   **Marketstack** -- global cross-asset EOD verification\
-   **Financial Modeling Prep (FMP)** -- fundamentals, earnings history\
-   **Quandl** -- alternative macro datasets (free-only subset)\
-   **Google Sheets API** -- writeback, reporting, logs

### Purpose:

Stage 2 builds deep results using all advanced datasets.

------------------------------------------------------------------------

## Important Notes

-   **Google Cloud NLP was removed** due to billing-account requirement
    and cost risk.\
-   Stage 1 results are fully passed into Stage 2 for enriched
    reasoning.\
-   No API is duplicated without purpose; each adds unique value.\
-   The system remains **100% free** while maximizing data richness.
