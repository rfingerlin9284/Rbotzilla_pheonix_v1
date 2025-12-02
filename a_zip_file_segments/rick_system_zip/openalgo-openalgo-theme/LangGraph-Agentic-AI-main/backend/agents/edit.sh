find . -type f -name "*.py" -exec sed -i "s/import aioredis/import redis.asyncio as redis/g" {} +
find . -type f -name "*.py" -exec sed -i "s/aioredis.create_redis_pool/redis.from_url/g" {} +
