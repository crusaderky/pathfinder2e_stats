default: all
.PHONY: all clean

clean:
	rm -rf _build notebooks/*.nbconvert.ipynb ../build ../notebooks/.ipynb_checkpoints ../*.egg-info

all:
	pip install ..
	jupyter nbconvert --execute --to notebook ../notebooks/*.ipynb
	mv ../notebooks/*.nbconvert.ipynb notebooks/
	sphinx-build -W -n -j auto -b html -d ../build/doctrees . ../build/html
