
function_name = qms

env := missing
profile := sms-dev
region := us-west-2
stage := v1
vpc_env := dev


watch_command := make test
watch_pattern := *.py

AWS_PARAMS=AWS_PROFILE=$(profile) AWS_DEFAULT_REGION=${region}

vpc_id := $(shell ${AWS_PARAMS} aws ec2 describe-vpcs --filters "Name=tag:Environment,Values=${vpc_env}" --query Vpcs[0].VpcId --output text)
subnet_ids := $(shell ${AWS_PARAMS} aws ec2 describe-subnets --filters "Name=vpc-id,Values=${vpc_id}" --query Subnets[*].SubnetId --output text)
redis_ip := $(shell dig +short ${redis_host} | tail -n1)

SCRIPT_PARAMS=ALLOW_CIDR="${allow_cidr}" REDIS_HOST="${redis_host}" REDIS_IP="${redis_ip}" REDIS_QUERY_KEY="${redis_query_key}" REDIS_QUERY_USER="${redis_query_user}"
LAMBDA_PARAMS=ENV=${env} VPC_ID=${vpc_id} VPC_SUBNETS="${subnet_ids}" ${SCRIPT_PARAMS}

# environment
venv: ## create virtual environment
	python3 -m virtualenv venv

install: ## install virtual env requirements
	yarn install
	./venv/bin/pip3 install -r requirements/dev.txt

# testing
test: | isort flake8 pytest

isort:
	./venv/bin/isort --skip venv --skip node_modules --recursive --check-only --quiet src

flake8:
	./venv/bin/flake8 src/ tests/

pytest:
	./venv/bin/pytest --cov=src/ --cov-branch tests/

run:
	${SCRIPT_PARAMS} ./venv/bin/python3 src/list.py

watch:
	${SCRIPT_PARAMS} watchmedo shell-command --command '$(watch_command); echo "---\\\\---"' --pattern "${watch_pattern}" --recursive


# serverless
local-invoke:
	${AWS_PARAMS} ${LAMBDA_PARAMS} ./node_modules/.bin/lambda-local -t 20 -f $(function_file) -e $(event_file)

deploy:
	${AWS_PARAMS} ${LAMBDA_PARAMS} ./node_modules/.bin/serverless deploy --stage ${stage}

invoke:
	${AWS_PARAMS} ${LAMBDA_PARAMS} ./node_modules/.bin/serverless invoke --stage ${stage} -f $(function_name)

remove:
	${AWS_PARAMS} ${LAMBDA_PARAMS} ./node_modules/.bin/serverless remove --stage ${stage}
