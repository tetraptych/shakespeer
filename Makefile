flask-debug:
	docker-compose run --service-ports shakespeer bash -c "python main.py"

lint:
	docker-compose run --no-deps shakespeer bash -c "flake8 ."

test:
	docker-compose run --no-deps shakespeer pytest -s tests

coverage:
	docker-compose run --no-deps shakespeer pytest --cov='shakespeer' --cov-config .coveragerc --cov-report term-missing

# [Dummy dependency to force a make command to always run.]
FORCE:
