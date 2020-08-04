from flask_rq2 import cli
cli.rq_cli.worker()
# redis.from_url("redis://redis:6379/0")
# import redis