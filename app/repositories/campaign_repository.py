from app.services.supabase_service import SupabaseService


class CampaignRepository:

    def __init__(self):
        self.client = SupabaseService().client

    def save_campaign(
        self,
        user_id,
        product_name,
        campaign,
    ):
        return (
            self.client
            .table("campaigns")
            .insert({
                "user_id": user_id,
                "product_name": product_name,
                "campaign": campaign,
            })
            .execute()
        )