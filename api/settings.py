import os


# goes through the above config variables 
# checks if env vars of those names exist and sets them if they do
vars = [v for v in globals()]
for v in vars :
    env_val = os.getenv(v)
    if env_val is None:
        continue
    else:
        globals()[v] = env_val
