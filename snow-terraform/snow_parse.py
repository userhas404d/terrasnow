"""Parse servicenow input."""
import json
import logging

logging.basicConfig(filename='snow_parse.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
# log.setLevel(logging.INFO)


# [x]group vars based on template or 'generic'
# [x]create var group for reusable vars
# [x]move vars to variable sets and add prefixes to their names
# [x]test assume role deployments (add role to EC2 instance..)
# [x]test from the EC2 Instance
# [x]add admin assume role to variable inputs in servicenow
# [x]chain this with tasks.py

# figure out way to handle outputs :(
# check that the assume role works and alert snow if it doesn't
# once assume role is verified check the resources called out:
#   keypair
#   ami-id
#   SecurityGroupIds
#   VPCs

# how to handle outputs..(send/log results back to snow)
# account for multiple providers?

# snow_req_input = """{
#     "gen_template_name":"",
#     "tfv_Name":"test stack",
#     "tfv_AmiId":"ami-1c8ee466",
#     "gen_template_path":"",
#     "tfv_AmiDistro":"CentOS",
#     "gen_AssumeRoleToggle":"Yes",
#     "tfv_InstanceType":"t2.micro",
#     "tfv_InstanceRole":"",
#     "gen_credential_type":"",
#     "tfv_KeyPairName":"tf_instance",
#     "gen_credential_key":"",
#     "pvdr_Provider":"aws",
#     "tfv_NoPublicIp":"true",
#     "ar_AssumeRoleArn":"",
#     "tfv_NoReboot":"false",
#     "ar_ExternalId":"EXTERNAL_ID",
#     "tfv_NoUpdates":"false",
#     "ar_SessionName":"SESSION_NAME",
#     "tfv_SecurityGroupIds":"sg-91c51be4",
#     "mod_ModuleName":"",
#     "tfv_PypiIndexUrl":"https://pypi.org/simple",
#     "tfv_WatchmakerConfig":"",
#     "mod_ModuleSource":"git::https://github.com/plus3it/terraform-aws-watchamker//modules/lx-instance",
#     "tfv_WatchmakerEnvironment":"",
#     "tfv_WatchmakerComputerName":"",
#     "tfv_WatchmakerOuPath":"",
#     "tfv_WatchmakerAdminGroups":"",
#     "tfv_WatchmakerAdminUsers":"",
#     "tfv_AppScriptUrl":"",
#     "tfv_AppScriptParams":"",
#     "tfv_AppScriptShell":"bash",
#     "tfv_AppVolumeDevice":"false",
#     "tfv_AppVolumeMountPath":"/opt/data",
#     "tfv_AppVolumeSize":"1",
#     "tfv_AppVolumeType":"gp2",
#     "tfv_PrivateIp":"",
#     "tfv_SubnetId":"subnet-81a03fe5",
#     "tfv_CfnEndpointUrl":"https://cloudformation.us-east-1.amazonaws.com",
#     "tfv_CfnGetPipUrl":"https://bootstrap.pypa.io/get-pip.py",
#     "tfv_CfnBootstrapUtilsUrl":"https://s3.amazonaws.com/cloudformation-examples/aws-cfn-bootstrap-latest.tar.gz",
#     "tfv_OnFailureAction":"DO_NOTHING",
#     "tfv_ToggleCfnInitUpdate":"A"
#     }"""


def input_to_json(input_string):
    """Convert input string to JSON."""
    try:
        output_json_obj = json.loads(input_string)
        logging.info('Received valid input string.')
        return output_json_obj
    except ValueError as e:
        logging.exception('ServiceNow returned invalid JSON.')


def remove_prefix(text, prefix):
    """Remove string prefix."""
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def get_sorted_obj(obj):
    """Sort input variables."""
    # ar_ = assume role
    # gen_ = generic
    # mod_ = module
    # pvdr_ = provider
    # tfv_ = terraform variable
    sorted_dict = {"assume_role": {}, "generic": {}, "module": {},
                   "provider": {}, "variables": {}}
    d_assume_role = {}
    d_generic = {}
    d_module = {}
    d_provider = {}
    d_variables = {}
    for var in obj:
        if var.startswith("ar_"):
            rm_prefix = remove_prefix(var, "ar_")
            d_assume_role[rm_prefix] = obj[var]
        elif var.startswith("gen_"):
            rm_prefix = remove_prefix(var, "gen_")
            d_generic[rm_prefix] = obj[var]
        elif var.startswith("mod_"):
            rm_prefix = remove_prefix(var, "mod_")
            d_module[rm_prefix] = obj[var]
        elif var.startswith("pvdr_"):
            rm_prefix = remove_prefix(var, "pvdr_")
            d_provider[rm_prefix] = obj[var]
        elif var.startswith("tfv_"):
            rm_prefix = remove_prefix(var, "tfv_")
            d_variables[rm_prefix] = obj[var]

    sorted_dict['assume_role'] = d_assume_role
    sorted_dict['generic'] = d_generic
    sorted_dict['module'] = d_module
    sorted_dict['provider'] = d_provider
    sorted_dict['variables'] = d_variables
    logging.info('Input variables successfully sorted.')
    return sorted_dict


def get_provider_block(assume_role_toggle, assume_role_arn,
                       session_name, external_id):
    """Create provider block of template."""
    if assume_role_toggle == "Yes":
        provider_block_contents = (get_assume_role_block(assume_role_arn,
                                                         session_name,
                                                         external_id))
    else:
        provider_block_contents = ""

    provider_block = ("""
    provider "aws" {{
            {}
        }}
    """).format(provider_block_contents)
    return provider_block


def get_assume_role_block(assume_role_arn, session_name, external_id):
    """Return the assume role block."""
    return """
        assume_role {{
                role_arn = "{}"
                session_name = "{}"
                external_id = "{}"
            }}
        """.format(assume_role_arn, session_name, external_id)


def get_module_block(module_name, module_source):
    """Return the module block."""
    return ("""
        module "{}" {{
            source = "{}"
    """).format(module_name, module_source)


def get_var_block(input_obj):
    """Return list of var pairs."""
    var_list = []
    for var in input_obj:
        if input_obj[var] != "":
            pair_string = "{} = \"{}\"".format(var, input_obj[var])
            pair_string = """
                    {}
            """.format(pair_string)
            var_list.append(pair_string)
            output_obj = ''.join(var_list)
    return output_obj


def write_contents(filename, contents):
    """Write to output file."""
    with open(filename, 'w') as file:
        file.write(contents)


def combinator(snow_req_output):
    """Combine all the things."""
    logging.info('Starting combinator.')
    logging.info('Recieved obj: {}'.format(snow_req_output))
    file_name = "test.txt"
    file_contents = []
    template_status = "FAIL"
    try:
        assume_role_toggle = snow_req_output['generic']['AssumeRoleToggle']
        assume_role_arn = snow_req_output['assume_role']['AssumeRoleArn']
        session_name = snow_req_output['assume_role']['SessionName']
        external_id = snow_req_output['assume_role']['ExternalId']
        module_name = snow_req_output['module']['ModuleName']
        module_source = snow_req_output['module']['ModuleSource']
        file_contents.append(get_provider_block(assume_role_toggle,
                                                assume_role_arn,
                                                session_name, external_id))
        logging.info('get_provider_block executed successfully')
        file_contents.append(get_module_block(module_name, module_source))
        logging.info('get_module_block executed successfully')
        file_contents.append(get_var_block(snow_req_output['variables']))
        logging.info('get_var_block executed successfully')

        file_contents.append('}')

        file_contents = ''.join(file_contents)
        write_contents(file_name, file_contents)
        logging.info('successfully wrote contents of template.')
        template_status = "SUCCESS"
        logging.info('template built successfully.')
    except ValueError as e:
        logging.exception('Required variable missing from SN catalog item.')
    except KeyError as e:
        logging.exception('Variables have not been sorted.')
    finally:
        logging.info("Returing status: {}".format(template_status))
        return template_status


# combinator(input_to_json(snow_req_input))

# new_dict = get_sorted_obj(input_to_json(snow_req_input))
# print(new_dict['assume_role']['ExternalId'])
