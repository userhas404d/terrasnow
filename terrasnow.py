s"""All the things."""

import json
import logging
import os
import shutil

import handlers.s3_handler as s3_handler
import handlers.sn_client_script_handler as sn_client_script_handler
import handlers.sn_cred_handler as sn_cred_handler
import handlers.sn_var_handler as sn_var_handler
import handlers.snow_cat_item as snow_cat_item
import handlers.snowgetter as snowgetter
import handlers.zip_handler as zip_handler

# Should be static (set at the workflow level?)
file_path = './templates/'
target_bucket = 'snow-terraform-testing'

FORMAT = ("[%(asctime)s][%(levelname)s]" +
          "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
logging.basicConfig(filename='terrasnow.log', level=logging.INFO,
                    format=FORMAT)


def post_ssh_creds(user_name, user_pwd, key_name, host_user_name,
                   ssh_private_key):
    """Create ssh credentials in target snow instance."""
    ssh_cred = sn_cred_handler.SnowSSHCredential(key_name, host_user_name,
                                                 ssh_private_key)
    cred_list = ssh_cred.get_creds()
    for cred in cred_list:
        snowgetter.make_ssh_cred(cred, user_name, user_pwd)


def get_attachment(user_name, user_pwd, table_name, table_sys_id,
                   attachment_sys_id, file_name):
    """Download the attachment."""
    # get the attachment's sys_id and file_name
    try:
        if table_name:
            logging.info('table name provided to get_attachment.')
            attachment_info = snowgetter.get_attachment_info(table_name,
                                                             table_sys_id,
                                                             user_name,
                                                             user_pwd)
            sys_id = attachment_info['sys_id']
            file_name = attachment_info['file_name']
        else:
            logging.info('table name not provided to get_attachment.')
            sys_id = attachment_sys_id
            file_name = file_name
        # download the attachment based on returned sys_id
        snowgetter.get_attachment(sys_id, file_name, file_path, user_name,
                                  user_pwd)
        test_dict = {}
        test_dict['FileName'] = file_name
        test_dict['AttachmentSysId'] = sys_id
        return json.dumps(test_dict)
    except TypeError as e:
        logging.exception('Query results were empty.')
        return ('ERROR: Query results were empty.' +
                ' Confirm record and attachment exist.')


def create_catalog_item(user_name, user_pwd, table_name, table_sys_id,
                        cat_item_name, cat_item_description):
    """Create the catalog item."""
    # define a new category item.
    my_cat = snow_cat_item.SnowCatalogItem(cat_item_name, cat_item_description)
    # create the category item and return it's sys_id
    cat_sys_id = snowgetter.make_cat_item(my_cat.data(), user_name, user_pwd)
    logging.info('created catalog item: {}'.format(cat_sys_id))
    return cat_sys_id


def unzip_and_create_vars(user_name, user_pwd, file_name, cat_sys_id,
                          ritm_attachment_sys_id, os_type):
    """Unzip template and create catalog item vars."""
    # unzip the downloaded file and create category item variables
    my_zip = zip_handler.zip_parser(file_name, file_path, cat_sys_id)
    my_zip.unzip()
    json_obj = my_zip.hcl_to_json(my_zip.tf_var_loc)
    sn_vars = sn_var_handler.SnowVars(json_obj, cat_sys_id,
                                      ritm_attachment_sys_id, os_type)
    var_list = sn_vars.get_vars()

    # push category item variables to snow
    for item in var_list:
        snowgetter.make_cat_var(item, user_name, user_pwd)

    # create client scripts
    script_client = sn_client_script_handler.SnowClientScript(cat_sys_id)
    client_scripts = script_client.get_scripts()
    for script in client_scripts:
        snowgetter.make_client_script(script, user_name, user_pwd)

    return my_zip.full_path


def s3_upload(user_name, user_pwd, table_name, sys_id, file_name,
              cat_sys_id, zip_full_path, target_bucket):
    """Upload attachment to s3."""
    # upload zip to s3
    s3_obj = s3_handler.Handler(file_name, cat_sys_id, zip_full_path,
                                target_bucket)
    # my_bucket.check_bucket()
    if s3_obj.upload_file():
        # var_item_data = {"uri": my_bucket.obj_uri}
        var_item_data = {
           "name": 'gen_S3_URI',
           "type": 'URI',
           "cat_item": cat_sys_id,
           "question_text": 'S3 URI',
           "tooltip": 'S3 URI',
           "default_value": s3_obj.obj_uri,
           "help_text": 'S3 URI'
           }
        snowgetter.make_cat_var(var_item_data, user_name, user_pwd)
        var_item_data = {
           "name": 'gen_S3_obj_name',
           "type": 'String',
           "cat_item": cat_sys_id,
           "question_text": 'S3 object name',
           "tooltip": 'S3 object name',
           "default_value": s3_obj.upload_file_name,
           "help_text": 'S3 URI'
           }
        snowgetter.make_cat_var(var_item_data, user_name, user_pwd)
        var_item_data = {
           "name": 'gen_S3_bucket',
           "type": 'String',
           "cat_item": cat_sys_id,
           "question_text": 'S3 bucket',
           "tooltip": 'S3 bucket',
           "default_value": s3_obj.target_bucket,
           "help_text": 'S3 URI'
           }
        snowgetter.make_cat_var(var_item_data, user_name, user_pwd)
    else:
        return 'File upload failed.'


def s3_reupload(file_name, cat_sys_id, zip_full_path, target_bucket):
    """Reupload template to S3."""
    s3_obj = s3_handler.Handler(file_name, cat_sys_id, zip_full_path,
                                target_bucket)
    s3_obj.upload_file()
    return "SUCESS"


def delete_S3obj(file_name, cat_sys_id, target_bucket):
    """Remove S3 object."""
    zip_full_path = ""
    s3_obj = s3_handler.Handler(file_name, cat_sys_id, zip_full_path,
                                target_bucket)
    s3_obj.delete_obj()
    return "SUCESS"


def cleanup(zip_full_path):
    """Delete the local zip file."""
    os.remove(zip_full_path)
    try:
        shutil.rmtree('./templates/tmp')
        return "Attachment download removed from local disk."
    except FileNotFoundError as e:
        logging.exception('directory is not present.')
        return "tmp directory not present."
