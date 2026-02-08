FROM debian:bookworm-slim

# Install dependencies required for the install script
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    git \
    && rm -rf /var/lib/apt/lists/*

# Run the official installer
# We run this as root so it likely installs to /usr/local/bin or /root/.opencode
RUN curl -fsSL https://opencode.ai/install | bash

# Create a working directory for your project files
WORKDIR /workspace

# Set the port environment variable if the tool supports it, 
# otherwise we just expose it for Docker.
EXPOSE 4096

# Set a default password to suppress the warning (override this in docker run!)
ENV OPENCODE_SERVER_PASSWORD=changeme

# Run the server. 
# CRITICAL: We attempt to bind to 0.0.0.0 so the host can see it.
# If opencode doesn't support the --host flag, see the "Host Networking" note below.
CMD ["opencode", "serve", "--host", "0.0.0.0"]
