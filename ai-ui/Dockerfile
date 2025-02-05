# Use an official Node runtime as a parent image
FROM node:16-alpine

# (Optional) Set environment variable to force polling for file changes.
# This is sometimes needed on Docker for Mac/Windows.
ENV CHOKIDAR_USEPOLLING=true

# Set the working directory in the container
WORKDIR /app

# Copy dependency definitions
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the app's source code
COPY . .

# Expose port 3000 for the React development server
EXPOSE 3000

# Run the app in development mode (with hot reloading)
CMD ["npm", "start"]

