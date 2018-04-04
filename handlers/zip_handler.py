"""Parse information from snow requests."""

# # import logging
import json
import pathlib
import shlex
import subprocess
import zipfile


class zip_parser(object):
    """Terraform Zip Parser."""

    def __init__(self, zip_name, zip_path, cat_item_id):
        """Initialize."""
        self.zip_name = zip_name
        self.zip_path = zip_path
        self.cat_item_id = cat_item_id
        self.cat_item_list = []
        self.full_path = self.zip_path + zip_name
        self.json_obj = []
        self.tf_var_file = 'variables.tf'
        self.tf_out_file = 'outputs.tf'
        # file locations in zip file
        self.var_file_loc = self.get_file_path(self.tf_var_file)
        self.out_file_loc = self.get_file_path(self.tf_out_file)
        # file locations on local disk
        self.unzip_path = './templates/tmp'
        self.tf_var_loc = '{0}/{1}'.format(self.unzip_path, self.var_file_loc)
        self.tf_out_loc = '{0}/{1}'.format(self.unzip_path, self.out_file_loc)
        self.tf_files = [self.tf_var_loc, self.tf_out_loc]

    def get_file_path(self, tf_file):
        """Set outputs.tf and variables.tf file locations."""
        # remove file exension from file name
        return (pathlib.PurePosixPath(self.zip_name).stem + '/' + tf_file)

    def unzip(self):
        """Validate zip."""
        try:
            snow_zip = zipfile.ZipFile(self.full_path)
            zip_test = snow_zip.testzip()
            if zip_test is None:
                try:
                    snow_zip.extract(self.var_file_loc,
                                     path=self.unzip_path)
                    snow_zip.extract(self.out_file_loc,
                                     path=self.unzip_path)
                except KeyError as e:
                    print('ERROR: Required files not present in archive.')
            else:
                print(zip_test)
                raise
        except zipfile.BadZipFile as e:
            print("ERROR: Bad zip file")

    def hcl_to_json(self, tf_loc):
        """Convert HCL format files to JSON."""
        tf_loc = shlex.quote(tf_loc)
        cmd = 'json2hcl -reverse <' + tf_loc
        process = subprocess.run(cmd,
                                 shell=True,
                                 universal_newlines=True,
                                 stdout=subprocess.PIPE)
        self.json_obj.append(json.loads(process.stdout))

    def json_to_servicenow(self):
        """Convert JOSN formatted terraform vars to ServiceNow vars."""
        counter = 0
        for var_list in self.json_obj[0]['variable']:
            for key in var_list:
                var_name = key
                mandatory_toggle = 'false'
                if var_list[key][0]['type'] == 'string':
                    obj_type = 'String'
                try:
                    def_val = var_list[key][0]['default']
                    order_val = 1000
                except KeyError as e:
                    mandatory_toggle = 'true'
                    counter = counter + 10
                    order_val = counter
                    def_val = ""
                desc = var_list[key][0]['description']
                self.cat_item_list.append(
                     {
                       "name": 'tfv_' + var_name,
                       "type": obj_type,
                       "cat_item": self.cat_item_id,
                       "question_text": var_name,
                       "tooltip": desc,
                       "default_value": def_val,
                       "help_text": desc,
                       "order": order_val,
                       "mandatory": mandatory_toggle
                       })
        return self.cat_item_list


# print(hcl_to_json('variables.tf'))
# print(json_to_servicenow(json_obj, "12345"))
