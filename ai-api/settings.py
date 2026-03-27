import os

from aws_utils import get_params
from pydantic import SecretStr


APP_NAME = "Merlin AI Controller API"
APP_DESCRIPTION = """
<div style='margin: 1em 0'>
    <strong>Controller API for Merlin AI</strong><br>
    <a href="/" style="font-size:1em;">&larr; Go Back Home</a>
</div>
"""

TARGET_API = "api"
TARGET_UI = "ui"
AI_MODEL = "gpt-4.1"
OPENAI_API_BASE_URL = "https://api.openai.com/v1"
LICENSE_STATE_FILE = ".license_state.json"
LICENSE_REFRESH_INTERVAL_SECONDS = 86400
LICENSE_GRACE_WINDOW_SECONDS = 604800
GUMROAD_REQUEST_TIMEOUT_SECONDS = 10

OPENAI_API_KEY = SecretStr("sk-fjk3490fj...")

GIT_NAME = ""
GIT_EMAIL = ""

MY_TEST_PARAMETER = ""
MY_TEST_ENV_RESET_VAR = ""


CONFIG_VARS = [var for var in globals() if var.isupper()]

secrets = {
    "OPENAI_API_KEY": "/merlinai/ai-api/openai_api_key",
}

fetched_secrets = {}
for key, parameter_name in secrets.items():
    try:
        fetched_value = get_params.get_parameter(parameter_name)
    except Exception:
        continue

    if fetched_value is None:
        continue

    fetched_secrets[key] = SecretStr(fetched_value) if key.endswith("_KEY") else fetched_value

for var in CONFIG_VARS:
    if var in fetched_secrets:
        globals()[var] = fetched_secrets[var]

    env_val = os.environ.get(var)
    if env_val is not None:
        globals()[var] = SecretStr(env_val) if var.endswith("_KEY") else env_val

legacy_openai_key = os.environ.get("OPENAPI_KEY")
if legacy_openai_key is not None:
    OPENAI_API_KEY = SecretStr(legacy_openai_key)

LICENSE_REFRESH_INTERVAL_SECONDS = int(LICENSE_REFRESH_INTERVAL_SECONDS)
LICENSE_GRACE_WINDOW_SECONDS = int(LICENSE_GRACE_WINDOW_SECONDS)
GUMROAD_REQUEST_TIMEOUT_SECONDS = int(GUMROAD_REQUEST_TIMEOUT_SECONDS)


if __name__ == "__main__":
    print(f"AWS Param Store TEST ::::::: {MY_TEST_PARAMETER}")
    print(f"Local env TEST ::::::: {MY_TEST_ENV_RESET_VAR}")
