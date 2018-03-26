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


@task
def get_attachment(ctx, user_name, user_pwd,
                   table_name, table_sys_id):
    """Call catalog item creation application."""
    # returns the file name of the attachment
    return terrasnow.get_attachment(user_name, user_pwd, table_name,
                                    table_sys_id)


@task
def create_catalog_item(ctx, user_name, user_pwd, table_name, table_sys_id,
                        cat_item_name, cat_item_description):
    """Call catalog item creation application."""
    # returns sys id of new catalog item
    return terrasnow.create_catalog_item(user_name, user_pwd, table_name,
                                         table_sys_id, cat_item_name,
                                         cat_item_description)


@task
def unzip_and_create_vars(ctx, user_name, user_pwd, file_name, cat_sys_id):
    """Unzip template and create catalog item vars."""
    # returns the full path of the zip file's location on the local disk
    return terrasnow.unzip_and_create_vars(user_name, user_pwd, file_name,
                                           cat_sys_id)


@task
def s3_upload(ctx, user_name, user_pwd, table_name, sys_id, file_name,
              cat_sys_id, zip_full_path, target_bucket):
    """Upload the attachment to s3."""
    return terrasnow.s3_upload(user_name, user_pwd, table_name, sys_id,
                               file_name, cat_sys_id, zip_full_path,
                               target_bucket)


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
