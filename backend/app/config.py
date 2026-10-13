from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"
    jwt_secret: str = "change-me-in-production"
    jwt_expiry_minutes: int = 60
    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o"
    saml_idp_entity: str = ""
    saml_idp_cert: str = ""
    saml_acs_url: str = ""
    saml_sp_entity: str = ""
    oauth_client_id: str = ""
    oauth_client_secret: str = ""
    oauth_redirect_uri: str = ""
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_default_region: str = "us-east-1"
    gcp_project_id: str = ""
    gcp_service_account_email: str = ""
    azure_client_id: str = ""
    azure_client_secret: str = ""
    azure_tenant_id: str = ""
    azure_subscription_id: str = ""
    class Config:
        env_prefix = ""

settings = Settings(
    host=os.getenv("HOST", "0.0.0.0"),
    port=int(os.getenv("PORT", "8000")),
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    jwt_secret=os.getenv("JWT_SECRET", "change-me-in-production"),
    jwt_expiry_minutes=int(os.getenv("JWT_EXPIRY_MINUTES", "60")),
    llm_api_key=os.getenv("LLM_API_KEY", ""),
    llm_base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
    llm_model=os.getenv("LLM_MODEL", "gpt-4o"),
    saml_idp_entity=os.getenv("SAML_IDP_ENTITY", ""),
    saml_idp_cert=os.getenv("SAML_IDP_CERT", ""),
    saml_acs_url=os.getenv("SAML_ACS_URL", ""),
    saml_sp_entity=os.getenv("SAML_SP_ENTITY", ""),
    oauth_client_id=os.getenv("OAUTH_CLIENT_ID", ""),
    oauth_client_secret=os.getenv("OAUTH_CLIENT_SECRET", ""),
    oauth_redirect_uri=os.getenv("OAUTH_REDIRECT_URI", ""),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", ""),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", ""),
    aws_default_region=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
    gcp_project_id=os.getenv("GCP_PROJECT_ID", ""),
    gcp_service_account_email=os.getenv("GCP_SERVICE_ACCOUNT_EMAIL", ""),
    azure_client_id=os.getenv("AZURE_CLIENT_ID", ""),
    azure_client_secret=os.getenv("AZURE_CLIENT_SECRET", ""),
    azure_tenant_id=os.getenv("AZURE_TENANT_ID", ""),
    azure_subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID", ""),
)
