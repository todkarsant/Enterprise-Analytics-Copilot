install:
	python -m pip install -r requirements.txt

init:
	python scripts/init_db.py

run:
	uvicorn app.main:app --reload

ui:
	streamlit run ui/streamlit_app.py

test:
	pytest -q

evaluate:
	python scripts/evaluate.py

demo:
	python scripts/demo.py
