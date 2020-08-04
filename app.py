import subprocess
import redis
from rq import Queue
from flask_rq2 import cli
from flask import Flask,request,Response
from io import TextIOWrapper

def create_app():
	from jobs import rq
	app = Flask('example')
	app.config['RQ_REDIS_URL'] = 'redis://redis:6379/0'
	subprocess.run(["rq","resume"])
	rq.init_app(app)
	rq.init_cli(app)
	return app


app = create_app()

'''
baseline upload receives a CSV file and divides it into mini jobs , if the user 
terminates the connection during upload it stops queuing more jobs 
and pauses the worker. if completed un-interrupted returns status code 201
'''
@app.route('/baseline-upload',methods=['POST'])
def baseline_up(): 
	file = TextIOWrapper(request.files["file"],encoding = 'utf-8')
	lis = file.readlines()
	def generate():
		try:
			from jobs import baseline_upload
			for x in lis:
				baseline_upload.queue(x.rsplit(","))
				yield "data: {}\n\n"
			yield "done"	
		finally:
			print("CLOSED!!!!!")
			subprocess.run(["rq","suspend"])
	return Response(generate(),status = 201,mimetype='text/plain')

'''
create teams works similarly as baseline upload ,receives a CSV file and divides
it into mini jobs , if the user terminates the connection during upload it stops 
queuing more jobs and pauses the worker. if completed un-interrupted returns 
status code 201
'''
@app.route('/create-teams',methods=['POST'])
def create_teams():
	file = TextIOWrapper(request.files["file"],encoding = 'utf-8')
	lis = file.readlines()
	def generate():
		try:
			from jobs import create_team
			for x in lis:
				create_team.queue(x.rsplit(","))
				yield "data: {}\n\n"
			yield "done"	
		finally:
			print("CLOSED!!!!!")
			subprocess.run(["rq","suspend"])
	return Response(generate(),status = 201,mimetype='text/plain')
''''
export request would receive a sql query and divide it into subtasks 
would use the same idea as create team and baseline upload
'''
@app.route('/export',methods=["PUT"])
def process_query():
	query = request.form['sql_query']
	from jobs import process_query
	def dummy_process_func(query):
		pass
	return Response(status = 204)

'''
pauses the worker
'''
@app.route('/pause',methods=["PUT"])
def pause():
	subprocess.run(["rq","suspend"])
	return Response(status = 204)

'''
resumes the worker
'''
@app.route('/resume',methods=["PUT"])
def resume():
	subprocess.run(["rq","resume"])
	return Response(status = 204)

'''
cancels all queued tasks and un-pauses the worker for next request
'''
@app.route('/cancel-task',methods=["PUT"])
def cancel():
	if len(Queue.all(redis.from_url("redis://redis:6379/0"))) != 0:
		Queue.all(redis.from_url("redis://redis:6379/0"))[0].empty()
	return Response(status = 204)

if __name__ == '__main__':
	app.run(host="0.0.0.0")
