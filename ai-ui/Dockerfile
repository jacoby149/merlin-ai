FROM oven/bun:latest

ENV CHOKIDAR_USEPOLLING=true
ENV HOST=0.0.0.0

# Set the working directory in the container
WORKDIR /app

COPY package.json bun.lock ./

RUN bun install

# Copy the rest of the app's source code
COPY . .

# Expose port 3000 for the React development server
EXPOSE 3000

CMD ["bun", "run", "start"]
