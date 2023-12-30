
all: venv build/pasta-a-la-vodka.html build/pasta-zozona.html

clean:
	rm -rf venv build

venv:
	virtualenv venv
	venv/bin/pip install jinja2 pyyaml

build/%.html: recipies/%.yml
	mkdir -p build
	venv/bin/python convert.py $< > $@

