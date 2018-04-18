"""Create a servicenow credential."""


class SnowSSHCredential(object):
    """ServiceNow Credential."""

    def __init__(self, key_name, user_name, ssh_private_key):
        """Initialize."""
        self.key_name = key_name
        self.user_name = user_name
        self.ssh_private_key = ssh_private_key
        self.ssh_cred_list = []

    def create_ssh_cred(self):
        """Create client script data block from REST call."""
        self.ssh_cred_list.append(
             {
                 "user_name": self.user_name,
                 "type": "ssh_private_key",
                 "ssh_private_key": self.ssh_private_key,
                 "sys_class_name": "ssh_private_key_credentials",
                 "tag": "terraform",
                 "order": "100",
                 "active": "true",
                 "classification": "ssh",
                 "name": self.key_name
             })

    def get_creds(self):
        """Return list of credentials."""
        self.create_ssh_cred()
        return self.ssh_cred_list
