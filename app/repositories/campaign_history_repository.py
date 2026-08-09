from app.services.supabase_service import SupabaseService


class CampaignHistoryRepository:

    def __init__(self):
        self.client = SupabaseService().client

    def get_campaigns(self, user_id: str):

        return (
            self.client
            .table("campaigns")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )