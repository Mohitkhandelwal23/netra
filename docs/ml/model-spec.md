## ML Model Spec and Evaluation Plan

### A. Detection & Tracking (Edge-first)
- **Models:** YOLOv8-n/s for vehicles/pedestrians; DeepSORT/ByteTrack for tracking.
- **Optimizations:** INT8 quantization, TensorRT, pruning, frame skipping, async pipelines.
- **Outputs:** `vehicle_type`, `bbox`, `track_id`, `timestamp`, `lane_id` (if mapped), `speed_estimate`.
- **Calibration:** per-camera homography for perspective; lane ROIs for counting.

### B. Density & Queue Estimation
- **Method:** ROI-based counting + perspective transform; fuse upstream/downstream counts to estimate queue propagation.
- **KPIs:** queue length (vehicles), density (vehicles/m), avg speed (km/h).

### C. Violation Detection
- **Red-light:** correlate `SignalState` timeline with stop-line crossing events; threshold on confidence and grace windows.
- **Speeding:** displacement/time using calibrated scale; compare against zone limit.
- **Wrong-lane / encroachment:** lane segmentation mask + object location.
- **Human-in-the-loop:** candidates above threshold auto-create `Violation`; operator review required to issue challan.

### D. Predictive Modeling (Cloud)
- **Models:** LSTM / TFT / Prophet-like baselines for 5–60 min forecasts.
- **Features:** historical counts, DoW/ToD, weather, events, incidents, signal plans, upstream flows.
- **Targets:** future counts, queue length growth; uncertainty estimates where possible.

### E. Signal Optimization / Controller
- **Tier 1 (Rule-based):** extend/trim green based on queue thresholds and min/max bounds.
- **Tier 2 (MPC):** short-horizon search (10–60s) using predicted arrivals; objective = min(queue + delay) with constraints.
- **Tier 3 (RL):** multi-agent with corridor coordination; trained in SUMO/Aimsun; safety layer enforces constraints before apply.

### F. Active Learning & Retraining
- **Triggers:** model uncertainty, drift metrics, false-positive spikes.
- **Loop:** sample frames → label queue → periodic retrain (weekly/monthly) → A/B rollout.
- **Datasets:** balanced across cities, weather, time-of-day; maintain fixed validation set.

### G. Explainability
- **Per decision:** top contributing signals (counts, queues, predicted arrivals), model confidence, counterfactual (previous timing baseline).

### H. Evaluation Plan
- **Detection:** mAP@0.5, recall by class, FPS, latency p50/p95.
- **Tracking:** IDF1, MOTA, track fragmentation.
- **Violations:** precision/recall on reviewed set; false positive rate; time-to-review.
- **Predictive:** RMSE/MAE/MAPE over rolling windows; calibration of uncertainty.
- **Control:** reduction in avg delay and queue length vs baseline; throughput; safety constraint violations (should be zero).
- **Operational:** camera uptime, ingest error rate, edge-to-cloud E2E latency.

### I. Deployment & Monitoring
- **Edge:** OTA model/config updates; watchdog; local buffering on outages.
- **Cloud:** canary deploys for models; Prometheus metrics; drift monitors; alerting for degradation.
