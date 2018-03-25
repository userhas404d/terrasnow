"""Define Snow Category Item."""


class SnowCatalogItem(object):
    """ServiceNow Category Item."""

    def __init__(self, name, description):
        """Initialize."""
        self.name = name
        # terraform catalog sys_id
        self.catalogs = "e0ab3e2e84341300777f3b0167a0485f"
        # terraform catalog's watchmaker category
        self.category = "062ef22284741300777f3b0167a0480d"
        self.description = description
        # terraform deployment workflow
        self.workflow = "6eb4e31abc705300777f67a411c7cc7b"
        self.isactive = "true"

    def data(self):
        """Create category item data payload."""
        return {"name": self.name,
                "category": self.category,
                "sc_catalogs": self.catalogs,
                "description": self.description,
                "workflow": self.workflow,
                "active": self.isactive
                }
