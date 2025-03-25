
.PHONY: test format lint clean

test:
	python -m unittest discover tests

format:
	black .

lint:
	flake8 .

clean:
	find temp_pixabay_cache/ -type f -mtime +7 -delete