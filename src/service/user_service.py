import os
import uuid
from typing import Optional
from database.supabase_client import get_supabase_client

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

USERS_TABLE = "users"


class UserService:
    def __init__(self):
        self.client: Client = get_supabase_client()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_user_or_raise(self, user_id: str) -> dict:
        try:
            response = (
                self.client.table(USERS_TABLE)
                .select("*")
                .eq("id", user_id)
                .maybe_single()
                .execute()
            )
        except Exception:
            raise ValueError(f"User '{user_id}' not found.")
        
        if response.data is None:
            raise ValueError(f"User '{user_id}' not found.")
        return response.data

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def create_user(
        self,
        email: str,
        name: str,
        max_cash_amt: Optional[float] = None,
        max_cash_pct: Optional[float] = None,
    ) -> dict:
        """Create a new user. Raises ValueError if the email is already taken."""
        existing = (
            self.client.table(USERS_TABLE)
            .select("id")
            .eq("email", email)
            .maybe_single()
            .execute()
        )
        if existing.data:
            raise ValueError(f"A user with email '{email}' already exists.")

        new_user = {
            "id": str(uuid.uuid4()),
            "email": email,
            "name": name,
            "max_cash_amt": max_cash_amt,
            "max_cash_pct": max_cash_pct,
        }
        response = self.client.table(USERS_TABLE).insert(new_user).execute()
        return response.data[0]

    def get_user_by_id(self, user_id: str) -> dict:
        """Fetch a single user by their UUID."""
        return self._get_user_or_raise(user_id)

    def get_user_by_email(self, email: str) -> dict:
        """Fetch a single user by their email address."""
        response = (
            self.client.table(USERS_TABLE)
            .select("*")
            .eq("email", email)
            .maybe_single()
            .execute()
        )
        if response.data is None:
            raise ValueError(f"No user found with email '{email}'.")
        return response.data

    def update_user(
        self,
        user_id: str,
        name: Optional[str] = None,
        max_cash_amt: Optional[float] = None,
        max_cash_pct: Optional[float] = None,
    ) -> dict:
        """Update mutable fields on an existing user."""
        self._get_user_or_raise(user_id)

        updates: dict = {}
        if name is not None:
            updates["name"] = name
        if max_cash_amt is not None:
            updates["max_cash_amt"] = max_cash_amt
        if max_cash_pct is not None:
            updates["max_cash_pct"] = max_cash_pct

        if not updates:
            return self._get_user_or_raise(user_id)

        response = (
            self.client.table(USERS_TABLE)
            .update(updates)
            .eq("id", user_id)
            .execute()
        )
        return response.data[0]

    def delete_user(self, user_id: str) -> dict:
        """Delete a user and all associated records across every table."""
        self._get_user_or_raise(user_id)

        # 1. Delete messages sent by this user
        self.client.table("messages").delete().eq("sender_id", user_id).execute()

        # 2. Delete deals involving this user, and their chatrooms/messages
        deals = (
            self.client.table("deals")
            .select("id")
            .or_(f"user1_id.eq.{user_id},user2_id.eq.{user_id}")
            .execute()
        )
        deal_ids = [d["id"] for d in deals.data]
        for deal_id in deal_ids:
            # Delete chatroom messages first, then the chatroom itself
            chatrooms = (
                self.client.table("chatrooms")
                .select("id")
                .eq("deal_id", deal_id)
                .execute()
            )
            for chatroom in chatrooms.data:
                self.client.table("messages").delete().eq("chatroom_id", chatroom["id"]).execute()
            self.client.table("chatrooms").delete().eq("deal_id", deal_id).execute()

        # 3. Delete the deals themselves
        if deal_ids:
            self.client.table("deals").delete().in_("id", deal_ids).execute()

        # 4. Delete this user's items
        self.client.table("items").delete().eq("owner_id", user_id).execute()

        # 5. Delete this user's wanted categories
        self.client.table("user_categories").delete().eq("user_id", user_id).execute()

        # 6. Finally delete the user
        self.client.table(USERS_TABLE).delete().eq("id", user_id).execute()

        return {"message": f"User '{user_id}' deleted successfully."}