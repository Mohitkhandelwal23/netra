## Netra System Architecture

```mermaid
flowchart LR
  %% Edge
  subgraph Edge["Edge Devices (Cameras + Edge boxes)"]
    CAM1[Camera Streams]
    EDGE["Edge Box\nYOLOv8/DeepSORT\nQueue Estimator"]
  end

  %% Backend
  subgraph Backend["Central Backend (Kubernetes cluster)"]
    APIGW[API Gateway & Auth]
    INGEST[Telemetry Ingest]
    SNAP[Video/Snapshot Service]
    ANALYTICS[Analytics Service]
    SIGNAL[Signal Orchestration]
    ENFORCE[E-Challan Service]
    MODELS[ML Inference & Monitoring]
    SIM[Simulation Service]
    MAPS[Map/Visualization Service]
  end

  %% Data Layer
  subgraph Data["Data Layer"]
    TSDB[(TimescaleDB / InfluxDB)]
    PG[(Postgres)]
    S3[(S3 Object Store)]
    REDIS[(Redis)]
  end

  %% UI
  subgraph Admin["Admin UI (Web)"]
    UI[Admin Dashboard]
  end

  %% Third-party
  subgraph ThirdParty["Third‑party Integrations"]
    MAPPROV[Map Provider]
    PAY[Payment Gateway]
    RTO[RTO / Law Enforcement]
  end

  %% Hardware controllers
  subgraph Hardware["Signal Controllers"]
    CTRL[Intersection Controllers]
  end

  %% Flows
  CAM1 -->|RTSP/RTMP| EDGE
  EDGE -->|Metadata JSON (counts, bboxes, violations)| APIGW
  EDGE -->|Evidence crops (JPG)| APIGW

  UI <--> APIGW

  APIGW --> INGEST
  APIGW --> SNAP
  APIGW --> ANALYTICS
  APIGW --> SIGNAL
  APIGW --> ENFORCE
  APIGW --> MODELS
  APIGW --> SIM
  APIGW --> MAPS

  INGEST --> TSDB
  INGEST --> PG
  INGEST --> S3

  SNAP --> S3
  ANALYTICS <--> TSDB
  ENFORCE <--> PG
  ENFORCE --> S3
  MODELS <--> TSDB
  MODELS <--> PG
  SIGNAL <--> REDIS
  SIGNAL -->|Commands| CTRL
  CTRL -->|State/Heartbeats| SIGNAL

  UI -->|Tiles/API| MAPPROV
  ENFORCE --> PAY
  ENFORCE --> RTO

  %% Styling
  classDef secure fill:#eef,stroke:#99f,stroke-width:1px;
  APIGW:::secure
  classDef data fill:#efe,stroke:#5a5,stroke-width:1px;
  TSDB:::data
  PG:::data
  S3:::data
  REDIS:::data
```

### Notes
- **Latency targets**: edge inference ≤ 200 ms/frame; end-to-end control loop ≤ 5 s.
- **Safety**: min/max green, amber interlocks, watchdog fallback to local schedule.
- **Security**: OAuth2/JWT for admins; mTLS for inter-service; TLS in transit; S3 encryption at rest.
- **Observability**: Prometheus metrics, Grafana dashboards, Jaeger traces, JSON structured logs.
- **Manual override**: explicit UI affordances; audit every override with operator ID and timestamps.
