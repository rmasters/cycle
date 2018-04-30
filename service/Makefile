.PHONY: image run

image:
	docker build -t rmasters/cycle .

run: image
	docker run --rm rmasters/cycle python cycles/__init__.py

