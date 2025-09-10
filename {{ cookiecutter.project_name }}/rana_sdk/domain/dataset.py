from clean_python import ValueObject
from pydantic import AnyHttpUrl

from .lizard_raster import LizardRaster

__all__ = ["RanaDataset", "RanaDatasetLizardRaster"]


class ResourceIdentifier(ValueObject):
    code: str
    link: AnyHttpUrl | None


class RanaDataset(ValueObject):
    """Subset of fields of the Dataset get and search response"""

    id: str
    title: str  # mapped from resourceTitleObject.default
    resource_identifier: list[ResourceIdentifier] = []

    def get_id_for_namespace(self, namespace: AnyHttpUrl) -> str | None:
        """Returns the id of given namespace, otherwise None."""
        for identifier in self.resource_identifier:
            if identifier.link == namespace:
                return identifier.code
        return None


class RanaDatasetLizardRaster(RanaDataset):
    id: str
    title: str  # mapped from resourceTitleObject.default
    resource_identifier: list[ResourceIdentifier] = []
    lizard_raster: LizardRaster

    def get_id_for_namespace(self, namespace: AnyHttpUrl) -> str | None:
        """Returns the id of given namespace, otherwise None."""
        for identifier in self.resource_identifier:
            if identifier.link == namespace:
                return identifier.code
        return None
