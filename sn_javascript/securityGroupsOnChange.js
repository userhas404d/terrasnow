// 1. populate aws data var with json obj
// 2. lock subnets field until security group is selected
//
// on change of security groups dropdown:
// 1. get security group id from value
// 2. load json obj var

var sgDropdownValue = g_form.getValue('tfv_SecurityGroupIds')
for (var item in json_obj['subnets']){
    if(json_obj['subnets'][item]['VpcId'] == sgDropdownValue){
        g_form.addOption('tfv_SubnetId',json_obj['subnets'][item]['SubnetId'], json_obj['subnets'][item]['Name']);
      }
    }
g_form.setDisabled('tfv_SubnetId', false);

// 3. compare json_obj['subnets']['VpcId'] and json_obj['security_group'][]
//
// 1. set values of options in security group dropdown to include subnets
// 2. lock subnets field until security group is selected
// 3. once security group is selected:
//     3a. populate the security groups dropdown with the dict stored in the value of the security group selected
//     3b. update the value of the security group selection to only include the subnetID
//
//
// question: can you create a temporary variable to store the json?
//
//
//
// g_form.getOption('tfv_SecurityGroupIds', );
