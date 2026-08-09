from app.repositories.campaign_repository import CampaignRepository


repository = CampaignRepository()

response = repository.save_campaign(
    user_id="beta-test-user",
    product_name="Excel Masterclass",
    campaign='{"campaign_name": "Excel Masterclass Test Campaign"}',
)

print(response.data)