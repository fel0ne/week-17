import asyncio
from concurrent import futures
import dataclasses
from fastapi import FastAPI, APIRouter
import grpc
from pydantic import BaseModel
import strawberry
from strawberry.fastapi import GraphQLRouter
import uvicorn

# ---- 1. ОБЩАЯ БАЗА ДАННЫХ (IN-MEMORY ДЛЯ ПРОСТОТЫ ЗАПУСКА) ----
NOTIFICATIONS_DB = [
    {"id": 1, "user_id": 101, "title": "Welcome", "body": "Hello!", "channel": "email"},
    {"id": 2, "user_id": 102, "title": "Alert", "body": "Device offline", "channel": "telegram"}
]

# ----  REST API ----
app = FastAPI(title="Notifications Service s05")
router = APIRouter(prefix="/api/notifications")

class NotificationSchema(BaseModel):
    user_id: int
    title: str
    body: str
    channel: str

@router.get("")
def get_all_notifications():
    return NOTIFICATIONS_DB

@router.post("")
def create_rest_notification(payload: NotificationSchema):
    new_notif = {
        "id": len(NOTIFICATIONS_DB) + 1,
        "user_id": payload.user_id,
        "title": payload.title,
        "body": payload.body,
        "channel": payload.channel
    }
    NOTIFICATIONS_DB.append(new_notif)
    return new_notif

app.include_router(router)

# ----  GRAPHQL  ----
@strawberry.type
class NotificationType:
    id: int
    user_id: int
    title: str
    body: str
    channel: str

@strawberry.type
class Query:
    @strawberry.field
    def notifications(self) -> list[NotificationType]:
        return [NotificationType(**n) for n in NOTIFICATIONS_DB]

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_notification(self, user_id: int, title: str, body: str, channel: str) -> NotificationType:
        new_notif = {
            "id": len(NOTIFICATIONS_DB) + 1,
            "user_id": user_id,
            "title": title,
            "body": body,
            "channel": channel
        }
        NOTIFICATIONS_DB.append(new_notif)
        return NotificationType(**new_notif)

schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

# ---- gRPC ----r
class GRPCNotificationsService:
    def CreateNotification(self, request, context):
        new_notif = {
            "id": len(NOTIFICATIONS_DB) + 1,
            "user_id": request.user_id,
            "title": request.title,
            "body": request.body,
            "channel": request.channel
        }
        NOTIFICATIONS_DB.append(new_notif)
        # Возвращаем эмуляцию ответа gRPC
        class Response:
            id = new_notif["id"]
            status = "SENT"
        return Response()

async def run_grpc():

    print("gRPC Server starting on port 8152 (sharing business logic)...")
    # Для демонстрации gRPC логика встроена, полноценный сервер поднимается отдельно при необходимости

# ----  ЗАПУСК ----
if __name__ == "__main__":
    # Запускаем FastAPI (REST + GraphQL) на порту 8151
    uvicorn.run(app, host="0.0.0.0", port=8151)