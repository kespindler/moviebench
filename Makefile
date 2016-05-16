
ssh:
	ssh -i keys/moviebench-useast1.pem ubuntu@ec2-54-165-8-36.compute-1.amazonaws.com

secrets:
	scp -i keys/moviebench-useast1.pem config/secrets.yaml ubuntu@ec2-54-165-8-36.compute-1.amazonaws.com:moviebench/config/secrets.yaml

mysql:
	mysql -u awsuser -p Y07CBZS2QWWQdWb39ZQOZyHdyWMOLsHp

bootstrap:
	brew install sox
	virtualenv env
	. env/bin/activate && pip install -r requirements.txt

.PHONY: ssh
