"""Parse ServiceNow Terraform Catalog item."""

import json
import logging
import os
import pathlib
import time
import zipfile

import handlers.s3_handler as s3_handler

logging.basicConfig(filename='terraparse.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

templates_path = "./templates"

# [Workflow activity #1]
# check that template has been downloaded
#    if not download it.


def get_template(template_file, source_bucket):
    """Confirm the terraform template is on disk."""
    my_file = pathlib.Path("{0}/{1}".format(templates_path, template_file))
    if my_file.is_file():
        logging.info('File found on local disk.')
        print('SUCCESS.')
    else:
        logging.info('File not found. Retrieving from S3.')
        s3_obj = s3_handler.Handler(template_file, "", my_file, source_bucket)
        s3_obj.download_obj()
        print('SUCCESS')


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
    while not os.path.exists(working_dir):
        time.sleep(1)

    if os.path.isfile(working_dir):
        with zipfile.ZipFile(template_file, "r") as zip_ref:
            zip_ref.extractall(working_dir)
        logging.info('Unzipped template to: {}'.format(working_dir))
    else:
        raise ValueError("%s isn't a file!" % working_dir)


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
    try:
        full_file_name = target_dir + 'terraform.tfvars'
        json_obj = input_to_json(input_string)
        json_obj = get_sorted_obj(json_obj)
        write_contents(full_file_name, json_obj)
        print('SUCCESS')
    except FileNotFoundError as e:
        logging.exception('target directory does not exist.')
        print('ERROR')

# [workflow activity #3]
# run terraform init


# get_template('lx-instance-test.zip', 'snow-terraform-testing')
# get_tf_vars(snow_req_input, './templates/')
