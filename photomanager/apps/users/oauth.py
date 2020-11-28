from django.conf import settings
from social_core.backends.oauth import BaseOAuth2


class NextcloudOAuth2(BaseOAuth2):
    name = "nextcloud"
    AUTHORIZATION_URL = f"https://{settings.NEXTCLOUD_URI}/apps/oauth2/authorize"
    ACCESS_TOKEN_URL = f"https://{settings.NEXTCLOUD_URI}/apps/oauth2/api/v1/token"
    ACCESS_TOKEN_METHOD = "POST"

    def get_scope(self):
        return ["read"]

    def get_user_details(self, profile):
        return {
            "username": profile["ocs"]["data"]["id"],
            "email": profile["ocs"]["data"]["email"],
        }

    def user_data(self, access_token, *args, **kwargs):
        return self.get_json(
            f"https://{settings.NEXTCLOUD_URI}/ocs/v2.php/cloud/user?format=json",
            headers={"Authorization": f"Bearer {access_token}"},
        )
