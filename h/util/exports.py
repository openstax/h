import csv

from StringIO import StringIO

from boxsdk import JWTAuth, Client


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


def authenticate_box_client(client_id,
                            client_secret,
                            enterprise_id,
                            jwt_key_id,
                            rsa_private_key_passphrase,
                            rsa_private_key_file_sys_path,
                            store_tokens):


    auth = JWTAuth(
        client_id=client_id,
        client_secret=client_secret,
        enterprise_id=enterprise_id,
        jwt_key_id=jwt_key_id,
        rsa_private_key_passphrase=rsa_private_key_passphrase,
        rsa_private_key_file_sys_path=rsa_private_key_file_sys_path,
        store_tokens=store_tokens
    )

    auth.authenticate_instance()
    return Client(auth)
