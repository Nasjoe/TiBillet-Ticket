import json
import logging

import requests
from django.conf import settings

from AuthBillet.models import RsaKey, TibilletUser
from BaseBillet.models import Configuration
from fedow_connect.models import FedowConfig
from fedow_connect.utils import sign_message, data_to_b64, verify_signature

logger = logging.getLogger(__name__)


### GENERIC GET AND POST ###
def _post(config: FedowConfig = None,
          user: TibilletUser = None,
          data: dict = None,
          path: str = None,
          apikey: str = None):
    fedow_domain = config.fedow_domain()

    # Pour la création, on prend la clé api de Root. On rempli apikey
    # Si vide, on prend la clé du lieu du tenant
    if apikey is None:
        apikey = config.fedow_place_admin_apikey

    # Signature de la requete
    private_key = user.get_private_key()
    signature = sign_message(
        data_to_b64(data),
        private_key,
    ).decode('utf-8')

    # Ici, on s'autovérifie :
    # Assert volontaire. Si non effectué en prod, ce n'est pas grave.
    # logger.debug("_post verify_signature start")
    assert verify_signature(user.get_public_key(),
                            data_to_b64(data),
                            signature)

    session = requests.Session()
    request_fedow = session.post(
        f"https://{fedow_domain}/{path}/",
        headers={
            "Authorization": f"Api-Key {apikey}",
            "Signature": f"{signature}",
            "Content-type": "application/json",
        },
        data=json.dumps(data),
        verify=bool(not settings.DEBUG),
    )

    # TODO: Vérifier la signature de FEDOW avec root_config.fedow_primary_pub_pem

    session.close()
    return request_fedow


def _get(config: FedowConfig = None,
         user: TibilletUser = None,
         path: str = None, apikey=None):
    fedow_domain = config.fedow_domain()

    # Pour la création, on prend la clé api de Root. On rempli apikey
    # Si vide, on prend la clé du lieu du tenant
    if apikey is None:
        apikey = config.fedow_place_admin_apikey

    # Signature de la requete : on signe le path
    private_key = user.get_private_key()
    # Signature de la requete : on signe la clé

    signature = sign_message(
        apikey.encode('utf8'),
        private_key,
    ).decode('utf-8')

    # Ici, on s'autovérifie :
    # Assert volontaire. Si non effectué en prod, ce n'est pas grave.
    assert verify_signature(user.get_public_key(),
                            apikey.encode('utf8'),
                            signature)

    session = requests.Session()
    request_fedow = session.get(
        f"https://{fedow_domain}/{path}/",
        headers={
            'Authorization': f'Api-Key {apikey}',
            "Signature": f"{signature}",
        },
        verify=bool(not settings.DEBUG),
    )
    session.close()
    # TODO: Vérifier la signature de FEDOW
    return request_fedow


class WalletFedow():
    def __init__(self, config):
        self.config: FedowConfig = config
        if not config:
            self.config = FedowConfig.get_solo()

    def get_or_create(self, user: TibilletUser):
        # email = user.email
        # pub_key = user.get_public_key()
        # response_link = _post(self.config, 'wallet', {"email": email})
        pass


class PlaceFedow():
    def __init__(self, config):
        self.config: FedowConfig = config
        if not config:
            self.config = FedowConfig.get_solo()

    def create(self, admin: TibilletUser = None, place_name=None):
        # Pour la création, on prend la clé api de Root
        apikey = self.config.get_fedow_create_place_apikey()
        data = {
            'place_name': place_name,
            'admin_email': admin.email,
            'admin_pub_pem': admin.get_public_pem(),
        }

        import ipdb; ipdb.set_trace()
        new_place = _post(config=self.config,
                          user=admin,
                          path='place',
                          data=data, apikey=apikey)


# from fedow_connect.fedow_api import FedowAPI
class FedowAPI():
    def __init__(self, config: FedowConfig = None):
        self.config = config
        if config is None:
            self.config = FedowConfig.get_solo()

        self.wallet = WalletFedow(self.config)
        self.place = PlaceFedow(self.config)

    def handshake(self):
        pass
