"""Terraform invoker."""

import logging

import handlers.aws_info_getter as aws_info_getter
import invoke
import terraparse
import terrasnow
from invoke import task

# from snow_parse import combinator, input_to_json, get_sorted_obj
FORMAT = ("[%(asctime)s][%(levelname)s]" +
          "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
logging.basicConfig(filename='tasks.log', level=logging.INFO,
                    format=FORMAT)


@task
def get_attachment(ctx, user_name, user_pwd,
                   table_name, table_sys_id):
    """Call catalog item creation application."""
    # returns the file name of the attachment
    print(terrasnow.get_attachment(user_name, user_pwd, table_name,
                                   table_sys_id))


@task
def create_catalog_item(ctx, user_name, user_pwd, table_name, table_sys_id,
                        cat_item_name, cat_item_description):
    """Call catalog item creation application."""
    # returns sys id of new catalog item
    print(terrasnow.create_catalog_item(user_name, user_pwd, table_name,
                                        table_sys_id, cat_item_name,
                                        cat_item_description))


@task
def unzip_and_create_vars(ctx, user_name, user_pwd, file_name, cat_sys_id,
                          os_type):
    """Unzip template and create catalog item vars."""
    # returns the full path of the zip file's location on the local disk
    print(terrasnow.unzip_and_create_vars(user_name, user_pwd, file_name,
                                          cat_sys_id, os_type))


@task
def s3_upload(ctx, user_name, user_pwd, table_name, sys_id, file_name,
              cat_sys_id, zip_full_path, target_bucket):
    """Upload the attachment to s3."""
    print(terrasnow.s3_upload(user_name, user_pwd, table_name, sys_id,
                              file_name, cat_sys_id, zip_full_path,
                              target_bucket))


@task
def cleanup(ctx, zip_full_path):
    """Delete the downloaded attachment and tmp files."""
    print(terrasnow.cleanup(zip_full_path))


@task
def initialize(ctx, template_file, source_bucket, req_sys_id):
    """Initilize the terraform working env."""
    terraparse.get_template(template_file, source_bucket)
    working_dir = terraparse.create_working_dir(req_sys_id)
    if working_dir:
        terraparse.unzip_template(template_file, working_dir)
        terraparse.flatten_files(working_dir)
        print(working_dir)


@task
def create_var_file(ctx, input_string, target_dir):
    """Create tfvars file."""
    terraparse.get_tf_vars(input_string, target_dir)


@task
def terraform_init(ctx, target_dir):
    """Call terraform init."""
    logging.info('terraform init called')
    print(ctx.run("terraform init " + target_dir, warn=True))


@task
def terraform_plan(ctx, target_dir):
    """Call terraform plan."""
    responder = invoke.watchers.Responder(pattern=r"Enter a value:",
                                          response="\n")
    logging.info('terraform plan called')
    print(ctx.run('terraform plan -var-file=' + target_dir +
                  '/terraform.tfvars -out=' + target_dir +
                  '/terraform.plan ' + target_dir,
                  watchers=[responder],
                  warn=True))


@task
def terraform_apply(ctx, sys_id, target_dir):
    """Call terraform apply."""
    logging.info('terraform apply called')
    state_file = sys_id + '-' + 'terraform.tfstate'
    responder = invoke.watchers.Responder(pattern=r"Enter a value:",
                                          response="\n")
    print(ctx.run('terraform apply ' +
                  '-var-file=' + target_dir + '/terraform.tfvars ' +
                  '-auto-approve ' +
                  '-state=' + target_dir + '/' + state_file + ' '
                  + target_dir +
                  ' && echo "Success" >> ' + target_dir + '/apply.status ' +
                  '|| echo "Failed" >> ' + target_dir + '/apply.status',
                  watchers=[responder], warn=True))


@task
def export_terraform_state(ctx, target_dir, sys_id, target_bucket):
    """Upload the terraform state to S3."""
    logging.info('Exporting terraform state file.')
    terraparse.export_terraform_state(target_dir, sys_id, target_bucket)


@task
def tfleanup(ctx, target_dir):
    """Remove the working dir."""
    terraparse.cleanup(target_dir)


@task
def terraform_destroy(ctx):
    """Call terraform destroy."""
    logging.info('terraform destroy called')
    ctx.run('terraform destroy')


@task
def get_aws_info(ctx, target_role, duration):
    """Call aws info getter."""
    logging.info('aws_info_getter called')
    response = aws_info_getter.assumed_role_get_everything(target_role,
                                                           int(duration))
    print(response)
