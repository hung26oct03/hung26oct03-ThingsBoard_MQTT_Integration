from enum import Enum
import os

base_url = os.getenv("THINGSBOARD_HOST", "/api")

class thingsboard_endpoint(str, Enum):
    login = f"{base_url}/auth/login"
    tenant_profile = f"{base_url}/tenantProfiles"
    add_tenant = f"{base_url}/tenant"