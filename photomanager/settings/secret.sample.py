# Django secret key.
SECRET_KEY = ""

# Set to False in production.
# If in production, also add to ALLOWED_HOSTS.
DEBUG = False
ALLOWED_HOSTS = []

# If running behind a reverse proxy and you are using HTTPS, set to True
SOCIAL_AUTH_REDIRECT_IS_HTTPS = False

SOCIAL_AUTH_NEXTCLOUD_KEY = ""
SOCIAL_AUTH_NEXTCLOUD_SECRET = ""
NEXTCLOUD_URI = ""  # Hostname of your Nextcloud instance, like "nextcloud.example.com"

# Whether to enable tagging using Tensorflow/Keras for images
# or not. Be warned: you should have at least, at the bare minimum
# 4 GiB of RAM to use automatic tagging. Even with 4 GiB of RAM,
# you will experience slowdowns.
ENABLE_TENSORFLOW_TAGGING = True

# Same for face recognition.
ENABLE_FACE_RECOGNITION = True


# Configure your database and cache here.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "",  # Database name
        "USER": "",  # Database user
        "PASSWORD": "",  # Database password
        "HOST": "postgres",  # Database hostname
        "PORT": "5432",  # Database port number
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "",  # in the format redis://{{ HOSTNAME }}:{{ PORT NUMBER }}/1
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}
