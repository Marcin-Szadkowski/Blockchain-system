
.PHONY: reformat
reformat:
	isort . --only-modified
	black . --diff

.PHONY: broker
broker:
	docker run --rm -d --hostname my-rabbit --name some-rabbit -e RABBITMQ_DEFAULT_USER=user -e RABBITMQ_DEFAULT_PASS=password -p 8080:15672 rabbitmq:3-management && docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' some-rabbit

.PHONY: prune
prune: 
	docker kill some-rabbit