.PHONY: image run

image:
	docker build -t rmasters/cycle .

run: image
	docker run --rm rmasters/cycle python cycles/__init__.py

clean:
	rm -rf dist/
	rm -rf build/
	rm -rf cycles.onboard.egg-info/

wheel: image clean
	docker run --rm -v "$(CURDIR):/app" rmasters/cycle python setup.py bdist_wheel

