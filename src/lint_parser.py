# auther: caleb.bryant@cyderes.com
# created: 2023/04/02

import argparse
from Tokens import createTokens

parser = argparse.ArgumentParser(
    prog='lint_parser.py',
    description='Chronicle Parser Config Linting Tool'
)

parser.add_argument('-f', '--config_file')
parser.add_argument('-t', '--log_file')
parser.add_argument('-c', '--customer')
parser.add_argument('-l', '--log_type')
parser.add_argument('-e', '--only_errors', action='store_true')

args = parser.parse_args()

chronicle_command = "chronicle parser test"
config_file = args.config_file
log_file = args.log_file
customer = args.customer
log_type = args.log_type
only_errors = args.only_errors
if config_file:
    chronicle_command += f' -f {config_file}'
if log_file:
    chronicle_command += f' -t {log_file}'
if customer:
    chronicle_command += f' -c {customer}'
if log_type:
    chronicle_command += f' -l {log_type}'
if only_errors:
    chronicle_command += f' -e'

createTokens(config_file)