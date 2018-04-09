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
        self.dropdown_population_script = """
        function onLoad() {
        function getAWSAccountInfo(){
            var ga = new GlideAjax("TerraformAWSAccountQuery");
            // add name parameter to define which function we want to call
            // method name in script include will be getFavorites
            ga.addParam("sysparm_name", "getAWSAccountInfo");
            // make syncronus GlideAjax call
            ga.getXMLWait();
            var workflowSysId = ga.getAnswer();
            jslog("getAwsAccountInfo response: " + workflowSysId);
            var workflowGlideRecord = getWorkflowGlideRecord(workflowSysId);
            var jsonObj = getWorkflowResults(workflowGlideRecord);
            return jsonObj;
        }

        function getWorkflowGlideRecord(sysId){
            var gr = new GlideRecord('wf_context');
            gr.addQuery('sys_id', sysId);
            gr.query();
            while(gr.next()){return gr;}
        }

        function getWorkflowResults(workflowGlideRecord){
            var result = workflowGlideRecord.scratchpad;
         // jslog('json_obj: ' + result);
            // convert scratchpad string result to json obj
            var test = JSON.parse(result);
            // extract 'aws account info' as json string from scratchpad json obj
            var json_str = test['json_obj'];
         // jslog("result json: " +json_str);
         // convert 'aws account info' json string into json obj
            var json_obj = JSON.parse(json_str);
         // pass json obj to set_values function
            return json_obj;
        }

        function setValues(json_obj){
           //Type appropriate comment here, and begin script below
           jslog(typeof json_obj);
           jslog('made it this far');
           jslog('json_obj: '+json_obj);
           for (var list in json_obj['amis']){
           //gs.log(list);
             for (var key in json_obj['amis'][list]){
                 if (json_obj['amis'][list][key]['ImageId']){
                 g_form.addOption('tfv_AmiId', json_obj['amis'][list][key]['ImageId'],json_obj['amis'][list][key]['Name']);
                 g_form.addOption('tfv_AmiDistro', json_obj['amis'][list][key]['OSType'], json_obj['amis'][list][key]['OSType'] );
             }
           }
         }

          for (var key0 in json_obj['key_pairs']){
              if(json_obj['key_pairs'][key0]['KeyName']){
                  g_form.addOption('tfv_KeyPairName',json_obj['key_pairs'][key0]['KeyName'], json_obj['key_pairs'][key0]['KeyName']);
            }
          }

          for (var key1 in json_obj['vpcs']){
              if(json_obj['vpcs'][key1]['Name']){
              g_form.addOption('tfv_SubnetId',json_obj['vpcs'][key1]['VpcId'], json_obj['vpcs'][key1]['Name']);
            }
          }

          for (var key2 in json_obj['security_groups']){
              if(json_obj['security_groups'][key2]['Name']){
                g_form.addOption('tfv_SecurityGroupIds', json_obj['security_groups'][key2]['GroupId'], json_obj['security_groups'][key2]['Name']);
              }
          }
        }

    function showLoadingOverlay(){
        showLoadingDialog();
        setTimeout(function() {
            setValues(getAWSAccountInfo());
            hideLoadingDialog();
        }, 1000);
    }

//Show the loading dialog immediately as the form loads
showLoadingOverlay();
// var json_str = waitForElement(sys_id);


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
