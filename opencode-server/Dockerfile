FROM debian:bookworm-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
  curl \
  ca-certificates \
  git \
  && rm -rf /var/lib/apt/lists/*

# Run the installer
RUN curl -fsSL https://opencode.ai/install | bash

# --- THE FIX ---
# Update the PATH environment variable so Docker knows where to look.
# Assuming standard install location is /root/.opencode/bin
ENV PATH="/root/.opencode/bin:${PATH}"

WORKDIR /workspace

EXPOSE 4096

ENV OPENCODE_SERVER_PASSWORD=changeme

# Now 'opencode' should be found
CMD ["opencode", "serve", "--hostname", "0.0.0.0","--port","4096"]
