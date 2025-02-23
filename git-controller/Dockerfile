# Use a lightweight Alpine image
FROM alpine:latest

# Install Git
RUN apk update && apk add --no-cache git

# Set the working directory in the container
WORKDIR /repo

# Optionally copy your repository files into the container.
# NOTE: If you mount a volume on /repo via docker-compose,
#       the volume content will override these files.
COPY . /repo

# Set a default command so you can access a shell
CMD ["tail", "-f", "/dev/null"]

