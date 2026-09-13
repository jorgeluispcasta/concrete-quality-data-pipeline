.PHONY: setup generate analyze test

setup:
	python -m pip install -r requirements.txt

generate:
	python data_simulation/run_all.py

analyze:
	python analytics/quality_analysis.py
	python analytics/plant_performance.py
	python analytics/acquisition_analysis.py

test:
	pytest -q
