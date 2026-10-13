import logging, json
from typing import Optional, Dict
import httpx

logger = logging.getLogger(__name__)

class OAuthHandler:

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def build_auth_url(self, scope: str = "openid email profile") -> str:
        from urllib.parse import urlencode
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": scope,
            "state": "oauth-state",
        }
        return f"https://auth.example.com/authorize?{urlencode(params)}"

    def exchange_code(self, request) -> Dict:
        from fastapi import HTTPException
        code = request.query_params.get("code", "")
        if not code:
            raise HTTPException(status_code=400, detail="Missing authorization code")
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    "https://auth.example.com/token",
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "redirect_uri": self.redirect_uri,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"OAuth exchange failed: {e}")
        return {
            "email": data.get("email", ""),
            "name": data.get("name", ""),
            "role": data.get("role", "operator"),
        }
