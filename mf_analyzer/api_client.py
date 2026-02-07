"""
API client for fetching mutual fund data from mfapi.in
"""

import requests
import pandas as pd
from typing import List, Dict, Optional
import logging
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import API_BASE_URL, API_TIMEOUT

logger = logging.getLogger(__name__)


class MFAPIClient:
    """Client for interacting with the Mutual Fund API"""
    
    def __init__(self, base_url: str = API_BASE_URL, timeout: int = API_TIMEOUT):
        self.base_url = base_url
        self.timeout = timeout
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic"""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,  # Total number of retries
            backoff_factor=1,  # Wait 1, 2, 4 seconds between retries
            status_forcelist=[429, 500, 502, 503, 504],  # Retry on these HTTP status codes
            allowed_methods=["GET"],  # Only retry GET requests
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
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
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                api_url = f"{self.base_url}/{scheme_code}"
                response = self.session.get(api_url, timeout=self.timeout)
                
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
                
            except (requests.ConnectionError, requests.Timeout, requests.HTTPError) as e:
                if attempt < max_retries - 1:
                    error_msg = f"Server error ({e.response.status_code})" if hasattr(e, 'response') and e.response else "Connection error"
                    logger.warning(f"{error_msg} on attempt {attempt + 1}/{max_retries} for scheme {scheme_code}. Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"API request failed after {max_retries} attempts for scheme {scheme_code}: {e}")
                    raise ConnectionError(
                        f"Failed to fetch data for scheme {scheme_code} after {max_retries} attempts. "
                        "The API server may be temporarily unavailable. Please try again later."
                    ) from e
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
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                api_url = f"{self.base_url}/search?q={query}"
                response = self.session.get(api_url, timeout=self.timeout)
                response.raise_for_status()
                
                results = response.json()
                logger.info(f"Found {len(results)} funds matching '{query}'")
                return results
                
            except (requests.ConnectionError, requests.Timeout, requests.HTTPError) as e:
                if attempt < max_retries - 1:
                    error_msg = f"Server error ({e.response.status_code})" if hasattr(e, 'response') and e.response else "Connection error"
                    logger.warning(f"{error_msg} on attempt {attempt + 1}/{max_retries} for search. Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    logger.error(f"Search failed after {max_retries} attempts for query '{query}': {e}")
                    raise ConnectionError(
                        f"Failed to search for '{query}' after {max_retries} attempts. "
                        "The API server may be temporarily unavailable. Please try again later."
                    ) from e
            except requests.RequestException as e:
                logger.error(f"Search failed for query '{query}': {e}")
                raise
