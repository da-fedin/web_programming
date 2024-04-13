# Set variables
VENV_DIR := venv
SCRIPTS_DIR := scripts
PS_SCRIPT := $(SCRIPTS_DIR)/build_project.ps1
REQUIREMENTS_FILE := requirements.txt

.PHONY: build-project-linux
# Build project
build-project-linux:
	@echo '----- Build run -----'
	@chmod +x scripts/build.sh
	@scripts/build.sh
	@echo '----- Build done -----'

# Install pre-commit hook
.PHONY: pre-commit-install
pre-commit-install:
	.venv/bin/pre-commit install

# Run pre-commit hook
.PHONY: pre-commit-run
pre-commit-run:
	.venv/bin/pre-commit run