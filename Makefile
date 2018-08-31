DOCKER_TAG = dev

GULP := node_modules/.bin/gulp

# Unless the user has specified otherwise in their environment, it's probably a
# good idea to refuse to install unless we're in an activated virtualenv.
ifndef PIP_REQUIRE_VIRTUALENV
PIP_REQUIRE_VIRTUALENV = 1
endif
export PIP_REQUIRE_VIRTUALENV

.PHONY: default
default: test

build/manifest.json: node_modules/.uptodate
	$(GULP) build

## Clean up runtime artifacts (needed after a version update)
.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	rm -f node_modules/.uptodate .pydeps
	rm -rf build

.PHONY: env
env:
	@bin/hypothesis authclient add --name openstax --authority openstax.org --type confidential | tail -n 2 | sed -e 's/Client ID: /HYPOTHESIS_CLIENT_ID=/' | sed -e 's/Client Secret: /HYPOTHESIS_CLIENT_SECRET=/'

## Run the development H server locally
.PHONY: dev
dev:
	@echo "initializing hypothesis..."
	@bin/hypothesis init

ifneq ($(add_credentials_to),)
	@echo "generating credentials..."
	@make -s env > "$(add_credentials_to)"
endif

	@echo "starting server..."
	@init-env supervisord -c conf/supervisord.conf

## Build hypothesis/hypothesis docker image
.PHONY: docker
docker:
	git archive HEAD | docker build -t openstax/hypothesis-server:$(DOCKER_TAG) -

## Run test suite
.PHONY: test
test: node_modules/.uptodate
	@pip install -q tox
	tox
	$(GULP) test

################################################################################

# Fake targets to aid with deps installation
.pydeps: requirements.txt
	@echo installing python dependencies
	@pip install --use-wheel -r requirements-dev.in tox
	@touch $@

node_modules/.uptodate: package.json
	@echo installing javascript dependencies
	@node_modules/.bin/check-dependencies 2>/dev/null || npm install
	@touch $@

# Self documenting Makefile
.PHONY: help
help:
	@echo "The following targets are available:"
	@echo " env        Generates content that can be added to an .env file with api credentials"
	@echo " clean      Clean up runtime artifacts (needed after a version update)"
	@echo " dev        Run the development H server locally. Can specify path to environment file with the add_credentials_to option"
	@echo " docker     Build hypothesis/hypothesis docker image"
	@echo " test       Run the test suite (default)"
