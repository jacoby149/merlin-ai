# Use your preferred Python base
FROM python:3.10-slim

# 1. Install system dependencies required for Node.js, git, and downloads
RUN apt-get update && apt-get install -y \
  curl \
  ca-certificates \
  git \
  && rm -rf /var/lib/apt/lists/*

# 2. Install Node.js 20.x
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
  && apt-get install -y nodejs

# 3. Run the OpenCode installer
RUN curl -fsSL https://opencode.ai/install | bash

# 4. Update the PATH environment variable so Docker (and pipenv) can find OpenCode
ENV PATH="/root/.opencode/bin:${PATH}"

# 5. Install oh-my-opencode globally
RUN npm install -g oh-my-opencode
RUN oh-my-opencode install --no-tui --claude=no --openai=no --gemini=no --copilot=no

WORKDIR /app

# 6. Install pipenv
RUN pip install --no-cache-dir pipenv

# 7. Setup the Pipenv environment
# (If you already have a Pipfile, you can COPY it here and use `pipenv install --deploy`)
# Since we are building this dynamically, we just tell pipenv to install our 3 packages.
RUN pipenv install fastapi uvicorn boto3

# 8. Copy our Python Bootstrapper script
COPY bootstrapper.py /app/bootstrapper.py

EXPOSE 4096

# 9. Run the bootstrapper using Pipenv
CMD ["pipenv", "run", "python", "/app/bootstrapper.py"]
