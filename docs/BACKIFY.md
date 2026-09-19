# Backify — Ý tưởng dự án

> **Backend-as-a-Service cho developer muốn ship nhanh, không muốn config dài dòng.**
> Tạo backend hoàn chỉnh (auth, CRUD, storage) trong 5 phút qua wizard flow.

**Version:** 0.5.0
**Ngày:** 2026-09-19
**Trạng thái:** Pre-MVP / Architecture phase — chờ Phase 0 Validation trước khi build đầy đủ

---

## 1. Vấn đề

Developer muốn làm MVP / side project / app nhỏ phải setup backend từ đầu: viết auth, setup database, build CRUD, wire file upload, deploy, config reverse proxy. Mất **3-7 ngày** chỉ cho boilerplate trước khi viết dòng logic sản phẩm nào.

Các BaaS hiện có (Supabase, Appwrite, Firebase) giải quyết được — nhưng được build cho dev đã hiểu RLS, migration, multi-tenant. Với người mới, learning curve quá cao.

**Chưa validate:** Vấn đề này được suy ra từ kinh nghiệm cá nhân, chưa có phỏng vấn/khảo sát dev mục tiêu để xác nhận mức độ đau và mức sẵn sàng trả tiền. Xem mục 2.2.

---

## 2. Giải pháp

**Wizard flow thay vì dashboard.**

```
Tạo project → Chọn plan → Define Field Pool (entity + fields)
→ Chọn module (Auth, CRUD, Storage)
→ Chọn function (signup, signin, create, update)
→ Toggle field nào function đó dùng
→ Generate
→ Nhận URL + API key trong 5 phút
```

**Triết lý:** Bạn không config backend. Bạn lắp ráp nó từ các phần có sẵn.

### Điểm khác biệt — Field Pool

Mỗi entity (User, Product, Order) có **field pool** — danh sách tất cả field nó có thể có. Mỗi function (signup, create...) chỉ **toggle ON/OFF** field từ pool đó.

**Ví dụ — Entity "User" pool:**

```
🔒 id uuid
🔒 email email, unique
🔒 password password
fullName string
dob date
address string
phone phone
gender enum [male, female, other]
```

**User A (web giao hàng) toggle cho signup:**

```
✓ fullName ✓ dob ✓ address ✓ email ✓ phone ✓ password
✗ gender
```

**User B (web social) toggle cho signup:**

```
✓ fullName ✓ dob ✓ email ✓ phone ✓ gender ✓ password
✗ address
```

→ Cùng module. Cùng function. Config khác. Backend behavior khác. Không viết dòng code nào.

### 2.1. Field Pool là acquisition wedge, không phải moat kỹ thuật

Field Pool về bản chất là JSON schema với `enabled: bool` per field per function. Đối thủ copy được trong ~2 tuần. Vai trò thật: **cửa vào**, không phải **thành trì**.

| Tầng | Thứ giữ user | Vai trò |
|---|---|---|
| **Acquisition** | Field Pool UX — dễ demo, dễ hiểu, dễ viral | Kéo user vào |
| **Retention** | Tốc độ config-propagation + zero-downtime schema migration | Giữ user ở lại |
| **Defense** | Cộng đồng VN + payment VN + support tiếng Việt | Chống đối thủ quốc tế |

**Moat thật nằm ở 2 metric:**

- **Config-propagation latency** — target < 100ms từ lúc user bấm Save đến lúc request mới apply config. Cơ chế: RabbitMQ publish `project.config.updated` → Runtime subscribe → invalidate cache ngay. Redis cache TTL 30s chỉ là fallback.
- **Zero-downtime migration** — target 0 request fail khi user đổi field trong pool.

### 2.2. Validation trước khi build đầy đủ

**Vấn đề:** Roadmap 13 tuần (mục 10) build 5 microservices dựa trên giả định chưa kiểm chứng — rằng dev VN thật sự sẽ chuyển từ Supabase/Firebase sang Backify vì Field Pool. Microservices + database-per-project + gRPC + RabbitMQ là lượng đầu tư hạ tầng lớn để đặt cược trước khi biết có ai cần.

**Kế hoạch trước khi vào Phase 1:**

1. Phỏng vấn 10-15 dev mục tiêu (indie hacker / freelancer VN) — xác nhận: họ có thật sự tốn 3-7 ngày cho backend boilerplate? Họ đã thử Supabase/Firebase chưa, bỏ vì lý do gì?
2. Fake-door test: landing page mô tả wizard flow + Field Pool demo (video hoặc clickable prototype, không cần backend thật) → đo tỷ lệ đăng ký chờ / willingness-to-pay ở mức $7-25/tháng.
3. Go/no-go: nếu tín hiệu đủ mạnh, vào Phase 1 với scope microservices như mục 7. Nếu yếu, cân nhắc scope nhỏ hơn (vd: chỉ Auth Service như một sản phẩm độc lập, monolith, không gRPC/RabbitMQ) trước khi mở rộng.

Đây không phải bước bắt buộc cứng nhắc — nhưng nên có trước khi cam kết 13 tuần full-time cho hạ tầng.

---

## 3. Target User

**Primary:** Developer cá nhân / indie hacker / freelancer. Biết frontend (React, Vue, Flutter). Không muốn setup backend. Budget < $25/tháng. **MVP: VN-only** — UI, docs, support tiếng Việt. Không build i18n ở giai đoạn này.

**Secondary:** Agency nhỏ làm nhiều project cho khách. Cần backend nhanh, clone template, self-host hoặc multi-tenant.

**Không target:** Enterprise (cần compliance, SLA). Non-tech user hoàn toàn (họ cần Bubble).

---

## 4. Backify KHÔNG phải là gì

- **Không phải no-code builder.** Bạn vẫn viết frontend. Backify chỉ lo backend.
- **Không phải Supabase clone.** Supabase cho dev đã biết làm gì. Backify cho dev không muốn biết.
- **Không phải enterprise product.** Không SLA, không compliance, không B2B sales.
- **Chưa hoàn thiện.** Đang ở giai đoạn kiến trúc, chưa validate với user thật.

---

## 5. Modules có sẵn

| Module | Functions |
|--------|-----------|
| 🔐 Auth | signup, signin, forgotPassword, oauth |
| 📦 CRUD | create, read, update, delete |
| 📁 Storage | upload, download, presign |
| 🔔 Notification | sendEmail, push |
| 💳 Payment | createOrder, webhook (phase 2) |

**MVP chỉ enable Auth module.** Module khác note "Coming soon" trong UI.

**Rủi ro cần theo dõi:** OAuth bị đẩy sang Phase 2 (mục 7.9), nhưng đa số app tiêu dùng VN kỳ vọng login Google/Facebook ngay từ đầu. Email+password-only có thể khiến dev thử rồi bỏ vì thiếu tính năng họ coi là baseline, không phải vì auth service kém. Cân nhắc theo dõi feedback sớm ở Phase 0/1 để quyết định có cần đẩy OAuth lên sớm hơn không — chưa đổi quyết định, chỉ ghi nhận rủi ro.

---

## 6. Compute Plans

| Plan | CPU | RAM | Storage | Price |
|---|---:|---:|---:|---:|
| Free | 0.1 | 512 MB | 1 GB | $0 |
| 0.5c-512mb | 0.5 | 512 MB | 10 GB | $7/tháng |
| 1c-2g | 1 | 2 GB | 50 GB | $25/tháng |
| 2c-4g | 2 | 4 GB | 100 GB | $85/tháng |

Capabilities (Images, Videos, Audio) — add-on theo dung lượng.

**Free tier MVP:** Chạy trên **shared runtime instance** (multi-tenant). **Không có cold start thật** — vì không có container riêng cho free project ở MVP. Giới hạn: 5 GB bandwidth/tháng, 10.000 request/ngày.

⚠️ Cold shutdown + slot eviction là tính năng Phase 2 (container-per-project). Không quảng cáo cho MVP.

⚠️ **Noisy neighbor risk:** Vì Runtime là shared instance, 1 project free bị spam request (cố ý hoặc do bug từ chính dev đó) có thể ảnh hưởng latency của project khác trên cùng instance. Giới hạn request/ngày ở mức project (không phải rate limiting per-user, vẫn giữ Non-goal ở mục 13) là biện pháp giảm thiểu tối thiểu cần có ngay ở MVP — không đợi Phase 2.

---

## 7. Kiến trúc

### 7.1. Nguyên tắc đã chốt

1. **Không generate code** — 1 runtime duy nhất đọc config JSON, tự route. Update config = update 1 row DB.
2. **Microservices** — 5 services độc lập, scale riêng.
3. **Clean Architecture** — domain / usecase / port / adapter / handler. Domain không import infra.
4. **Field Pool per Entity.**
5. **Control Plane + Data DB:** schema-per-project. **Auth Service:** database-per-project.
6. **RabbitMQ** cho async, **gRPC** cho sync service-to-service.
7. **Config-driven runtime** — 1 binary serve mọi project.
8. **Comment rule:** Doc comment cho exported symbol. Comment WHY, không WHAT. Tiếng Anh cho doc comment, tiếng Việt cho business rule.
9. **Validate trước khi mở rộng** — mỗi service mới hoặc mỗi lớp hạ tầng mới (gRPC, RabbitMQ, sharding) chỉ thêm khi có nhu cầu cụ thể đã xảy ra, không thêm vì "sẽ cần sau này" (xem mục 2.2).

### 7.2. Sơ đồ hệ thống

```
                 ┌──────────────────┐
                 │   API Gateway     │
                 │   (Traefik)       │
                 └────────┬──────────┘
                          │
   ┌────────────┬─────────┼─────────────────┬────────────┐
   ▼             ▼         ▼                 ▼            ▼
┌────────┐  ┌────────┐ ┌────────┐      ┌────────┐   ┌────────┐
│Control │  │Runtime │ │ Auth   │      │Storage │   │Billing │
│Plane   │  │Service │ │Service │      │Service │   │Service │
└───┬────┘  └───┬────┘ └───┬────┘      └───┬────┘   └───┬────┘
    │           │           │               │             │
    └───────────┴───────────┼───────────────┴─────────────┘
                             │
                      ┌──────▼──────┐
                      │  RabbitMQ   │
                      └──────┬──────┘
                             │
   ┌────────────┬───────────┼───────────────┬────────────┐
   ▼             ▼           ▼               ▼            ▼
┌────────┐  ┌────────┐  ┌────────┐     ┌────────┐   ┌────────┐
│Control │  │  Data  │  │  Auth  │     │ MinIO  │   │Billing │
│  DB    │  │  DB    │  │  DB    │     │  /R2   │   │  DB    │
│        │  │        │  │ +Redis │     │        │   │        │
└────────┘  └────────┘  └────────┘     └────────┘   └────────┘
```

### 7.3. Services

| Service | Trách nhiệm | DB | Scale |
|---|---|---|---|
| **Control Plane** | Dashboard API — quản lý project/entity/field/module | Control DB (schema-per-project) | 1-2 |
| **Runtime** | Serve end-user API (hot path) | Data DB (schema-per-project) | 10-100 |
| **Auth** | JWT, multi-tenant auth | Auth DB (database-per-project) + Redis | 3-5 |
| **Storage** | Upload/download, presigned URL | MinIO + metadata | 2-5 |
| **Billing** | Usage tracking | Billing DB | 1-2 |

### 7.4. Giao tiếp giữa services

| From → To | Cách | Lý do |
|---|---|---|
| Gateway → Any | HTTP | External API |
| Auth → Control Plane | gRPC | Lấy project config |
| Runtime → Auth | gRPC | Verify token |
| Control → Runtime | RabbitMQ | Invalidate cache |
| Runtime → Billing | RabbitMQ | Track usage |
| Control → Storage | HTTP/gRPC | Tạo bucket |

**Event bus (RabbitMQ):**

```
project.created           → Runtime (spawn schema), Auth (tạo DB), Billing (init usage)
project.config.updated    → Runtime (invalidate cache), Auth (invalidate config cache)
project.deleted           → Runtime (drop schema), Auth (drop DB), Storage (delete bucket)
user.signup.completed     → Notification (welcome email)
usage.request             → Billing (aggregate)
file.uploaded             → Billing (track egress)
```

### 7.5. Runtime — điểm mấu chốt

Runtime serve mọi project (MVP: shared instance).

```
Request → POST /auth/signup (shop-app.api.backify.io)
↓
Traefik route theo subdomain → Runtime
↓
Runtime:
  1. Đọc config từ cache (Redis, TTL 30s = fallback)
  2. Lấy signup.enabledFields
  3. Lấy pool User để validate
  4. Validate request body
  5. INSERT INTO proj_shop_app.users
  6. Return JWT + user info
```

Cache invalidation: Control publish `project.config.updated` → Runtime subscribe → invalidate cache ngay. TTL 30s là lưới an toàn.

### 7.6. Data isolation

- **Control DB:** schema `control`
- **Data DB:** schema-per-project (`proj_abc123.users`)
- **Auth DB:** database-per-project (`auth_proj_<id>`, instance riêng port 5433)
- **Billing DB:** Postgres riêng

**Rule cứng:** Không share DB giữa services. Auth Service **không** connect Control DB — lấy config qua gRPC.

### 7.7. Scaling schema-per-project (Control DB, Data DB)

Vấn đề ở scale lớn: `pg_dump` chậm dần, `search_path` switching cần PgBouncer, `pg_catalog` bloat.

**Kế hoạch:**
1. Benchmark — tìm ngưỡng X = số schema tối đa 1 instance chịu được (p99 < 100ms)
2. Ghi ngưỡng X vào ADR-004
3. Vượt ngưỡng → **shard bằng lookup table** (`project_id → shard_id`)

⚠️ Không dùng `hash(project_id) % N` — khi N tăng, hash mod đổi kết quả → phải move data. Lookup table cho phép chỉ assign project mới vào shard mới.

### 7.7.1. Scaling database-per-project (Auth DB) — thiếu kế hoạch, cần bổ sung

Auth DB dùng database-per-project (không phải schema-per-project), nên rủi ro scale khác với mục 7.7: mỗi database riêng có overhead nặng hơn schema riêng — connection pool per database, catalog riêng, backup/vacuum riêng, giới hạn số database thực tế 1 Postgres instance nên chứa (thường khuyến nghị dưới vài trăm đến ~1000 tùy cấu hình, chưa kiểm chứng cho case cụ thể này).

**Cần làm trước khi có nhiều project thật:**
1. Benchmark — tìm ngưỡng Y = số database tối đa 1 Auth DB instance chịu được trước khi connection overhead / backup time / vacuum time vượt ngưỡng chấp nhận được
2. Ghi ngưỡng Y vào ADR riêng (vd ADR-005), song song với ADR-004 ở mục 7.7
3. Vượt ngưỡng → cân nhắc: (a) nhiều Auth DB instance + lookup table tương tự 7.7, hoặc (b) đánh giá lại có nên đổi sang schema-per-project cho Auth (đánh đổi: mất lợi ích cô lập mạnh của database riêng, đổi lại scale dễ hơn) — quyết định này nên hoãn tới khi có số liệu thật từ benchmark, không quyết trước.

### 7.8. Xoá field khỏi pool — Hybrid

- **System field** (`id`, `email`, `password`) → **chặn xoá hoàn toàn**
- **Custom field** → cho xoá, nhưng phải confirm nếu đang toggle ON ở function (`force=true`), tự động tắt toggle ở mọi function liên quan

**Không active-purge JSONB ở MVP:** Xoá field = xoá metadata + tắt toggle. Key cũ nằm im trong JSONB, vô hại vì Runtime chỉ đọc field có trong pool. Cleanup job là Phase 2.

### 7.9. Auth Service — Multi-tenant auth cho end-user

Phục vụ **end-user của khách hàng** (user của project), không phải platform user.

| # | Quyết định | Giá trị |
|---|---|---|
| 1 | JWT algorithm | HS256 |
| 2 | JWT expiry | 1 giờ |
| 3 | Refresh token expiry | 7 ngày hoặc 30 ngày (user chọn) |
| 4 | Multi-tenant DB | Database-per-project (`auth_proj_<id>`) |
| 5 | OAuth | Phase 2 — xem rủi ro ở mục 5 |
| 6 | Custom field | Không — chỉ system fields (email, password, fullName, phone) |
| 7 | Scope | 4 tuần |

**HS256 Secret Management:** Secret load từ env, 1 secret cho toàn Auth Service. **Runtime không verify JWT trực tiếp** — gọi gRPC `AuthService.VerifyToken`. Auth Service giữ secret, verify, trả user info. Runtime không bao giờ thấy secret.

**API:** `POST /auth/signup`, `signin`, `signout`, `refresh`, `forgot-password`, `reset-password`; `GET /auth/me`, `/health`.

**gRPC:** `VerifyToken(token, expected_project_id)` → `{valid, user_id, project_id, email, error}`.

**Domain rules:**
- User: email unique trong project, password hash argon2id, metadata JSONB
- RefreshToken: random 32 bytes, lưu SHA-256 hash, token reuse detection
- PasswordResetToken: random 32 bytes, expiry 1h
- JWT payload: `{sub, pid, email, jti, iat, exp}`

**Event:** publish `auth.user.signup`, `auth.user.signin`, `auth.password_reset_requested`. Subscribe `project.created`, `project.deleted`, `project.config.updated`.

**Còn thiếu:** benchmark database-per-project — xem mục 7.7.1.

### 7.10. Control Plane — gRPC service

Control Plane expose gRPC song song HTTP để Auth (và Runtime sau này) lấy config.

**Proto ở `pkg/proto/control/`** (shared kernel).

```protobuf
service ControlPlaneService {
    rpc GetProjectConfig(GetProjectConfigRequest) returns (GetProjectConfigResponse);
    rpc GetProject(GetProjectRequest) returns (GetProjectResponse);
}
```

**Nguyên tắc:**
- Proto3 backward compatible: thêm field OK, xoá dùng `reserved`, đổi type không được
- Dùng gRPC status codes (`codes.NotFound`, `codes.InvalidArgument`, `codes.Internal`) — không dùng in-band error string
- Có gRPC health service (`grpc.health.v1.Health/Check`)
- Graceful shutdown cho gRPC server

---

## 8. Tech Stack

| Layer | Công nghệ |
|---|---|
| Ngôn ngữ | **Go 1.26+ cho toàn bộ service ở MVP.** Không kết hợp Python trừ khi có nhu cầu cụ thể đã xảy ra (vd: workload ML/data nặng thật sự cần hệ sinh thái Python) — quyết định khi có bằng chứng, không quyết định trước, cùng tinh thần với "field type immutable" ở mục 12. Polyglot service-per-language là khả thi về kỹ thuật (kiến trúc đã tách service qua gRPC/RabbitMQ) nhưng thêm CI pipeline, deploy pattern, và bề mặt lỗi thứ hai — cái giá không đáng trả khi chưa có nhu cầu rõ. |
| HTTP | Chi (control) / Fiber (runtime) |
| RPC | gRPC + Protocol Buffers |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Message queue | RabbitMQ 3.13 |
| Object storage | MinIO (dev) → Cloudflare R2 (prod) |
| Reverse proxy | Traefik v3 |
| Container | Docker + Docker Compose |
| Migration | golang-migrate |
| Logging | zerolog (structured JSON) |
| Tracing | OpenTelemetry → Jaeger (Phase 2) |
| Metrics | Prometheus + Grafana (1 dashboard cơ bản) |
| Auth | JWT (HS256) + argon2id |
| Billing | MVP: chuyển khoản thủ công. Phase 2: Stripe + payOS |

---

## 9. Repo Structure

```
backify/
├── services/
│   ├── control-plane/
│   │   ├── cmd/api/main.go
│   │   ├── internal/
│   │   │   ├── domain/
│   │   │   ├── port/
│   │   │   ├── usecase/
│   │   │   ├── adapter/
│   │   │   ├── handler/
│   │   │   ├── grpc/
│   │   │   └── module.go
│   │   ├── migrations/
│   │   ├── go.mod
│   │   └── Dockerfile
│   ├── auth/
│   │   ├── cmd/api/main.go
│   │   ├── internal/
│   │   │   ├── domain/
│   │   │   ├── port/
│   │   │   ├── usecase/
│   │   │   ├── adapter/
│   │   │   ├── handler/
│   │   │   ├── grpc/
│   │   │   ├── jwt/
│   │   │   └── module.go
│   │   ├── migrations/
│   │   ├── go.mod
│   │   └── Dockerfile
│   ├── runtime/
│   ├── storage/
│   └── billing/
├── pkg/                    # Shared libs
│   ├── logger/
│   ├── config/
│   ├── tracing/
│   ├── events/
│   ├── errors/
│   └── proto/
│       └── control/
├── deployments/
│   ├── docker-compose.yml
│   └── traefik/
├── api/
│   └── openapi/
├── docs/
│   ├── BACKIFY.md
│   └── adr/
├── go.work
├── Makefile
└── README.md
```

Mỗi service có `go.mod` riêng. `pkg/` chỉ chứa infrastructure + proto, không chứa domain.

**Makefile target:** suffix `-auth`, `-control` để không đè lẫn nhau. Thêm `run-all` target để chạy full stack local.

---

## 10. Roadmap

| Phase | Thời gian | Nội dung |
|---|---|---|
| **0** | **2 tuần** | **Validation** — phỏng vấn 10-15 dev mục tiêu, fake-door test landing page + demo Field Pool, quyết định go/no-go và scope trước khi vào Phase 1. Xem mục 2.2. |
| 1 | Tuần 1-4 | Foundation + Control Plane (domain, migration, CRUD API). Song song: benchmark schema-per-project (7.7) VÀ database-per-project cho Auth (7.7.1). |
| 2 | Tuần 5-9 | Auth Service + Runtime Service (config-driven routing, cache invalidation qua RabbitMQ). Runtime là phần khó nhất — cho 5 tuần. |
| 3 | Tuần 10-11 | Storage Service: presigned upload, MinIO. |
| 4 | Tuần 12-13 | Structured logging + 1 dashboard Grafana + deploy production (VPS + Docker Compose). |
| 5 | Tuần 14+ | Post-MVP: OpenTelemetry tracing, Loki, Billing (Stripe + payOS), load test. Đánh giá lại OAuth timing dựa trên feedback thật. |

**MVP không có Billing tự động** — bán thủ công qua chuyển khoản.

**Beyond MVP:** Compute plan thật (container-per-project), edge functions, frontend hosting, AI-assisted config, multi-region, marketplace.

---

## 11. Tại sao Microservices từ đầu?

**Lý do:**
- Runtime cần scale độc lập (traffic gấp 100x Control Plane) — *giả định, chưa có traffic thật để đo*
- Billing isolated vì security (giữ credentials thanh toán)
- Deploy độc lập — fix Billing không ảnh hưởng Runtime
- Auth là cross-cutting concern, cần service riêng
- Team growth — service ownership map với team structure

**Trade-off:** ~13 tuần tới MVP thay vì ~8 tuần với monolith. Distributed tracing, centralized logging, message idempotency là bắt buộc (nhưng tracing/logging đẩy sang Phase 2).

**Ghi chú:** Phần lớn lý do trên là chuẩn bị cho tương lai chưa xảy ra (traffic 100x, team growth). Nếu Phase 0 (mục 2.2) cho tín hiệu yếu, cân nhắc bắt đầu với scope nhỏ hơn — vd chỉ Auth Service dạng monolith độc lập — trước khi đầu tư đủ 5 service.

---

## 12. Open Questions

**Đã trả lời:**

- **Field type migration?** → MVP: cấm đổi type. Field immutable. Phase 2: versioned field.
- **Field Pool có phải moat?** → Không. Là acquisition wedge. Moat thật = config-propagation + zero-downtime.
- **Free tier economics?** → MVP không cold shutdown. Dựa trên giới hạn bandwidth/request.
- **K8s hay Docker Compose?** → Docker Compose đủ cho MVP. Ngưỡng chuyển K8s gắn với ngưỡng sharding Postgres.
- **Xoá field đang dùng?** → Hybrid: chặn system field, auto-tắt toggle custom field, không active-purge JSONB.
- **Target VN hay global?** → VN-first. Không build i18n. Global expansion gộp 1 quyết định Phase 2.
- **Auth lấy config từ đâu?** → gRPC từ Control Plane. Auth không connect Control DB.
- **HS256 secret cho Runtime?** → Runtime không verify JWT trực tiếp. Gọi gRPC `VerifyToken`.
- **Kết hợp Python + Go?** → Không ở MVP. Go-only trừ khi có nhu cầu cụ thể đã xảy ra (xem mục 8).

**Còn mở:**

- Relation field (userId → User) — UI concept chưa thiết kế, ảnh hưởng schema
- Có nên expose code cho user custom logic? (Phase 3)
- Go-to-market: Product Hunt, Hacker News, hay VN communities? — nên trả lời sau Phase 0
- Database-per-project benchmark: 1 Postgres instance chịu được bao nhiêu database? — xem 7.7.1, chưa có số liệu
- Refresh token duration UI: chọn 7d/30d ở đâu?
- Custom field trong Auth: cần endpoint `PATCH /auth/me` để update metadata không?
- OAuth ở Phase 2 có đủ sớm không, dựa trên kỳ vọng dev VN? — cần theo dõi feedback Phase 0/1

---

## 13. Non-goals for MVP

- ❌ Container-per-project (chỉ shared runtime)
- ❌ Cold shutdown + slot eviction thật
- ❌ OpenTelemetry tracing
- ❌ Loki centralized logging
- ❌ Billing tự động (bán thủ công)
- ❌ Field type migration
- ❌ i18n / đa ngôn ngữ
- ❌ Active-purge JSONB
- ❌ Relation field
- ❌ OAuth
- ❌ Email verification
- ❌ 2FA / MFA
- ❌ Custom field validation trong Auth
- ❌ Rate limiting per-user (per-project request cap ở free tier vẫn giữ — xem mục 6)
- ❌ Account lockout
- ❌ Custom logic / edge functions
- ❌ Frontend hosting
- ❌ Multi-region
- ❌ AI-assisted config
- ❌ Marketplace module
- ❌ Kết hợp ngôn ngữ khác ngoài Go (xem mục 8)

---

## 14. Glossary

| Thuật ngữ | Định nghĩa |
|---|---|
| **Project** | 1 backend instance user tạo. Có subdomain riêng, DB riêng. |
| **Entity** | Concept trong project (User, Product, Order). Có field pool riêng. |
| **Field Pool** | Danh sách tất cả field entity có thể có. Source of truth. |
| **System Field** | Field mặc định không xóa được (id, email, password). |
| **Custom Field** | Field user tự thêm vào pool. |
| **Module** | Nhóm chức năng (Auth, CRUD, Storage). |
| **Function** | Hành động trong module (signup, signin, create). |
| **Runtime** | Service serve API cho end-user. Đọc config, validate, route. |
| **Control Plane** | Service cho dashboard (user quản lý project). |
| **Cold Start** | Thời gian khởi động container khi có request đầu tiên sau sleep. Phase 2. |
| **Slot Eviction** | Đuổi free project khỏi node để nhường cho paid. Phase 2. |
| **Shard (lookup table)** | Cách chia Postgres instance khi vượt ngưỡng số schema — route bằng bảng `project_id → shard_id`, không dùng hash mod. |
| **Database-per-project** | Cách isolate Auth DB — mỗi project 1 database riêng. |
| **Schema-per-project** | Cách isolate Control DB và Data DB — mỗi project 1 schema trong cùng database. |
| **Phase 0** | Giai đoạn validate ý tưởng (phỏng vấn dev, fake-door test) trước khi cam kết 13 tuần build. |

---

## 15. Changelog

| Ngày | Version | Thay đổi |
|---|---|---|
| 2026-09-13 | 0.1.0 | Initial draft. Chốt microservices, field pool, config-driven runtime. |
| 2026-09-14 | 0.1.0 | Restructure thành bản copy-ready. |
| 2026-09-14 | 0.2.0 | Sửa inconsistency free tier vs config-driven runtime. Định vị Field Pool là acquisition wedge. Roadmap 12→13 tuần. Chốt field type immutable. Sửa sharding sang lookup table. Thêm Non-goals. |
| 2026-09-14 | 0.3.0 | Chốt xoá field: Hybrid + không active-purge JSONB. Chốt target VN-only, không i18n. Thêm 2 non-goals. |
| 2026-09-15 | 0.4.0 | Control Plane MVP hoàn thành. Chốt plan Auth: HS256, JWT 1h, refresh 7d/30d, database-per-project, không OAuth, không custom field, 4 tuần. Thêm mục 7.9. |
| 2026-09-19 | 0.4.1 | Chốt gRPC: Auth lấy config từ Control Plane qua gRPC (Option A2). Thêm mục 7.10. Proto ở `pkg/proto/control/`. Auth không connect Control DB. |
| 2026-09-19 | 0.5.0 | Thêm mục 2.2 (Phase 0 Validation) trước roadmap 13 tuần. Thêm mục 7.7.1 (benchmark database-per-project cho Auth DB — trước đây thiếu). Chốt ngôn ngữ: Go-only cho MVP, không kết hợp Python (mục 8, 12). Ghi nhận rủi ro: thiếu OAuth ở MVP có thể ảnh hưởng adoption VN (mục 5); noisy-neighbor ở free tier shared runtime (mục 6) — thêm per-project request cap làm biện pháp giảm thiểu tối thiểu. Cập nhật mục 11 để làm rõ phần lớn lý do chọn microservices là giả định chưa kiểm chứng. |

---

*Đây là single source of truth cho context dự án Backify. Mọi thay đổi lớn phải update file này.*