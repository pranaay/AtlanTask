from flask_rq2 import RQ

rq = RQ()

# dummy mini jobs 
@rq.job
def baseline_upload(x):
	return True

@rq.job
def create_team(x):
	return True

@rq.job
def process_query(x):
	return True