IMAGE_NAMESPACE ?= okfn-brasil
IMAGE_NAME ?= querido-diario-api
IMAGE_TAG ?= latest
IMAGE_FORMAT ?= docker

# Architecture detection and configuration
CURRENT_ARCH := $(shell uname -m)
ifeq ($(CURRENT_ARCH),x86_64)
    DEFAULT_PLATFORM := linux/amd64
else ifeq ($(CURRENT_ARCH),aarch64)
    DEFAULT_PLATFORM := linux/arm64
else ifeq ($(CURRENT_ARCH),arm64)
    DEFAULT_PLATFORM := linux/arm64
else
    DEFAULT_PLATFORM := linux/amd64
endif

# Allow override via command line flags
ifdef amd64
    PLATFORM := linux/amd64
else ifdef arm64
    PLATFORM := linux/arm64
else
    PLATFORM := $(DEFAULT_PLATFORM)
endif

# Opensearch ports
# Variables used to connect the app to the OpenSearch
QUERIDO_DIARIO_DATABASE_CSV ?= censo.csv
OPENSEARCH_PORT1 ?= 9200
OPENSEARCH_PORT2 ?= 9300
# Containers data
POD_NAME ?= querido-diario
DATABASE_CONTAINER_NAME ?= $(POD_NAME)-db
OPENSEARCH_CONTAINER_NAME ?= $(POD_NAME)-opensearch
# Database info user to run the tests
POSTGRES_COMPANIES_USER ?= companies
POSTGRES_COMPANIES_PASSWORD ?= companies
POSTGRES_COMPANIES_DB ?= companiesdb
POSTGRES_COMPANIES_HOST ?= localhost
POSTGRES_COMPANIES_PORT ?= 5432
POSTGRES_COMPANIES_IMAGE ?= docker.io/postgres:10
DATABASE_RESTORE_FILE ?= contrib/data/queridodiariodb.tar
# Run integration tests. Run local opensearch to validate the iteration
RUN_INTEGRATION_TESTS ?= 0

API_PORT := 8080

run-command=docker compose run --rm api $1

wait-for=docker compose run --rm api wait-for-it --timeout=90 $1

.PHONY: black
black:
	$(call run-command, black .)

.PHONY: build
build:
	docker build --platform $(PLATFORM) --tag $(IMAGE_NAMESPACE)/$(IMAGE_NAME):$(IMAGE_TAG) \
		-f Dockerfile $(PWD)

.PHONY: build-multi-arch
build-multi-arch:
	docker buildx build --platform linux/amd64,linux/arm64 --tag $(IMAGE_NAMESPACE)/$(IMAGE_NAME):$(IMAGE_TAG) \
		-f Dockerfile $(PWD)

login:
	docker login --username $(REGISTRY_USER) --password "$(REGISTRY_PASSWORD)" https://index.docker.io/v1/

.PHONY: publish
publish:
	docker tag $(IMAGE_NAMESPACE)/$(IMAGE_NAME):${IMAGE_TAG} $(IMAGE_NAMESPACE)/$(IMAGE_NAME):$(shell date --rfc-3339=date --utc)
	docker push $(IMAGE_NAMESPACE)/$(IMAGE_NAME):$(shell date --rfc-3339=date --utc)
	docker push $(IMAGE_NAMESPACE)/$(IMAGE_NAME):${IMAGE_TAG}

.PHONY: publish-tag
publish-tag:
	docker tag $(IMAGE_NAMESPACE)/$(IMAGE_NAME):${IMAGE_TAG} $(IMAGE_NAMESPACE)/$(IMAGE_NAME):$(shell git describe --tags)
	docker push $(IMAGE_NAMESPACE)/$(IMAGE_NAME):$(shell git describe --tags)

.PHONY: destroy
destroy:
	docker rmi --force $(IMAGE_NAMESPACE)/$(IMAGE_NAME):$(IMAGE_TAG)

destroy-services:
	docker compose down --volumes --remove-orphans

create-services: setup-environment destroy-services
	docker compose up -d postgres opensearch

.PHONY: setup-environment
setup-environment:
	-cp --no-clobber config/sample.env config/current.env
	test -f censo.csv || curl -s -O https://data.queridodiario.ok.org.br/censo/censo.csv
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
test: set-test-variables create-services retest

.PHONY: retest
retest: set-test-variables black
	$(call run-command, python -m unittest discover tests)

.PHONY: test-all
test-all: set-integration-test-variables create-services retest

.PHONY: test-shell
test-shell: set-test-variables
	$(call run-command, bash)

.PHONY: coverage
coverage: set-test-variables create-services
	$(call run-command, coverage erase)
	$(call run-command, coverage run -m unittest tests)
	$(call run-command, coverage report -m)

.PHONY: shell
shell:
	$(call run-command, bash)

.PHONY: run
run: create-services load-data re-run

.PHONY:load-data
load-data:
	$(call run-command, python scripts/load_fake_gazettes.py)

.PHONY: re-run
re-run: setup-environment wait-opensearch wait-database
	$(call run-command, python main)

.PHONY: runshell
runshell:
	$(call run-command, bash)


opensearch: stop-opensearch start-opensearch wait-opensearch

start-opensearch:
	docker compose up -d opensearch

stop-opensearch:
	docker compose stop opensearch

wait-opensearch:
	$(call wait-for, opensearch:9200)

.PHONY: stop-database
stop-database:
	docker compose stop postgres

.PHONY: database
database: stop-database start-database wait-database

start-database:
	docker compose up -d postgres

wait-database:
	$(call wait-for, postgres:5432)

load-database:
ifneq ("$(wildcard $(DATABASE_RESTORE_FILE))","")
	docker compose cp $(DATABASE_RESTORE_FILE) postgres:/mnt/dump_file
	docker compose exec postgres bash -c "pg_restore -v -c -h localhost -U $(POSTGRES_COMPANIES_USER) -d $(POSTGRES_COMPANIES_DB) /mnt/dump_file || true"
else
	@echo "cannot restore because file does not exists '$(DATABASE_RESTORE_FILE)'"
	@exit 1
endif

.PHONY: help-arch
help-arch:
	@echo "Architecture build options:"
	@echo "  make build                - Build for current architecture ($(DEFAULT_PLATFORM))"
	@echo "  make build amd64=1        - Build for AMD64 architecture"
	@echo "  make build arm64=1        - Build for ARM64 architecture"
	@echo "  make build-multi-arch     - Build for both amd64 and arm64 architectures"
	@echo ""
	@echo "Current system architecture: $(CURRENT_ARCH) -> $(DEFAULT_PLATFORM)"
