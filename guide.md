FastAPI() = The main application instance (like your Spring Boot @SpringBootApplication class)
APIRouter() = A way to organize routes into modules (like Spring's @RestController classes)

# ✅ GOOD: Organized by feature
app/main.py              # Just wires things together
app/api/v1/endpoints/
  ├── upload.py          # All upload-related endpoints
  ├── chat.py            # All chat-related endpoints
  └── users.py           # All user-related endpoints

You can easily add API versions:
# app/main.py
app.include_router(api_router_v1, prefix="/api/v1")
app.include_router(api_router_v2, prefix="/api/v2")  # New version!