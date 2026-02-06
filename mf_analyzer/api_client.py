"""
API client for fetching mutual fund data from mfapi.in
"""

import requests
import pandas as pd
from typing import List, Dict, Optional
import logging

from .config import API_BASE_URL, API_TIMEOUT

logger = logging.getLogger(__name__)


class MFAPIClient:
    """Client for interacting with the Mutual Fund API"""
    
    def __init__(self, base_url: str = API_BASE_URL, timeout: int = API_TIMEOUT):
        self.base_url = base_url
        self.timeout = timeout
    
    def fetch_nav_history(self, scheme_code: str) -> pd.DataFrame:
        """
        Fetch NAV history for a given mutual fund scheme code.
        
        Args:
            scheme_code: The mutual fund scheme code
            
        Returns:
            DataFrame with columns: date, nav
            
        Raises:
            ValueError: If scheme code is not found
            requests.RequestException: If API request fails
        """
        try:
            api_url = f"{self.base_url}/{scheme_code}"
            response = requests.get(api_url, timeout=self.timeout)
            
            if response.status_code == 404:
                raise ValueError(
                    f"Scheme code '{scheme_code}' not found. "
                    "Please enter a valid numeric scheme code."
                )
            
            response.raise_for_status()
            nav_json = response.json()["data"]
            
            nav_dataframe = pd.DataFrame(nav_json)
            nav_dataframe["date"] = pd.to_datetime(
                nav_dataframe["date"], format="%d-%m-%Y"
            )
            nav_dataframe["nav"] = nav_dataframe["nav"].astype(float)
            nav_dataframe.sort_values("date", inplace=True)
            nav_dataframe.reset_index(drop=True, inplace=True)
            
            logger.info(f"Fetched {len(nav_dataframe)} NAV records for scheme {scheme_code}")
            return nav_dataframe
            
        except requests.RequestException as e:
            logger.error(f"API request failed for scheme {scheme_code}: {e}")
            raise
    
    def search_mutual_funds(self, query: str) -> List[Dict]:
        """
        Search for mutual funds by name.
        
        Args:
            query: Search query string
            
        Returns:
            List of dictionaries with scheme information
            
        Raises:
            requests.RequestException: If API request fails
        """
        try:
            api_url = f"{self.base_url}/search?q={query}"
            response = requests.get(api_url, timeout=self.timeout)
            response.raise_for_status()
            
            results = response.json()
            logger.info(f"Found {len(results)} funds matching '{query}'")
            return results
            
        except requests.RequestException as e:
            logger.error(f"Search failed for query '{query}': {e}")
            raise
