IMAGE_NAME := querido-diario-api
IMAGE_TAG := devel

# Database configuration
POSTGRES_PASSWORD := queridodiario
POSTGRES_USER := $(POSTGRES_PASSWORD)
POSTGRES_DB := $(POSTGRES_PASSWORD)

TEST_POD_NAME := queridodiariotests
DATABASE_CONTAINER_NAME := queridodiario-test-db

.PHONY: clean
clean: clean-coverage
	podman rmi  $(IMAGE_NAME):$(IMAGE_TAG)

.PHONY: build
build:
	podman build --build-arg LOCAL_USER_ID=$(UID) \
		--tag $(IMAGE_NAME):$(IMAGE_TAG) \
		-f build/Dockerfile build/

.PHONY: test
test: 
	podman run --rm -ti --volume $(PWD):/mnt/code:rw \
		--pod $(TEST_POD_NAME) \
		--env PYTHONPATH=/mnt/code \
		--env POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) \
		--env POSTGRES_USER=$(POSTGRES_USER) \
		--env POSTGRES_DB=$(POSTGRES_DB) \
		--user=$(UID):$(UID) $(IMAGE_NAME):$(IMAGE_TAG) \
		python -m unittest tests

clean-coverage:
	podman run --rm -ti --volume $(PWD):/mnt/code:rw \
		--env PYTHONPATH=/mnt/code \
		--user=$(UID):$(UID) $(IMAGE_NAME):$(IMAGE_TAG) \
		coverage erase

coverage-run:
	podman run --rm -ti --volume $(PWD):/mnt/code:rw \
		--env PYTHONPATH=/mnt/code \
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

.PHONY: testshell
testshell:
	podman run --rm -ti --volume $(PWD):/mnt/code:rw \
		--pod $(TEST_POD_NAME) \
		--env PYTHONPATH=/mnt/code \
		--user=$(UID):$(UID) $(IMAGE_NAME):$(IMAGE_TAG) \
		bash

.PHONY: black
black:
	podman run --rm -ti --volume $(PWD):/mnt/code:rw \
		--env PYTHONPATH=/mnt/code \
		--user=$(UID):$(UID) $(IMAGE_NAME):$(IMAGE_TAG) \
		black .

.PHONY: redo-everything
redo-everything: black build coverage

.PHONY: destroy-test-pod
destroy-test-pod:
	podman pod rm --force --ignore $(TEST_POD_NAME)

.PHONY: create-test-pod
create-test-pod: destroy-test-pod
	podman pod create --name $(TEST_POD_NAME)

.PHONY: database
database: create-test-pod
	podman run -d --rm -ti \
		--name $(DATABASE_CONTAINER_NAME) \
		--pod $(TEST_POD_NAME) \
		-e POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) \
		-e POSTGRES_USER=$(POSTGRES_USER) \
		-e POSTGRES_DB=$(POSTGRES_DB) \
		postgres:12

sql:
	podman run --rm -ti \
		--pod $(TEST_POD_NAME) \
		postgres:12 psql -h localhost -U $(POSTGRES_USER)

.PHONY: destroydatabase
destroydatabase:
	podman rm --force $(DATABASE_CONTAINER_NAME)


