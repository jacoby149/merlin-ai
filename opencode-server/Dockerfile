FROM debian:bookworm-slim

# 1. Install dependencies
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

# 4. Update the PATH environment variable so Docker knows where to look.
ENV PATH="/root/.opencode/bin:${PATH}"

# 5. Fix the npx error by installing globally first!
RUN npm install -g oh-my-opencode
RUN oh-my-opencode install --no-tui --claude=no --openai=no --gemini=no --copilot=no

WORKDIR /workspace

EXPOSE 4096

ENV OPENCODE_SERVER_PASSWORD=changeme

# 6. Start the server
CMD ["opencode", "serve", "--hostname", "0.0.0.0","--port","4096"]
