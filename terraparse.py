"""Parse ServiceNow Terraform Catalog item."""

import json
import logging
import os
import pathlib
import shutil
import time
import zipfile

import handlers.s3_handler as s3_handler

FORMAT = ("[%(asctime)s][%(levelname)s]" +
          "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
logging.basicConfig(filename='terraparse.log', level=logging.INFO,
                    format=FORMAT)

templates_path = "./templates"

# [Workflow activity #1]
# check that template has been downloaded
#    if not download it.


def get_template(template_file, source_bucket):
    """Confirm the terraform template is on disk."""
    my_file = pathlib.Path("{0}/{1}".format(templates_path, template_file))
    if my_file.is_file():
        logging.info('File found on local disk.')
    else:
        logging.info('File not found. Retrieving from S3.')
        s3_obj = s3_handler.Handler(template_file, "", my_file, source_bucket)
        s3_obj.download_obj()


def create_working_dir(req_sys_id):
    """Create the working directory."""
    directory = './templates/' + req_sys_id
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info('Created working directory')
        return directory
    else:
        logging.error('Working directory exists.')
        print('ERROR')
        return None


def unzip_template(template_file, working_dir):
    """Unzip the terraform template into the working directory."""
    template_file = './templates/' + template_file
    while not os.path.exists(template_file):
        time.sleep(1)
    if os.path.isfile(template_file):
        with zipfile.ZipFile(template_file, "r") as zip_ref:
            zip_ref.extractall(working_dir)
        logging.info('Unzipped template to: {}'.format(working_dir))
    else:
        raise ValueError("%s isn't a file!" % template_file)


# https://forum.quartertothree.com/t/automatically-moving-files-from-subdirectories-up-to-parent-directory/64445/6
def flatten_files(working_dir):
    """Move all files in sub directories to here, then delete subdirs."""
    for root, dirs, files in os.walk(working_dir, topdown=False):
        if root != working_dir:
            for name in files:
                source = os.path.join(root, name)
                target = os.path.join(working_dir, name)
                os.rename(source, target)

        for name in dirs:
            os.rmdir(os.path.join(root, name))


# [Workflow acticity #2]
# convert sn json object to terraform readible object

def input_to_json(input_string):
    """Convert input string to JSON."""
    try:
        output_json_obj = json.loads(input_string)
        logging.info('Received valid input string.')
        return output_json_obj
    except ValueError as e:
        logging.exception('ServiceNow returned invalid JSON.')
        print('ERROR')
        exit()


def remove_prefix(text, prefix):
    """Remove string prefix."""
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def write_contents(filename, contents):
    """Write to output file."""
    contents = json.dumps(contents, indent=4)
    with open(filename, 'w') as outfile:
        outfile.write(contents)


def get_sorted_obj(json_obj):
    """Parse ServiceNow variable json object."""
    # need to filter out gen_ and tfo_ vars before sending to function
    raw_vars = {}
    for var in json_obj:
        if var.startswith('tfv_'):
            rm_prefix = remove_prefix(var, 'tfv_')
            raw_vars[rm_prefix] = json_obj[var]
    return raw_vars


def get_tf_vars(input_string, target_dir):
    """Create variables json file."""
    logging.info('input_string: {}'.format(input_string))
    logging.info('target_dir: {}'.format(target_dir))
    while not os.path.exists(target_dir):
        logging.info('target dir not found. waiting.. ')
        time.sleep(1)
    if os.path.exists(target_dir):
        logging.info('target directory: {} exists.'.format(target_dir))
        full_file_name = target_dir + '/' + 'terraform.tfvars'
        json_obj = input_to_json(input_string)
        json_obj = get_sorted_obj(json_obj)
        write_contents(full_file_name, json_obj)
        print('SUCCESS')


def terraform_apply_completion_check(target_dir):
    """Looped check for terraform apply status."""
    logging.info('confirming terraform apply completed.')
    status_file = target_dir + '/apply.status'
    while not os.path.exists(status_file):
        time.sleep(1)
    if os.path.isfile(status_file):
        check = open(status_file, 'r')
        if 'Success' in check.read():
            logging.info('terraform apply exucted successfully.')
            check.close()
            return True
        else:
            logging.error('terraform apply exuction encounterd errors.')
            check.close()
            return False


def export_terraform_state(target_dir, sys_id, target_bucket):
    """Upload terraform statefile to s3."""
    if terraform_apply_completion_check(target_dir):
        state_file = sys_id + '-' + 'terraform.tfstate'
        state_file_path = target_dir + '/' + state_file
        s3 = s3_handler.Handler(state_file, '', state_file_path,
                                target_bucket)
        s3.upload_file()
        print('SUCCESS')
        logging.info('Uploaded state file to s3.')
    else:
        logging.erro('Failed to upload state file to s3.')
        print('ERROR')


def cleanup(target_dir):
    """Remove the terraform folder."""
    shutil.rmtree(target_dir)
    print('SUCCESS')

# get_template('lx-instance-test.zip', 'snow-terraform-testing')
# get_tf_vars(snow_req_input, './templates/')
