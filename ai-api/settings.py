import os
from aws_utils import get_params

# Set variables to empty string (must exist before building CONFIG_VARS)
MY_TEST_PARAMETER = ""
MY_TEST_ENV_RESET_VAR = ""

# Only process all-uppercase config variables (common convention)
CONFIG_VARS = [var for var in globals() if var.isupper()]

# Set up secrets (mapping secrets var names to AWS parameter names)
secrets = {"MY_TEST_PARAMETER": "/my/parameter/name"}
# Fetch actual secret values for secrets
fetched_secrets = {k: get_params.get_parameter(v) for k, v in secrets.items()}

for var in CONFIG_VARS:
    # 1. Try loading from secrets fetched from AWS Parameter Store
    if var in fetched_secrets:  # Use fetched_secrets (actual values)
        globals()[var] = fetched_secrets[var]
    # 2. Try loading from environment variables (env overrides secret)
    env_val = os.environ.get(var)
    if env_val is not None:
        globals()[var] = env_val

if __name__ == "__main__":
    print(f"AWS Param Store TEST ::::::: {MY_TEST_PARAMETER}")
    print(f"Local env TEST ::::::: {MY_TEST_ENV_RESET_VAR}")
