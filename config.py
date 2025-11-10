import redis
import os

def get_redis_connection():
    host = os.getenv("KEYDB_HOST", "localhost")
    port = int(os.getenv("KEYDB_PORT", 6379))
    password = os.getenv("KEYDB_PASSWORD", "")

    try:
        cliente = redis.Redis(
            host=host,
            port=port,
            password=password,
            decode_responses=True
        )
        cliente.ping()
        return cliente
    except redis.ConnectionError:
        print("Error: No se pudo conectar a KeyDB. Verifique la configuración.")
        exit(1)
