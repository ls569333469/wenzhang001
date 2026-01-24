import os
import requests
import json
import time
from typing import Dict, List, Optional, Any
from app.core.config import get_logger

logger = get_logger("lark_client")

class LarkClient:
    """Client for interacting with Lark/Feishu Open Platform (Base/Bitable)"""
    
    def __init__(self):
        self.app_id = os.getenv("LARK_APP_ID")
        self.app_secret = os.getenv("LARK_APP_SECRET")
        # Support both Lark (International) and Feishu (China) endpoints
        # Lark International: https://open.larksuite.com
        # Feishu China: https://open.feishu.cn
        # Using Lark International endpoint (user confirmed)
        self.base_url = os.getenv("LARK_BASE_URL", "https://open.larksuite.com/open-apis")
        
        self._tenant_access_token: Optional[str] = None
        self._token_expire_time: float = 0
        
        if not self.app_id or not self.app_secret:
            logger.warning("Lark App ID or Secret not set. Lark integration will be disabled.")

    def _get_token(self) -> str:
        """Get or refresh tenant_access_token"""
        if self._tenant_access_token and time.time() < self._token_expire_time:
            return self._tenant_access_token
            
        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            data = resp.json()
            
            if data.get("code") != 0:
                logger.error(f"Failed to get Lark token: {data}")
                raise Exception(f"Lark Auth Error: {data.get('msg')}")
                
            self._tenant_access_token = data["tenant_access_token"]
            # Expire slightly before actual expiration (usually 2h) to be safe
            self._token_expire_time = time.time() + data["expire"] - 60 
            logger.info("Successfully refreshed Lark Tenant Access Token")
            return self._tenant_access_token
            
        except Exception as e:
            logger.error(f"Error requesting Lark token: {str(e)}")
            raise

    def list_records(self, app_token: str, table_id: str, view_id: str = None, filter: str = None, page_token: str = None, page_size: int = 100) -> Dict:
        """
        List records from a Bitable table.
        Docs: https://open.larksuite.com/document/server-docs/docs/bitable-v1/app-table-record/list
        """
        token = self._get_token()
        url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        params = {
            "page_size": page_size
        }
        if page_token:
            params["page_token"] = page_token
        if view_id:
            params["view_id"] = view_id
        if filter:
            params["filter"] = filter
            
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=15)
            return resp.json()
        except Exception as e:
            logger.error(f"Failed to list Lark records: {str(e)}")
            raise

    def update_record(self, app_token: str, table_id: str, record_id: str, fields: Dict[str, Any]) -> Dict:
        """Update a specific record's fields"""
        token = self._get_token()
        url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {"fields": fields}
        
        try:
            resp = requests.put(url, headers=headers, json=payload, timeout=10)
            return resp.json()
        except Exception as e:
            logger.error(f"Failed to update Lark record {record_id}: {str(e)}")
            raise

    def create_record(self, app_token: str, table_id: str, fields: Dict[str, Any], timeout: int = 30) -> Dict:
        """Create a new record"""
        token = self._get_token()
        url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {"fields": fields}
        
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
            return resp.json()
        except Exception as e:
            logger.error(f"Failed to create Lark record: {str(e)}")
            raise

    def create_field(self, app_token: str, table_id: str, field_name: str, field_type: int = 1) -> Dict:
        """
        Create a new field in a Bitable table.
        field_type: 1=文本, 2=数字, 3=单选, 4=多选, 5=日期, 7=复选框, 11=人员, 13=电话, 15=URL
        Docs: https://open.larksuite.com/document/server-docs/docs/bitable-v1/app-table-field/create
        """
        token = self._get_token()
        url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "field_name": field_name,
            "type": field_type
        }
        
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            result = resp.json()
            if result.get("code") == 0:
                logger.info(f"Successfully created field: {field_name}")
            else:
                logger.error(f"Failed to create field {field_name}: {result.get('msg')}")
            return result
        except Exception as e:
            logger.error(f"Failed to create Lark field: {str(e)}")
            raise

lark_client = LarkClient()
