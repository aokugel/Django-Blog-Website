
from storages.backends.azure_storage import AzureStorage
import os

class AzureMediaStorage(AzureStorage):
    account_name = 'djangostoracc1234' # Must be replaced by your <storage_account_name>
    account_key = os.environ.get('BLOB_MEDIA_KEY','')
    azure_container = 'media'
    expiration_secs = None

class AzureStaticStorage(AzureStorage):
    account_name = 'djangostoracc1234' # Must be replaced by your storage_account_name
    account_key = os.environ.get('BLOB_STATIC_KEY','')
    azure_container = 'static'
    expiration_secs = None