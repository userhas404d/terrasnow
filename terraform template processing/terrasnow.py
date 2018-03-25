"""All the things."""

import s3_handler
import snow_cat_item
import snowgetter
import zip_handler

# Should be static (set at the workflow level?)
file_path = './templates/'
target_bucket = 'snow-terraform-testing'


def create_cat_item(user_name, user_pwd, table_name, table_sys_id,
                    cat_item_name, cat_item_description):
    """Create a terraform catalog item."""
    # get the attachment's sys_id and file_name
    attachment_info = snowgetter.get_attachment_info(table_name, table_sys_id,
                                                     user_name, user_pwd)
    sys_id = attachment_info['sys_id']
    file_name = attachment_info['file_name']
    # download the attachment based on returned sys_id
    snowgetter.get_attachment(sys_id, file_name, file_path, user_name,
                              user_pwd)

    # define a new category item.
    my_cat = snow_cat_item.SnowCatalogItem(cat_item_name, cat_item_description)
    # create the category item and return it's sys_id
    cat_sys_id = snowgetter.make_cat_item(my_cat.data(), user_name, user_pwd)

    # unzip the downloaded file and create category item variables
    my_zip = zip_handler.zip_parser(file_name, file_path, cat_sys_id)
    my_zip.unzip()
    my_zip.hcl_to_json(my_zip.tf_var_loc)
    my_zip.hcl_to_json(my_zip.tf_out_loc)
    var_list = my_zip.json_to_servicenow()

    # push category item variables to snow
    for item in var_list:
        snowgetter.make_cat_var(item, user_name, user_pwd)

    # upload zip to s3
    my_bucket = s3_handler.Handler(file_name, cat_sys_id, my_zip.full_path,
                                   target_bucket)
    # my_bucket.check_bucket()
    if my_bucket.upload_file():
        var_item_data = {"uri": my_bucket.obj_uri}
        snowgetter.update_snow_var_value(table_name, sys_id, var_item_data,
                                         user_name, user_pwd)
    else:
        print('File upload failed.')
