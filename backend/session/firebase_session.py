import os
import json
from typing import List, Dict, Optional

import firebase_admin
from firebase_admin import credentials, firestore


_db: Optional[firestore.Client] = None


def init_firebase() -> firestore.Client:
    global _db

    # If already initialized, reuse the client
    if firebase_admin._apps:
        _db = firestore.client()
        return _db

    # First try JSON from env (for Render / production)
    service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    if service_account_json:
        info = json.loads(service_account_json)
        cred = credentials.Certificate(info)
    else:
        # Fallback: local path for dev
        cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not cred_path:
            raise RuntimeError(
                "FIREBASE_SERVICE_ACCOUNT_JSON or GOOGLE_APPLICATION_CREDENTIALS must be set"
            )
        cred = credentials.Certificate(cred_path)

    firebase_admin.initialize_app(cred)
    _db = firestore.client()
    return _db


def get_db() -> firestore.Client:
    global _db
    if _db is None:
        return init_firebase()
    return _db


def append_message(user_id: str, thread_id: str, role: str, content: str) -> None:
    """
    Append a single message document under:
    users/{userId}/conversations/{threadId}/messages/{messageId}
    """
    db = get_db()
    col_ref = (
        db.collection("users")
        .document(user_id)
        .collection("conversations")
        .document(thread_id)
        .collection("messages")
    )

    col_ref.add(
        {
            "role": role,
            "content": content,
            "timestamp": firestore.SERVER_TIMESTAMP,
        }
    )


def get_history(user_id: str, thread_id: str) -> List[Dict]:
    """
    Return all messages for a given user/thread, ordered by timestamp ascending.
    Each item: {"id", "role", "content", "timestamp"}.
    """
    db = get_db()
    col_ref = (
        db.collection("users")
        .document(user_id)
        .collection("conversations")
        .document(thread_id)
        .collection("messages")
    )

    docs = col_ref.order_by("timestamp").stream()

    history: List[Dict] = []
    for d in docs:
        history.append(
            {
                "id": d.id,
                "role": d.get("role"),
                "content": d.get("content"),
                "timestamp": d.get("timestamp"),
            }
        )
    return history


# Firestore chat structure:
#
# users/{userId}/conversations/{threadId}/messages/{messageId}
#
# - users: top-level collection
#   - {userId}: per user (use "anonymous" if unauthenticated)
#     - conversations: subcollection of conversations
#       - {threadId}: one document per chat thread
#         - messages: subcollection of messages in this thread
#           - {messageId}: auto-generated document ID
#
# Message document fields:
# - role: "user" | "assistant"
# - content: string (message text)
# - timestamp: Firestore server timestamp
