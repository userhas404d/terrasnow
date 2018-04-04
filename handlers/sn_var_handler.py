"""Parse information from snow requests."""


class SnowVars(object):
    """Terraform to ServiceNow cariable converter."""

    def __init__(self, json_obj, cat_item_id):
        """Initialize."""
        self.cat_item_id = cat_item_id
        self.cat_item_list = []
        self.json_obj = json_obj
        self.counter = 0

    def parse_tf_vars(self):
        """Convert JOSN formatted terraform vars to ServiceNow vars."""
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
                    self.counter = self.counter + 10
                    order_val = self.counter
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

    def create_adv_toggle(self):
        """Create the advanced mode toggle."""
        # requires json_to_servicenow run first in order update the counter to
        # match the number of required vars
        self.counter = self.counter + 10
        self.cat_item_list.append(
             {
               "name": 'adv_toggle',
               "type": "CheckBox",
               "cat_item": self.cat_item_id,
               "question_text": "Show Advanced Options",
               "tooltip": "Select to show advanced options",
               "default_value": "",
               "order": self.counter
               })

    def get_vars(self):
        """Preform correct order of operations and return variables."""
        self.parse_tf_vars()
        self.create_adv_toggle()
        return self.cat_item_list

# print(hcl_to_json('variables.tf'))
# print(json_to_servicenow(json_obj, "12345"))
