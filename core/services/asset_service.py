"""
Asset and service inventory services.
"""

import json
import logging

from sqlalchemy.orm import Session

from core.models import Asset, Service
from database.repositories import asset_repo, service_repo

logger = logging.getLogger(__name__)


class AssetService:
    """Application service for asset CRUD and queries."""

    def get_asset(self, session: Session, asset_id: str) -> Asset | None:
        return asset_repo.get_by_id(session, asset_id)

    def list_assets_by_lab(self, session: Session, lab_id: str) -> list[Asset]:
        return asset_repo.get_by_lab(session, lab_id)

    def get_asset_with_services(self, session: Session, asset_id: str) -> dict | None:
        asset = asset_repo.get_by_id(session, asset_id)
        if not asset:
            return None
        services = service_repo.get_by_asset(session, asset_id)
        return {
            "asset": asset,
            "services": services,
        }

    def count_by_lab(self, session: Session, lab_id: str) -> int:
        return len(asset_repo.get_by_lab(session, lab_id))


class ServiceService:
    """Application service for service inventory."""

    def get_service(self, session: Session, service_id: str) -> Service | None:
        return service_repo.get_by_id(session, service_id)

    def list_services_by_asset(self, session: Session, asset_id: str) -> list[Service]:
        return service_repo.get_by_asset(session, asset_id)

    def list_services_by_lab(self, session: Session, lab_id: str) -> list[Service]:
        assets = asset_repo.get_by_lab(session, lab_id)
        services = []
        for asset in assets:
            services.extend(service_repo.get_by_asset(session, asset.id))
        return services


asset_service = AssetService()
service_service = ServiceService()
