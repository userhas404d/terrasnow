"""Terraform invoker."""

import logging

import invoke
from invoke import task

import terrasnow
from snow_parse import combinator, input_to_json, get_sorted_obj

logging.basicConfig(filename='tasks.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


@task
def var_convert(ctx, convert):
    """Convert snow vars to terraform template."""
    EVAL = combinator(get_sorted_obj(input_to_json(convert)))
    if EVAL == 'SUCCESS':
        logging.info('Successfully invoked snow_parse.')
    else:
        logging.exception('Error occured when calling snow_parse.' +
                          'View snow_parse logs for more information.')


# create_cat_item(user_name, user_pwd, table_name, table_sys_id,
#                    cat_item_name, cat_item_description):


@task
def create_terraform_cat_item(ctx, user_name, user_pwd,
                              table_name, table_sys_id,
                              cat_item_name, cat_item_description):
    """Call catalog item creation application."""
    terrasnow.create_cat_item(user_name, user_pwd, table_name, table_sys_id,
                              cat_item_name, cat_item_description)


@task
def terraform_init(ctx):
    """Call terraform init."""
    logging.info('terraform init called')
    ctx.run("terraform init")


@task
def terraform_plan(ctx):
    """Call terraform plan."""
    responder = invoke.watchers.Responder(pattern=r"Enter a value:",
                                          response="\n")
    logging.info('terraform plan called')
    ctx.run('terraform plan', watchers=[responder])


@task
def terraform_apply(ctx):
    """Call terraform apply."""
    logging.info('terraform apply called')
    responder = invoke.watchers.Responder(pattern=r"Enter a value:",
                                          response="\n")
    ctx.run('terraform apply -auto-approve', watchers=[responder])


@task
def terraform_destroy(ctx):
    """Call terraform destroy."""
    logging.info('terraform destroy called')
    ctx.run('terraform destroy')
