import hashlib
import logging
import time
from pathlib import Path
from uuid import UUID
from zipfile import ZipFile

from rana_sdk.application.rana_runtime import RanaRuntime
import urllib3
from threedi_api_client.api import ThreediApi
from threedi_api_client.files import upload_file
from threedi_api_client.openapi import Revision, Schematisation

UPLOAD_TIMEOUT = urllib3.Timeout(connect=60, read=600)

__all__ = ["upload_schematisation"]


def md5(fname: str | Path) -> str:
    """
    Computes the MD5 checksum of a file.

    Parameters:
    - fname (str | Path): Path to the file.

    Returns:
    - str: The MD5 checksum as a hexadecimal string.
    """
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_or_create_schematisation(
    threedi_api: ThreediApi, schematisation_name: str, organisation_uuid: str, tags: list | None
) -> Schematisation:
    contracts = threedi_api.contracts_list(organisation__unique_id=organisation_uuid)
    if contracts.count < 1:
        raise ValueError(f"Organisation with UUID {organisation_uuid} does not exist or you have insufficient rights")
    tags = tags or []
    resp = threedi_api.schematisations_list(name=schematisation_name, owner__unique_id=organisation_uuid)
    if resp.count == 1:
        logging.info(f"Schematisation '{schematisation_name}' already exists, skipping creation.")
        return resp.results[0]
    elif resp.count > 1:
        raise ValueError(f"Found > 1 schematisations named'{schematisation_name}!")

    # if not found -> create
    logging.info(f"Creating schematisation '{schematisation_name}'...")
    schematisation = threedi_api.schematisations_create(
        data={
            "owner": organisation_uuid,
            "name": schematisation_name,
            "tags": tags,
        }
    )
    return schematisation


def upload_sqlite(
    threedi_api: ThreediApi, schematisation: Schematisation, revision: Revision, sqlite_path: str | Path
) -> None:
    sqlite_path = Path(sqlite_path)
    sqlite_zip_path = sqlite_path.with_suffix(".zip")
    ZipFile(sqlite_zip_path, mode="w").write(str(sqlite_path), arcname=str(sqlite_path.name))
    upload = threedi_api.schematisations_revisions_sqlite_upload(
        id=revision.id,
        schematisation_pk=schematisation.id,
        data={"filename": str(sqlite_zip_path.name)},
    )
    if upload.put_url is None:
        logging.info(f"Sqlite '{sqlite_path.name}' already existed, skipping upload.")
    else:
        logging.info(f"Uploading '{str(sqlite_path.name)}'...")
        upload_file(upload.put_url, sqlite_zip_path, timeout=UPLOAD_TIMEOUT)


def upload_raster(
    threedi_api: ThreediApi,
    rev_id: int,
    schema_id: int,
    raster_type: str,
    raster_path: str | Path,
) -> None:
    logging.info(f"Creating '{raster_type}' raster...")
    raster_path = Path(raster_path)
    md5sum = md5(str(raster_path))
    data = {"name": raster_path.name, "type": raster_type, "md5sum": md5sum}
    raster_create = threedi_api.schematisations_revisions_rasters_create(rev_id, schema_id, data)
    if raster_create.file and raster_create.file.state == "uploaded":
        logging.info(f"Raster '{raster_path}' already exists, skipping upload.")
        return

    logging.info(f"Uploading '{raster_path}'...")
    data = {"filename": raster_path.name}
    upload = threedi_api.schematisations_revisions_rasters_upload(raster_create.id, rev_id, schema_id, data)

    upload_file(upload.put_url, raster_path, timeout=UPLOAD_TIMEOUT)


def commit_revision(threedi_api: ThreediApi, rev_id: int, schema_id: int, commit_message: str) -> str:
    # First wait for all files to have turned to 'uploaded'
    for wait_time in [0.5, 1.0, 2.0, 10.0, 30.0, 60.0, 120.0, 300.0]:
        revision = threedi_api.schematisations_revisions_read(rev_id, schema_id)
        states = [revision.sqlite.file.state]
        states.extend([raster.file.state for raster in revision.rasters])

        if all(state == "uploaded" for state in states):
            break
        elif any(state == "created" for state in states):
            logging.info(f"Sleeping {wait_time} seconds to wait for the files to become 'uploaded'...")
            time.sleep(wait_time)
            continue
        else:
            raise RuntimeError("One or more rasters have an unexpected state")
    else:
        raise RuntimeError("Some files are still in 'created' state")

    schematisation_revision = threedi_api.schematisations_revisions_commit(
        rev_id, schema_id, {"commit_message": commit_message}
    )

    logging.info(f"Committed revision {revision.number}.")
    return schematisation_revision


def upload_schematisation(
    runtime: RanaRuntime,
    organisation_uuid: str | UUID,
    schematisation_name: str,
    sqlite_path: str | Path,
    rasters_dir_name: str | Path,
    schematisation_create_tags: list[str] | None,
    commit_message: str = "auto-commit",
) -> Schematisation:
    if isinstance(organisation_uuid, str):
        organisation_uuid = UUID(organisation_uuid)
    # Schematisatie maken als die nog niet bestaat
    schematisation = get_or_create_schematisation(
        threedi_api=runtime.threedi_gateway.client,
        organisation_uuid=organisation_uuid.hex,
        schematisation_name=schematisation_name,
        tags=schematisation_create_tags,
    )
    assert schematisation.id
    # Nieuwe (lege) revisie aanmaken
    revision = runtime.threedi_gateway.client.schematisations_revisions_create(schematisation.id, data={"empty": True})

    # Data uploaden
    # # Spatialite
    upload_sqlite(
        threedi_api=runtime.threedi_gateway.client,
        schematisation=schematisation,
        revision=revision,
        sqlite_path=Path(sqlite_path),
    )

    # # Rasters
    rasters = {
        "dem.tif": "dem_file",
        "infiltration.tif": "infiltration_rate_file",
        "friction.tif": "frict_coef_file",
    }

    for filename, raster_type in rasters.items():
        upload_raster(
            threedi_api=runtime.threedi_gateway.client,
            rev_id=revision.id,
            schema_id=schematisation.id,
            raster_type=raster_type,
            raster_path=Path(rasters_dir_name) / filename,
        )

    # Commit revision
    commit_revision(
        threedi_api=runtime.threedi_gateway.client,
        rev_id=revision.id,
        schema_id=schematisation.id,
        commit_message=commit_message,
    )

    # 3Di model en simulation template genereren
    logging.info(
        "Waiting for the revision to be ready...  Follow its "
        "progress on "
        f"https://management.3di.live/schematisations/{schematisation.id}"
    )

    return schematisation
