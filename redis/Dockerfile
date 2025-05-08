FROM redis:7.0-alpine

# Add health check 
HEALTHCHECK --interval=5s --timeout=3s --retries=3 \
    CMD redis-cli ping || exit 1

# Copy custom redis configuration file
COPY redis.conf /usr/local/etc/redis/redis.conf

# Define volume for data persistence
VOLUME /data

# Use custom configuration file 
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]