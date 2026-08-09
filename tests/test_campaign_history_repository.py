from app.repositories.campaign_history_repository import (
    CampaignHistoryRepository,
)

repository = CampaignHistoryRepository()

response = repository.get_campaigns(
    "beta-test-user"
)

print(response.data)