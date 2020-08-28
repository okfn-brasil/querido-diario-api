IMAGE_NAME := querido-diario-api
IMAGE_TAG := latest

.PHONY: clean
clean: clean-coverage
	podman rmi  $(IMAGE_NAME):$(IMAGE_TAG)

.PHONY: build-container-images
build-container-images:
	podman build --build-arg LOCAL_USER_ID=$(UID) \
		--tag $(IMAGE_NAME):$(IMAGE_TAG) \
		-f build/Dockerfile build/

.PHONY: test
test:
	podman run --rm -ti --volume $(PWD):/mnt/code:rw \
		--env PYTHONPATH=/mnt/code \
		--user=$(UID):$(UID) $(IMAGE_NAME):$(IMAGE_TAG) \
		python -m unittest tests

apitest:
	podman run --rm -ti --volume $(PWD):/mnt/code:rw \
		--env PYTHONPATH=/mnt/code \
		--user=$(UID):$(UID) $(IMAGE_NAME):$(IMAGE_TAG) \
		pytest -v tests/api_tests.py

clean-coverage:
	rm -f .coverage

.PHONY: coverage
coverage: clean-coverage
	podman run --rm -ti --volume $(PWD):/mnt/code:rw \
		--env PYTHONPATH=/mnt/code \
		--user=$(UID):$(UID) $(IMAGE_NAME):$(IMAGE_TAG) \
		coverage erase && coverage run -m unittest tests && coverage report -m

.PHONY: shell
shell:
	podman run --rm -ti --volume $(PWD):/mnt/code:rw \
		--env PYTHONPATH=/mnt/code \
		--user=$(UID):$(UID) $(IMAGE_NAME):$(IMAGE_TAG) \
		bash

.PHONY: black
black:
	podman run --rm -ti --volume $(PWD):/mnt/code:rw \
		--env PYTHONPATH=/mnt/code \
		--user=$(UID):$(UID) $(IMAGE_NAME):$(IMAGE_TAG) \
		black .
