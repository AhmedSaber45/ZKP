# Use Nginx image to serve static content
FROM nginx:alpine

# Copy static frontend files to Nginx web directory
COPY . /usr/share/nginx/html

# Expose port 80 for the frontend
EXPOSE 80

# Nginx starts automatically by default
