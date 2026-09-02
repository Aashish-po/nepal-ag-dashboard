"""
Backend service layer for the Nepal Agricultural Intelligence Dashboard.

Holds the long-running, non-route logic: ETL pipeline, forecasting models,
correlation analysis, climate helpers, Redis cache, and the APScheduler
job that drives weekly data refreshes.
"""
