compile_requirements:
	pip-compile requirements.in -o requirements.txt --quiet --no-header --no-emit-index-url

upgrade_requirements:
	pip-compile requirements.in -o requirements.txt --upgrade --quiet --no-header --no-emit-index-url

install_requirements:
	pip install -r requirements.dev.txt --upgrade --use-deprecated=legacy-resolver

refresh:
	git checkout master && \
	git fetch && git pull && \
	cp .env.template .env  && \
	make docker_migrate

run:
	docker-compose up asonika

shell:
	docker-compose run asonika python manage.py shell

docker_migrate:
	docker-compose run asonika python manage.py migrate

docker_test:
	docker-compose run asonika pytest

format:
	isort .
	black .

check:
	isort --check-only --diff .
	black --check .
	flake8 --config=flake8.ini
	bandit . --recursive --quiet --exclude **/tests*,./.venv,./venv
	mypy .
