IMAGE_NAMESPACE ?= okfn-brasil
IMAGE_NAME ?= querido-diario-api
IMAGE_TAG ?= latest
IMAGE_FORMAT ?= docker

# Opensearch ports
# Variables used to connect the app to the OpenSearch
QUERIDO_DIARIO_DATABASE_CSV ?= censo.csv
OPENSEARCH_PORT1 ?= 9200
OPENSEARCH_PORT2 ?= 9300
# Containers data
POD_NAME ?= querido-diario
DATABASE_CONTAINER_NAME ?= $(POD_NAME)-db
OPENSEARCH_CONTAINER_NAME ?= $(POD_NAME)-opensearch
OTEL_COLLECTOR_CONTAINER_NAME ?= $(POD_NAME)-otel-collector
# Database info user to run the tests
POSTGRES_USER ?= companies
POSTGRES_PASSWORD ?= companies
POSTGRES_DB ?= companiesdb
POSTGRES_HOST ?= localhost
POSTGRES_PORT ?= 5432
POSTGRES_IMAGE ?= docker.io/postgres:10
DATABASE_RESTORE_FILE ?= contrib/data/queridodiariodb.tar
# Run integration tests. Run local opensearch to validate the iteration
RUN_INTEGRATION_TESTS ?= 0

OTEL_COLLECTOR_PORT := 4317
API_PORT := 8080

run-command=(podman run --rm -ti --volume $(PWD):/mnt/code:rw \
	--pod $(POD_NAME) \
	--env PYTHONPATH=/mnt/code \
	--env RUN_INTEGRATION_TESTS=$(RUN_INTEGRATION_TESTS) \
	--env-file config/current.env \
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

.PHONY: publish-tag
publish-tag:
	podman tag $(IMAGE_NAMESPACE)/$(IMAGE_NAME):${IMAGE_TAG} $(IMAGE_NAMESPACE)/$(IMAGE_NAME):$(shell git describe --tags)
	podman push $(IMAGE_NAMESPACE)/$(IMAGE_NAME):$(shell git describe --tags)

.PHONY: destroy
destroy:
	podman rmi --force $(IMAGE_NAMESPACE)/$(IMAGE_NAME):$(IMAGE_TAG)

destroy-pod:
	podman pod rm --force --ignore $(POD_NAME)

create-pod: setup-environment destroy-pod
	podman pod create --publish $(API_PORT):$(API_PORT) \
	  --publish $(POSTGRES_PORT):$(POSTGRES_PORT) \
	  --publish $(OPENSEARCH_PORT1):$(OPENSEARCH_PORT1) \
	  --publish $(OPENSEARCH_PORT2):$(OPENSEARCH_PORT2) \
	  --publish $(OTEL_COLLECTOR_PORT):$(OTEL_COLLECTOR_PORT) \
	  --name $(POD_NAME)

.PHONY: setup-environment
setup-environment:
	-cp --no-clobber config/sample.env config/current.env
	test -f censo.csv || curl -s -O https://querido-diario.nyc3.cdn.digitaloceanspaces.com/censo/censo.csv
	test -f themes_config.json || curl -s -O https://raw.githubusercontent.com/okfn-brasil/querido-diario-data-processing/main/config/themes_config.json

set-test-variables:
	$(eval POD_NAME=test-$(POD_NAME))
	$(eval DATABASE_CONTAINER_NAME=test-$(DATABASE_CONTAINER_NAME))
	$(eval API_PORT=8088)
	$(eval OPENSEARCH_PORT1=9201)
	$(eval OPENSEARCH_PORT2=9301)
	$(eval OPENSEARCH_CONTAINER_NAME=test-$(OPENSEARCH_CONTAINER_NAME))
	$(eval QUERIDO_DIARIO_DATABASE_CSV="")

set-integration-test-variables: set-test-variables
	$(eval RUN_INTEGRATION_TESTS=1)

.PHONY: test
test: set-test-variables create-pod retest

.PHONY: retest
retest: set-test-variables black
	$(call run-command,  python -m unittest discover tests)

.PHONY: test-all
test-all: set-integration-test-variables create-pod opensearch database retest

.PHONY: test-shell
test-shell: set-test-variables
	$(call run-command, bash)

.PHONY: coverage
coverage: set-test-variables create-pod opensearch database
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
run: create-pod opensearch database otel-collector load-data re-run

.PHONY:load-data
load-data:
	$(call run-command, python scripts/load_fake_gazettes.py)

.PHONY: re-run
re-run: setup-environment wait-opensearch wait-database
	$(call run-command, opentelemetry-instrument python main)

.PHONY: runshell
runshell:
	$(call run-command, bash)


opensearch: stop-opensearch start-opensearch wait-opensearch

start-opensearch:
	podman run -d --rm -ti \
		--name $(OPENSEARCH_CONTAINER_NAME) \
		--pod $(POD_NAME) \
		--env discovery.type=single-node \
		--env plugins.security.ssl.http.enabled=false \
		opensearchproject/opensearch:2.9.0

stop-opensearch:
	podman rm --force --ignore $(OPENSEARCH_CONTAINER_NAME)

wait-opensearch:
	$(call wait-for, localhost:9200)

.PHONY: stop-database
stop-database:
	podman rm --force --ignore $(DATABASE_CONTAINER_NAME)

.PHONY: database
database: stop-database start-database wait-database

start-database:
	podman run -d --rm -ti \
		--name $(DATABASE_CONTAINER_NAME) \
		--pod $(POD_NAME) \
		-e POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) \
		-e POSTGRES_USER=$(POSTGRES_USER) \
		-e POSTGRES_DB=$(POSTGRES_DB) \
		$(POSTGRES_IMAGE)

wait-database:
	$(call wait-for, localhost:5432)

load-database:
ifneq ("$(wildcard $(DATABASE_RESTORE_FILE))","")
	podman cp $(DATABASE_RESTORE_FILE) $(DATABASE_CONTAINER_NAME):/mnt/dump_file
	podman exec $(DATABASE_CONTAINER_NAME) bash -c "pg_restore -v -c -h localhost -U $(POSTGRES_USER) -d $(POSTGRES_DB) /mnt/dump_file || true"
else
	@echo "cannot restore because file does not exists '$(DATABASE_RESTORE_FILE)'"
	@exit 1
endif

.PHONY: otel-collector
otel-collector: stop-otel-collector start-otel-collector wait-otel-collector

start-otel-collector:
	podman run -d --rm -ti \
		--name $(OTEL_COLLECTOR_CONTAINER_NAME) \
		--pod $(POD_NAME) \
		--volume $(PWD)/config/otel-collector-config.yaml:/etc/otel-collector-config.yaml \
		docker.io/otel/opentelemetry-collector-contrib:0.97.0 "--config=/etc/otel-collector-config.yaml"

stop-otel-collector:
	podman rm --force --ignore $(OTEL_COLLECTOR_CONTAINER_NAME)

wait-otel-collector:
	$(call wait-for, localhost:4317)

otel-auto-instrumentation-list:
	@echo "These packages were detected and can be auto-instrumented (maybe add/update them in requirements.txt):"
	@$(call run-command, opentelemetry-bootstrap -a requirements)
