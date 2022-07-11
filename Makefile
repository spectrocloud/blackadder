VERSION ?= $(shell git describe --always)
REGISTRY := docker.io
ORG      := oz123
PROJ     := blackadder
IMG      := $(REGISTRY)/$(ORG)/$(PROJ):$(VERSION)

docker-build:
	docker build -t $(REGISTRY)/$(ORG)/grafzahl:$(VERSION) .


docker-push:
	docker push $(REGISTRY)/$(ORG)/grafzahl:$(VERSION)

