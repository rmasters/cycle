.PHONY: image run

image:
	docker build -t rmasters/cycle .

run: image
	docker run --rm --device=/dev/cu.usbmodem1411 rmasters/cycle python cycles/__init__.py

