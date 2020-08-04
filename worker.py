#FILE TO START THE WORKER PROCESS
from flask_rq2 import cli
cli.rq_cli.worker()
