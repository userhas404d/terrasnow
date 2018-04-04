"""Handle client script creations."""


class SnowClientScript(object):
    """Terraform Zip Parser."""

    def __init__(self, cat_item_id):
        """Initialize."""
        self.cat_item_id = cat_item_id
        self.client_script_list = []
        self.display_toggle_script = """
        function onChange(control, oldValue, newValue, isLoading) {
           if (isLoading || newValue == '') {
              return;
           }
           //Type appropriate comment here, and begin script below
           if(newValue == 'true'){
            for (var index = 0; index < g_form.nameMap.length; index++) {
                var unhideme = g_form.nameMap[index].prettyName;
                if(!(unhideme.startsWith('gen_')) && !(g_form.isMandatory(unhideme))){
                    g_form.setDisplay(unhideme,true);
                    }
                }
            }
            else{
                for (var i = 0; i < g_form.nameMap.length; i++) {
                    var hideme = g_form.nameMap[i].prettyName;
                    if(hideme.startsWith('gen_') || (!(g_form.isMandatory(hideme)) && hideme != 'adv_toggle')){
                        g_form.setDisplay(hideme,false);
                        }
                    }
                }

        }
        """
        self.hide_generic_vars_script = """
        function onLoad() {
            for (var index = 0; index < g_form.nameMap.length; index++) {
                var hideme = g_form.nameMap[index].prettyName;
                if(hideme.startsWith('gen_') || (!(g_form.isMandatory(hideme)) && hideme != 'adv_toggle')){
                    g_form.setDisplay(hideme,false);
                    }
                }
            }
        """

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

    def get_scripts(self):
        """Preform correct order of operations and return variables."""
        self.create_display_toggle()
        self.create_hide_generic_vars()
        return self.client_script_list
