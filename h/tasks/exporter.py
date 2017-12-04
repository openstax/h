import os

from celery.utils.log import get_task_logger
from datetime import datetime

from h import models, settings
from h.celery import celery
from h.util.exports import to_csv, authenticate_box_client

log = get_task_logger(__name__)


@celery.task
def export_annotations():

    def store_tokens(access_token, refresh_token):
        os.environ['BOX_ACCESS_TOKEN'] = access_token
        if refresh_token:
            os.environ['BOX_REFRESH_TOKEN'] = refresh_token

    box_folder_id = celery.request.registry.settings['h.box_folder_id']

    client = authenticate_box_client(
        client_id=celery.request.registry.settings['h.box_client_id'],
        client_secret=celery.request.registry.settings['h.box_client_secret'],
        enterprise_id=celery.request.registry.settings['h.box_enterprise_id'],
        jwt_key_id=celery.request.registry.settings['h.box_jwt_key_id'],
        rsa_private_key_passphrase=celery.request.registry.settings[
            'h.box_rsa_private_key_pass'],
        rsa_private_key_file_sys_path=celery.request.registry.settings[
            'h.box_rsa_private_key_path'],
        store_tokens=store_tokens
    )

    annotation = models.Annotation
    app_url = celery.request.registry.settings['h.app_url']

    annotations = celery.request.db.query(
        annotation.id.label('annotation_id'),
        annotation.created.label('created_on'),
        annotation.updated.label('updated_on'),
        annotation.deleted.label('is_deleted'),
        annotation.document_id,
        annotation.tags,
        annotation.target_selectors[0]['research_identifier'].label('research_id'),
        annotation._text.label('annotated_text'),
        annotation.target_selectors[0]['content'].label('highlighted_text'),
        annotation._target_uri.label('module_id')
    ).distinct(annotation.id).all()

    attrs = [
        'annotation_id',
        'created_on',
        'updated_on',
        'is_deleted',
        'document_id',
        'tags',
        'research_id',
        'annotated_text',
        'highlighted_text',
        'module_id'
    ]

    if annotations:
        file_name = datetime.now().strftime(app_url + '-%Y%m%d.csv')

        csv_file = to_csv(attrs, annotations)

        client.folder(folder_id=box_folder_id).upload_stream(csv_file,
                                                             file_name)
