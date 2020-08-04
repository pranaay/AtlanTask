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

@app.route('/export',methods=["PUT"])
def process_query():
	query = request.form['sql_query']
	from jobs import process_query
	def dummy_process_func(query):
		pass
	return Response(status = 204)

@app.route('/')
def helllo():
	return "helllo"

@app.route('/pause',methods=["PUT"])
def pause():
	subprocess.run(["rq","suspend"])
	return Response(status = 204)

@app.route('/resume',methods=["PUT"])
def resume():
	subprocess.run(["rq","resume"])
	return Response(status = 204)

@app.route('/cancel-task',methods=["PUT"])
def cancel():
	if len(Queue.all(redis.from_url("redis://redis:6379/0"))) != 0:
		Queue.all(redis.from_url("redis://redis:6379/0"))[0].empty()
	return Response(status = 204)

if __name__ == '__main__':
	app.run(host="0.0.0.0")