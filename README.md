<p align="center">
  <img src="docs/assets/logo.svg" alt="VisionGrid" width="120" />
</p>

<h1 align="center">VisionGrid</h1>

<p align="center">
  <strong>Open-source real-time computer vision platform for any camera.</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#supported-cameras">Cameras</a> •
  <a href="#use-cases">Use Cases</a> •
  <a href="#docs">Docs</a> •
  <a href="#contributing">Contributing</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License" />
  <img src="https://img.shields.io/badge/python-3.11+-green.svg" alt="Python" />
  <img src="https://img.shields.io/badge/node-20+-green.svg" alt="Node" />
</p>

---

## What is VisionGrid?

VisionGrid is a **hardware-agnostic**, **privacy-first** computer vision platform that connects to any camera and runs real-time AI detection — entirely on your own infrastructure.

Unlike cloud-locked solutions (Verkada, Meraki) or vendor-specific platforms (Milestone, Genetec), VisionGrid works with **any existing camera** over standard protocols and keeps all video data **local by default**.

```
┌─────────────────────────────────────────────────────┐
│                  VisionGrid Cloud                     │
│  Dashboard • Alerts • Analytics • Multi-site mgmt    │
└──────────────────────┬──────────────────────────────┘
                       │ Events only (no raw video)
┌──────────────────────▼──────────────────────────────┐
│               VisionGrid Edge                        │
│  YOLO Detection • Zone Monitoring • People Counting  │
│  Local storage • Offline capable • Privacy-first     │
└──────────────────────┬──────────────────────────────┘
                       │ RTSP / ONVIF / USB / HTTP
┌──────────────────────▼──────────────────────────────┐
│              Any Camera, Any Brand                    │
│  Hikvision • Dahua • Axis • Reolink • USB • IP      │
└─────────────────────────────────────────────────────┘
```

## Features

- **Multi-protocol ingestion** — RTSP, ONVIF, USB, HTTP/HLS, MJPEG
- **Real-time AI detection** — YOLOv8/YOLO11 with GPU acceleration (CUDA, TensorRT, OpenVINO)
- **Virtual zones** — Draw zones, trigger alerts on intrusion/crossing
- **People counting** — Directional counting with line-crossing detection
- **Privacy-first** — All processing local, no cloud dependency, GDPR/EU AI Act compliant
- **Multi-camera dashboard** — Live view, events timeline, heatmaps
- **Alerts & notifications** — Webhook, MQTT, email, Telegram, push
- **REST API + WebSocket** — Full programmatic control and real-time event streaming
- **Docker-ready** — One command deployment with Docker Compose
- **Extensible** — Plugin system for custom models and integrations

## Quick Start

### Using Docker (recommended)

```bash
git clone https://github.com/your-org/visiongrid.git
cd visiongrid
cp .env.example .env
docker compose up -d
```

Open `http://localhost:3000` for the dashboard and `http://localhost:8000/docs` for the API.

### Manual Installation

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
visiongrid serve

# Frontend
cd frontend
npm install
npm run dev
```

## Supported Cameras

| Protocol | Examples | Status |
|----------|----------|--------|
| RTSP | Hikvision, Dahua, Axis, Reolink, Amcrest | ✅ Ready |
| ONVIF | Any ONVIF-compliant camera | ✅ Ready |
| USB/V4L2 | Webcams, USB cameras | ✅ Ready |
| HTTP/MJPEG | Generic IP cameras | ✅ Ready |
| HLS | Streaming servers, DVRs | ✅ Ready |
| RTMP | Action cameras, encoders | 🔄 Planned |

## Use Cases

### 🏪 Retail & Commercial
- People counting and occupancy control
- Heatmaps for customer flow analysis
- Queue length detection

### 🏗️ Industrial & Construction
- PPE compliance detection (helmets, vests)
- Restricted zone monitoring
- Equipment tracking

### 🚗 Parking & Logistics
- License plate recognition (ANPR)
- Vehicle counting and classification
- Parking occupancy

### 🏠 Residential & Security
- Intrusion detection with virtual zones
- Person/vehicle/animal classification
- Smart notifications (no more false alerts from cats)

### 🌆 Smart Cities
- Traffic flow analysis
- Crowd density monitoring
- Incident detection

## Architecture

```
backend/
├── visiongrid/
│   ├── core/          # Configuration, lifecycle, plugin system
│   ├── cameras/       # Multi-protocol camera connectors
│   ├── detection/     # YOLO pipeline, model management
│   ├── api/           # FastAPI routes + WebSocket
│   ├── events/        # Event bus, alerts, notifications
│   ├── models/        # Database models
│   └── utils/         # Shared utilities
├── tests/
└── pyproject.toml

frontend/
├── src/
│   ├── app/           # Next.js app router pages
│   ├── components/    # React components
│   ├── hooks/         # Custom hooks (WebSocket, streams)
│   └── lib/           # API client, utilities
├── package.json
└── next.config.js
```

## Configuration

```yaml
# visiongrid.yaml
cameras:
  - name: front-door
    url: rtsp://192.168.1.100:554/stream1
    protocol: rtsp
    detection:
      model: yolov8n
      confidence: 0.5
      classes: [person, car, dog, cat]
    zones:
      - name: entrance
        points: [[0.1, 0.1], [0.9, 0.1], [0.9, 0.9], [0.1, 0.9]]
        triggers: [enter, exit]

  - name: backyard
    url: rtsp://192.168.1.101:554/stream1
    protocol: rtsp
    detection:
      model: yolov8n
      classes: [person]
    alerts:
      - type: intrusion
        notify: [webhook, telegram]

detection:
  device: cuda:0  # or cpu, openvino
  batch_size: 4
  
server:
  host: 0.0.0.0
  port: 8000
```

## API

Full API documentation available at `http://localhost:8000/docs` (Swagger UI).

```python
import httpx

# Add a camera
response = httpx.post("http://localhost:8000/api/v1/cameras", json={
    "name": "lobby",
    "url": "rtsp://192.168.1.50:554/stream",
    "detection": {"model": "yolov8n", "classes": ["person"]}
})

# Get live detections via WebSocket
import websockets
async with websockets.connect("ws://localhost:8000/ws/events") as ws:
    async for event in ws:
        print(event)  # {"camera": "lobby", "type": "detection", "objects": [...]}
```

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
# Run tests
cd backend && pytest

# Run linting
ruff check .
mypy .

# Run frontend tests
cd frontend && npm test
```

## Roadmap

- [x] Multi-protocol camera ingestion
- [x] Real-time YOLO object detection
- [x] Virtual zones and intrusion detection
- [x] People counting with line crossing
- [ ] License plate recognition (ANPR)
- [ ] Face recognition (private spaces only, GDPR compliant)
- [ ] Heatmap generation
- [ ] Multi-node distributed deployment
- [ ] Model marketplace
- [ ] Mobile app (React Native)

## License

MIT — see [LICENSE](LICENSE) for details.

---

<p align="center">
  Built with ❤️ in Barcelona • Privacy-first • Hardware-agnostic
</p>
