IMAGE_NAME := querido-diario-api
IMAGE_TAG := devel

# Database configuration
POSTGRES_PASSWORD := queridodiario
POSTGRES_USER := $(POSTGRES_PASSWORD)
POSTGRES_DB := $(POSTGRES_PASSWORD)
POSTGRES_HOST := localhost

TEST_POD_NAME := queridodiariotests
API_POD_NAME := queridodiarioapi
TEST_DATABASE_CONTAINER_NAME := queridodiario-test-db
API_DATABASE_CONTAINER_NAME := queridodiario-api-db

POD_NAME := $(API_POD_NAME)
DATABASE_CONTAINER_NAME := $(API_DATABASE_CONTAINER_NAME)

API_PORT := 8080

.PHONY: help
help:
	@echo "destroy: remove the container image"
	@echo "build: builds the container image to run the API and tests"
	@echo "black: run black to format the source code"
	@echo "database: starts the database used by the API"
	@echo "stop-database: removes database used by the API"
	@echo "test-database: starts the database used by the tests"
	@echo "stop-test-database: removes database used by the tests"
	@echo "test: runs the tests"
	@echo "coverage: show the code coverage"
	@echo "shell: open a bash inside a container running the image used by tests and API"
	@echo "sql: access the API database using psql"
	@echo "test-sql: access the test database using psql"
	@echo "runall: start the database and API"
	@echo "run: start the API"

.PHONY: destroy
destroy: 
	podman rmi  $(IMAGE_NAME):$(IMAGE_TAG)

.PHONY: build
build:
	podman build --build-arg LOCAL_USER_ID=$(UID) \
		--tag $(IMAGE_NAME):$(IMAGE_TAG) \
		-f build/Dockerfile build/

.PHONY: black
black:
	podman run --rm -ti --volume $(PWD):/mnt/code:rw \
		--env PYTHONPATH=/mnt/code \
		--user=$(UID):$(UID) $(IMAGE_NAME):$(IMAGE_TAG) \
		black .

destroy-pod:
	podman pod rm --force --ignore $(POD_NAME)

create-pod: destroy-pod
	podman pod create --publish $(API_PORT):$(API_PORT) --name $(POD_NAME)

.PHONY: stop-database
stop-database:
	podman rm --force --ignore $(DATABASE_CONTAINER_NAME) 

.PHONY: database
database: create-pod start-database wait-database

start-database:
	podman run -d --rm -ti \
		--name $(DATABASE_CONTAINER_NAME) \
		--pod $(POD_NAME) \
		-e POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) \
		-e POSTGRES_USER=$(POSTGRES_USER) \
		-e POSTGRES_DB=$(POSTGRES_DB) \
		postgres:12

wait-database: 
	podman run --rm -ti --volume $(PWD):/mnt/code:rw \
		--pod $(POD_NAME) \
		--env PYTHONPATH=/mnt/code \
		--env POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) \
		--env POSTGRES_USER=$(POSTGRES_USER) \
		--env POSTGRES_DB=$(POSTGRES_DB) \
		--env POSTGRES_HOST=$(POSTGRES_HOST) \
		--user=$(UID):$(UID) $(IMAGE_NAME):$(IMAGE_TAG) \
		wait-for-it --timeout=30 localhost:5432

.PHONY: sql
sql:
	podman run --rm -ti \
		--pod $(POD_NAME) \
		postgres:12 psql -h localhost -U $(POSTGRES_USER)

.PHONY: test-database
test-database: POD_NAME=$(TEST_POD_NAME) 
test-database: DATABASE_CONTAINER_NAME=$(TEST_DATABASE_CONTAINER_NAME)
test-database: database

.PHONY: stop-test-database
stop-test-database: DATABASE_CONTAINER_NAME=$(TEST_DATABASE_CONTAINER_NAME)
stop-test-database: stop-database

.PHONY: test
test: POD_NAME=$(TEST_POD_NAME) 
test: DATABASE_CONTAINER_NAME=$(TEST_DATABASE_CONTAINER_NAME)
test: 
	podman run --rm -ti --volume $(PWD):/mnt/code:rw \
		--pod $(POD_NAME) \
		--env PYTHONPATH=/mnt/code \
		--env POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) \
		--env POSTGRES_USER=$(POSTGRES_USER) \
		--env POSTGRES_DB=$(POSTGRES_DB) \
		--user=$(UID):$(UID) $(IMAGE_NAME):$(IMAGE_TAG) \
		python -m unittest tests

.PHONY: test-sql
test-sql: POD_NAME=$(TEST_POD_NAME) 
test-sql: sql

clean-coverage:
	podman run --rm -ti --volume $(PWD):/mnt/code:rw \
		--env PYTHONPATH=/mnt/code \
		--user=$(UID):$(UID) $(IMAGE_NAME):$(IMAGE_TAG) \
		coverage erase

coverage-run:
	podman run --rm -ti --volume $(PWD):/mnt/code:rw \
		--pod $(TEST_POD_NAME) \
		--env PYTHONPATH=/mnt/code \
		--env POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) \
		--env POSTGRES_USER=$(POSTGRES_USER) \
		--env POSTGRES_DB=$(POSTGRES_DB) \
		--user=$(UID):$(UID) $(IMAGE_NAME):$(IMAGE_TAG) \
		coverage run -m unittest tests

coverage-report:
	podman run --rm -ti --volume $(PWD):/mnt/code:rw \
		--env PYTHONPATH=/mnt/code \
		--user=$(UID):$(UID) $(IMAGE_NAME):$(IMAGE_TAG) \
		coverage report -m

.PHONY: coverage
coverage: clean-coverage coverage-run coverage-report

.PHONY: shell
shell:
	podman run --rm -ti --volume $(PWD):/mnt/code:rw \
		--env PYTHONPATH=/mnt/code \
		--user=$(UID):$(UID) $(IMAGE_NAME):$(IMAGE_TAG) \
		bash

.PHONY: runall
runall: database run

.PHONY: run
run: wait-database
	podman run --rm -ti --volume $(PWD):/mnt/code:rw \
		--pod $(API_POD_NAME) \
		--env PYTHONPATH=/mnt/code \
		--env POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) \
		--env POSTGRES_USER=$(POSTGRES_USER) \
		--env POSTGRES_DB=$(POSTGRES_DB) \
		--env POSTGRES_HOST=$(POSTGRES_HOST) \
		--user=$(UID):$(UID) $(IMAGE_NAME):$(IMAGE_TAG) \
		python main


