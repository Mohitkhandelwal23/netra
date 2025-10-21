## Retention & Partitioning Policy

- **Detections (raw):** retain 30–90 days depending on storage budget; partition by day; move to Glacier/Deep Archive after 30 days (optional) and purge at retention end.
- **Violations:** retain 1 year minimum; associated evidence images retained 1–3 years based on legal requirements.
- **Challans:** retain 3–7 years (financial records), immutable after issuance except status fields; full audit log retained.
- **Signal states:** retain 180 days detailed; aggregate hourly/daily rollups retained 3 years.
- **Time-series telemetry:** per-junction per-minute metrics kept for 180 days; aggregated rollups (5m/1h/1d) retained 1–3 years.
- **Object store (images/videos):** S3 lifecycle rules by prefix (`/city/junction/camera/yyyy/mm/dd/`); transition to infrequent access after 30 days; optional archive after 90 days.
- **Indexes:** avoid over-indexing hot ingest tables; use time+foreign-key composite indexes; consider BRIN indexes for large time-series tables.
- **Compliance:** encrypt at rest (KMS-managed keys); maintain tamper-evident logs for e-challan chain-of-custody; document legal holds.
