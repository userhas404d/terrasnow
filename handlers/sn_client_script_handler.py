"""Handle client script creations."""

import os


class SnowClientScript(object):
    """Terraform Zip Parser."""

    def __init__(self, cat_item_id):
        """Initialize."""
        self.cat_item_id = cat_item_id
        self.client_script_list = []
        self.sn_javascript_path = '../sn_javascript/'
        self.display_toggle_script = (
          self.getJavascriptText('createDisplayToggleOnload.js'))
        self.hide_generic_vars_script = (
          self.getJavascriptText('hideGenericVariablesOnLoad.js'))
        self.dropdown_population_script = (
          self.getJavascriptText('populateDropdownsOnLoad.js'))

    def getJavascriptText(self, target_file):
        """Return text of the target file."""
        jspath = os.path.abspath(os.path.relpath(self.sn_javascript_path))
        with open(jspath + '/' + target_file) as file:
            script_text = file.read()
        return script_text

    def create_display_toggle(self):
        """Create the dispaly toggle client script."""
        self.client_script_list.append(
             {
                 "active": "true",
                 "name": "display toggle",
                 "applies_to": "A Catalog item",
                 "ui_type": "0",
                 "type": "onChange",
                 "cat_item": self.cat_item_id,
                 "cat_variable": "adv_toggle",
                 "applies_catalog": "true",
                 "applies_sc_task": "true",
                 "script": self.display_toggle_script
             })

    def create_hide_generic_vars(self):
        """Create the dispaly toggle client script."""
        self.client_script_list.append(
             {
                 "active": "true",
                 "name": "hide generic vars",
                 "applies_to": "A Catalog item",
                 "ui_type": "0",
                 "type": "onLoad",
                 "cat_item": self.cat_item_id,
                 "applies_catalog": "true",
                 "applies_sc_task": "true",
                 "script": self.hide_generic_vars_script
             })

    def create_population_dropdown(self):
        """Create the dispaly toggle client script."""
        self.client_script_list.append(
             {
                 "active": "true",
                 "name": "populate dropdowns",
                 "applies_to": "A Catalog item",
                 "ui_type": "0",
                 "type": "onLoad",
                 "cat_item": self.cat_item_id,
                 "applies_catalog": "true",
                 "applies_sc_task": "true",
                 "script": self.dropdown_population_script
             })

    def get_scripts(self):
        """Preform correct order of operations and return variables."""
        self.create_display_toggle()
        self.create_hide_generic_vars()
        self.create_population_dropdown()
        return self.client_script_list
