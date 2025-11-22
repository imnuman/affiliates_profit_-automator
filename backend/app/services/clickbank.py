"""
ClickBank API service
"""
import httpx
from typing import List, Optional, Dict, Any
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class ClickBankService:
    """ClickBank API service"""

    BASE_URL = "https://api.clickbank.com/rest/1.3"

    def __init__(self):
        self.api_key = settings.CLICKBANK_API_KEY
        self.developer_key = settings.CLICKBANK_DEVELOPER_KEY

    async def get_products(
        self,
        category: Optional[str] = None,
        page: int = 1,
        results_per_page: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Fetch products from ClickBank Marketplace
        """
        if not self.developer_key:
            logger.warning("ClickBank Developer Key not configured")
            return []

        async with httpx.AsyncClient() as client:
            try:
                headers = {
                    "Authorization": f"Bearer {self.developer_key}"
                }

                params = {
                    "page": page,
                    "resultsPerPage": results_per_page
                }

                if category:
                    params["category"] = category

                response = await client.get(
                    f"{self.BASE_URL}/products",
                    headers=headers,
                    params=params,
                    timeout=30.0
                )

                response.raise_for_status()
                data = response.json()

                return data.get("products", [])

            except Exception as e:
                logger.error(f"Error fetching ClickBank products: {e}")
                return []

    async def get_account_statistics(
        self,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """
        Get account statistics from ClickBank
        """
        if not self.api_key:
            logger.warning("ClickBank API Key not configured")
            return {}

        async with httpx.AsyncClient() as client:
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}"
                }

                params = {
                    "startDate": start_date,
                    "endDate": end_date
                }

                response = await client.get(
                    f"{self.BASE_URL}/accounts/statistics",
                    headers=headers,
                    params=params,
                    timeout=30.0
                )

                response.raise_for_status()
                return response.json()

            except Exception as e:
                logger.error(f"Error fetching ClickBank statistics: {e}")
                return {}


# Create singleton instance
clickbank_service = ClickBankService()
