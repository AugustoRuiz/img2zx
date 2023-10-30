build: ## build docker container
	- docker build -t rtorralba/img2zxbasic .

push:
	- docker push rtorralba/img2zxbasic

run:
	- python src/img2zxbasic.py

run-docker:
	- docker run -it -u $(id -u):$(id -g) -v ${PWD}:/out rtorralba/img2zxbasic $@