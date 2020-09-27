.PHONY: clean data lint get_data test_environment

#################################################################################
# GLOBALS                                                                       #
#################################################################################

SHELL=/bin/bash
PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
BUCKET = [OPTIONAL] your-bucket-for-syncing-data (do not include 's3://')
PROFILE = default
PROJECT_NAME = craiglist_crawler
PYTHON_INTERPRETER = python
CONDA_ROOT=$(shell conda info --base)
ENV_NAME=craiglist_crawler
MY_ENV_DIR=$(CONDA_ROOT)/envs/$(ENV_NAME)

# conda activate does stuff other than just modifying path. This is a more complete way to run a
# a command in a conda env
# Note that the extra activate is needed to ensure that the activate floats env to the front of PATH
CONDA_ACTIVATE=source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate


#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Make Dataset
data/raw/vancouver_data.parquet: test_environment
	$(PYTHON_INTERPRETER) craiglist_crawler/data/make_dataset.py \
	--metro "vancouver" \
	--output_file "data/raw/vancouver_data.parquet"

## Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Lint using flake8
lint:
	flake8 craiglist_crawler

## Download data from db

## Build Jupyter Environment
jupyter: environment test_environment
	ipython kernel install --name $(ENV_NAME) --user
	$(MY_ENV_DIR)/bin/jupyter labextension install @jupyter-widgets/jupyterlab-manager
	$(MY_ENV_DIR)/bin/jupyter labextension install jupyterlab-plotly
	$(MY_ENV_DIR)/bin/jupyter labextension install plotlywidget
	$(MY_ENV_DIR)/bin/jupyter labextension install jupyterlab-theme-solarized-dark
	$(MY_ENV_DIR)/bin/jupyter lab build --name "craigslab"

## Test python environment is set-up correctly
test_environment: environment-built
ifneq (${CONDA_DEFAULT_ENV}, $(PROJECT_NAME))
	$(error Must activate `$(PROJECT_NAME)` environment before proceeding)
endif

## Set up python interpreter environment
environment-built: environment.yml
ifneq ("$(wildcard $(MY_ENV_DIR))","") # check if the directory is there
	conda env update $(ENV_NAME) --file environment.yml --prune
else
	conda env create -f environment.yml
endif
	@echo ">>> Conda env $(ENV_NAME) ready. Activate with 'conda activate $(ENV_NAME)'"
	touch environment-built



#################################################################################
# PROJECT RULES                                                                 #
#################################################################################



#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: help
help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
