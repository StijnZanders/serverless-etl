
test-cli:
	python core/cli/cli.py --gcp-keyfile "test key file" --gcp-project "test project"
test:
	python core
deploy:
	terraform apply