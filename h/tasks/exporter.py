import csv
from StringIO import StringIO

import os

from boxsdk import JWTAuth, Client
from celery.utils.log import get_task_logger
from datetime import datetime

from h import models, settings
from h.celery import celery

log = get_task_logger(__name__)


def to_csv(field_names, collection):
    def get_att(model, att):
        att = getattr(model, att)
        att = att.encode('utf8') if type(att) is unicode else att
        return ' '.join(str(att).split())

    def make_row(model):
        return {att: get_att(model, att) for att in field_names}

    def make_writer(sio):
        return csv.DictWriter(sio, field_names, dialect='excel')

    sio = StringIO()
    w = make_writer(sio)
    w.writeheader()

    for model in collection:
        row = make_row(model)
        w.writerow(row)

    return sio


@celery.task
def export_annotations():

    def get_field_names(model):
        field_names = []
        for p in model.__mapper__.iterate_properties:
            field_names.append(p.key)
        return field_names

    def store_tokens(access_token, refresh_token):
        os.environ['BOX_ACCESS_TOKEN'] = access_token
        if refresh_token:
            os.environ['BOX_REFRESH_TOKEN'] = refresh_token

    box_folder_id = celery.request.registry.settings['h.box_folder_id']

    auth = JWTAuth(
        client_id=celery.request.registry.settings['h.box_client_id'],
        client_secret=celery.request.registry.settings['h.box_client_secret'],
        enterprise_id=celery.request.registry.settings['h.box_enterprise_id'],
        jwt_key_id=celery.request.registry.settings['h.box_jwt_key_id'],
        rsa_private_key_passphrase=celery.request.registry.settings['h.box_rsa_private_key_pass'],
        rsa_private_key_file_sys_path=celery.request.registry.settings['h.box_rsa_private_key_path'],
        store_tokens=store_tokens
    )

    access_token = auth.authenticate_instance()
    client = Client(auth)

    annotations = celery.request.db.query(models.Annotation).all()

    if annotations:

        file_name = datetime.now().strftime('hypothesis' + '-%Y%m%d.csv')

        field_names = get_field_names(annotations[0])

        csv_file = to_csv(field_names, annotations)

        client.folder(folder_id=box_folder_id).upload_stream(csv_file, file_name)
