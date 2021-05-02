IMAGE_NAMESPACE ?= serenata
IMAGE_NAME ?= querido-diario-api
IMAGE_TAG ?= latest
IMAGE_FORMAT ?= docker

# Elasticsearch ports
# Variables used to connect the app to the ElasticSearch
QUERIDO_DIARIO_ELASTICSEARCH_HOST ?= localhost
QUERIDO_DIARIO_ELASTICSEARCH_INDEX ?= gazettes
ELASTICSEARCH_PORT1 ?= 9200
ELASTICSEARCH_PORT2 ?= 9300
# Containers data
POD_NAME ?= querido-diario-api
DATABASE_CONTAINER_NAME ?= $(POD_NAME)-db
ELASTICSEARCH_CONTAINER_NAME ?= $(POD_NAME)-elasticsearch
# Run integration tests. Run local elasticsearch to validate the iteration
RUN_INTEGRATION_TESTS ?= 0

API_PORT := 8080

run-command=(podman run --rm -ti --volume $(PWD):/mnt/code:rw \
	--pod $(POD_NAME) \
	--env QUERIDO_DIARIO_ELASTICSEARCH_INDEX=$(QUERIDO_DIARIO_ELASTICSEARCH_INDEX) \
	--env QUERIDO_DIARIO_ELASTICSEARCH_HOST=$(QUERIDO_DIARIO_ELASTICSEARCH_HOST) \
	--env PYTHONPATH=/mnt/code \
	--env RUN_INTEGRATION_TESTS=$(RUN_INTEGRATION_TESTS) \
	--user=$(UID):$(UID) $(IMAGE_NAMESPACE)/$(IMAGE_NAME):$(IMAGE_TAG) $1)

wait-for=(podman run --rm -ti --volume $(PWD):/mnt/code:rw \
	--pod $(POD_NAME) \
	--env PYTHONPATH=/mnt/code \
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
	podman build --format $(IMAGE_FORMAT) --tag $(IMAGE_NAMESPACE)/$(IMAGE_NAME):$(IMAGE_TAG) \
		-f Dockerfile $(PWD)

login:
	podman login --username $(REGISTRY_USER) --password "$(REGISTRY_PASSWORD)" https://index.docker.io/v1/

.PHONY: publish
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

set-test-variables:
	$(eval POD_NAME=test-$(POD_NAME))
	$(eval DATABASE_CONTAINER_NAME=test-$(DATABASE_CONTAINER_NAME))
	$(eval API_PORT=8088)
	$(eval ELASTICSEARCH_PORT1=9201)
	$(eval ELASTICSEARCH_PORT2=9301)
	$(eval ELASTICSEARCH_CONTAINER_NAME=test-$(ELASTICSEARCH_CONTAINER_NAME))

set-integration-test-variables: set-test-variables
	$(eval RUN_INTEGRATION_TESTS=1)

.PHONY: test
test: set-test-variables create-pod retest

.PHONY: retest
retest: set-test-variables
	$(call run-command,  python -m unittest -f tests)

.PHONY: test-all
test-all: set-integration-test-variables create-pod elasticsearch retest

.PHONY: test-shell
test-shell: set-test-variables
	$(call run-command, bash)

.PHONY: coverage
coverage: set-test-variables create-pod elasticsearch
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
run: create-pod elasticsearch load-data rerun

.PHONY:load-data
load-data:
	$(call run-command, python scripts/load_fake_gazettes.py)


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
