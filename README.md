# Backify

Backend-as-a-Service cho developer muốn ship nhanh, không muốn config dài dòng.

Tạo backend hoàn chỉnh (auth, CRUD, storage) qua wizard flow: định nghĩa Field Pool cho entity, chọn module/function cần dùng, toggle field nào function đó dùng, generate — nhận URL + API key.

Context đầy đủ (vấn đề, quyết định kiến trúc, lý do chọn) nằm ở [`docs/BACKIFY.md`](docs/BACKIFY.md). File này chỉ để tra cứu nhanh: có service nào, service làm gì, module nào.

## Services

| Service | Ngôn ngữ | Trách nhiệm | Database |
|---|---|---|---|
| `control-plane` | Python | Dashboard API — quản lý project / entity / field / module. Traffic thấp (1-2 instance), chỉ chạy khi dev sửa cấu hình. | Control DB — schema-per-project |
| `runtime` | Go | Serve API cho end-user (hot path) — đọc config, validate, route vào data thật của project. | Data DB — schema-per-project |
| `auth` | Go | JWT + multi-tenant auth cho end-user của mọi project. | Auth DB — database-per-project + Redis |
| `storage` | Go | Upload/download, presigned URL. | MinIO + metadata |
| `billing` | Go | Usage tracking. | Billing DB |

**Giao tiếp giữa service:**
- Client → Gateway (Traefik) → service: HTTP
- Service → service đồng bộ: gRPC (vd: Runtime → Auth để verify token, Auth → Control Plane để lấy config)
- Service → service bất đồng bộ: RabbitMQ (vd: `project.created`, `project.config.updated`, `project.deleted`)

## Modules

| Module | Function | MVP |
|---|---|---|
| 🔐 Auth | signup, signin, signout, refresh, forgotPassword, resetPassword | Bật |
| 📦 CRUD | create, read, update, delete | Coming soon |
| 📁 Storage | upload, download, presign | Coming soon |
| 🔔 Notification | sendEmail, push | Coming soon |
| 💳 Payment | createOrder, webhook | Coming soon |

## Cấu trúc repo

```
backify/
├── .github/workflows/       # CI — Go + Python
├── services/
│   ├── control-plane/       # Python (FastAPI)
│   ├── auth/                # Go
│   ├── runtime/              # Go
│   ├── storage/               # Go
│   └── billing/                # Go
├── pkg/                        # Shared Go libs (logger, config, events, errors, proto)
├── deployments/                  # docker-compose.yml, traefik/
├── api/openapi/
└── docs/
    ├── BACKIFY.md              # full context — đọc file này khi cần chi tiết
    └── adr/
```

Mỗi service Go có `go.mod` riêng. `control-plane` có `pyproject.toml` riêng, không chia sẻ dependency với các service Go.