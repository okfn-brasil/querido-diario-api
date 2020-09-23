IMAGE_NAMESPACE ?= serenata
IMAGE_NAME ?= querido-diario-api
IMAGE_TAG ?= latest

# Database configuration
POSTGRES_PASSWORD ?= queridodiario
POSTGRES_USER ?= $(POSTGRES_PASSWORD)
POSTGRES_DB ?= $(POSTGRES_PASSWORD)
POSTGRES_HOST ?= localhost
# Elasticsearch ports
# Variables used to connect the app to the ElasticSearch
QUERIDO_DIARIO_ELASTICSEARCH_HOST ?= localhost
QUERIDO_DIARIO_ELASTICSEARCH_INDEX ?= gazettes
ELASTICSEARCH_PORT1 ?= 9200
ELASTICSEARCH_PORT2 ?= 9300
# Containers data
POD_NAME ?= queridodiarioapi
DATABASE_CONTAINER_NAME ?= queridodiario-db
ELASTICSEARCH_CONTAINER_NAME ?= queridodiario-elasticsearch

API_PORT := 8080

run-command=(podman run --rm -ti --volume $(PWD):/mnt/code:rw \
	--pod $(POD_NAME) \
	--env QUERIDO_DIARIO_ELASTICSEARCH_INDEX=$(QUERIDO_DIARIO_ELASTICSEARCH_INDEX) \
	--env QUERIDO_DIARIO_ELASTICSEARCH_HOST=$(QUERIDO_DIARIO_ELASTICSEARCH_HOST) \
	--env PYTHONPATH=/mnt/code \
	--env POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) \
	--env POSTGRES_HOST=$(POSTGRES_HOST) \
	--env POSTGRES_USER=$(POSTGRES_USER) \
	--env POSTGRES_DB=$(POSTGRES_DB) \
	--user=$(UID):$(UID) $(IMAGE_NAMESPACE)/$(IMAGE_NAME):$(IMAGE_TAG) $1)

wait-for=(podman run --rm -ti --volume $(PWD):/mnt/code:rw \
	--pod $(POD_NAME) \
	--env PYTHONPATH=/mnt/code \
	--env POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) \
	--env POSTGRES_USER=$(POSTGRES_USER) \
	--env POSTGRES_DB=$(POSTGRES_DB) \
	--env POSTGRES_HOST=$(POSTGRES_HOST) \
	--user=$(UID):$(UID) \
	$(IMAGE_NAMESPACE)/$(IMAGE_NAME):$(IMAGE_TAG) wait-for-it --timeout=30 $1)

.PHONY: black
black:
	podman run --rm -ti --volume $(PWD):/mnt/code:rw \
		--env PYTHONPATH=/mnt/code \
		--user=$(UID):$(UID) $(IMAGE_NAMESPACE)/$(IMAGE_NAME):$(IMAGE_TAG) \
		black .

.PHONY: build
build:
	podman build --tag $(IMAGE_NAMESPACE)/$(IMAGE_NAME):$(IMAGE_TAG) \
		-f build/Dockerfile $(PWD)

login:
	podman login --username $(REGISTRY_USER) --password "$(REGISTRY_PASSWORD)" https://index.docker.io/v1/

.PHONY:
publish:
	podman tag $(IMAGE_NAMESPACE)/$(IMAGE_NAME):${IMAGE_TAG} $(IMAGE_NAMESPACE)/$(IMAGE_NAME):$(shell date --rfc-3339=date --utc)
	podman push $(IMAGE_NAMESPACE)/$(IMAGE_NAME):$(shell date --rfc-3339=date --utc) 
	podman push $(IMAGE_NAMESPACE)/$(IMAGE_NAME):${IMAGE_TAG}

.PHONY: destroy
destroy:
	podman rmi --force $(IMAGE_NAMESPACE)/$(IMAGE_NAME):$(IMAGE_TAG)

destroy-pod:
	podman pod rm --force --ignore $(POD_NAME)

create-pod: destroy-pod
	podman pod create --publish $(API_PORT):$(API_PORT) \
		--publish $(ELASTICSEARCH_PORT1):$(ELASTICSEARCH_PORT1) \
		--publish $(ELASTICSEARCH_PORT2):$(ELASTICSEARCH_PORT2) \
		--name $(POD_NAME)

.PHONY: stop-database
stop-database:
	podman rm --force --ignore $(DATABASE_CONTAINER_NAME)

.PHONY: database
database: start-database wait-database

start-database:
	podman run -d --rm -ti \
		--name $(DATABASE_CONTAINER_NAME) \
		--pod $(POD_NAME) \
		-e POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) \
		-e POSTGRES_USER=$(POSTGRES_USER) \
		-e POSTGRES_DB=$(POSTGRES_DB) \
		postgres:12

wait-database:
	$(call wait-for, localhost:5432)

.PHONY: sql
sql:
	podman run --rm -ti \
		--pod $(POD_NAME) \
		postgres:12 psql -h localhost -U $(POSTGRES_USER)

set-test-variables:
	$(eval POD_NAME=test-$(POD_NAME))
	$(eval DATABASE_CONTAINER_NAME=test-$(DATABASE_CONTAINER_NAME))
	$(eval API_PORT=8088)
	$(eval ELASTICSEARCH_PORT1=9201)
	$(eval ELASTICSEARCH_PORT2=9301)
	$(eval ELASTICSEARCH_CONTAINER_NAME=test-$(ELASTICSEARCH_CONTAINER_NAME))

.PHONY: test
test: set-test-variables create-pod database elasticsearch retest

.PHONY: retest
retest: set-test-variables
	$(call run-command, python -m unittest -f tests)

.PHONY: test-sql
test-sql: set-test-variables sql

.PHONY: test-shell
test-shell: set-test-variables
	$(call run-command, bash)

.PHONY: coverage
coverage: set-test-variables
	$(call run-command, coverage erase)
	$(call run-command, coverage run -m unittest tests)
	$(call run-command, coverage report -m)

.PHONY: shell
shell:
	podman run --rm -ti --volume $(PWD):/mnt/code:rw \
		--env PYTHONPATH=/mnt/code \
		--user=$(UID):$(UID) $(IMAGE_NAMESPACE)/$(IMAGE_NAME):$(IMAGE_TAG) \
		bash

.PHONY: run
run: create-pod elasticsearch rerun


.PHONY: rerun
rerun: wait-elasticsearch
	$(call run-command, python main)

.PHONY: runshell
runshell:
	$(call run-command, bash)


elasticsearch: stop-elasticsearch start-elasticsearch wait-elasticsearch

start-elasticsearch:
	podman run -d --rm -ti \
		--name $(ELASTICSEARCH_CONTAINER_NAME) \
		--pod $(POD_NAME) \
		--env discovery.type=single-node \
		elasticsearch:7.9.1

stop-elasticsearch:
	podman rm --force --ignore $(ELASTICSEARCH_CONTAINER_NAME)

wait-elasticsearch:
	$(call wait-for, localhost:9200)
