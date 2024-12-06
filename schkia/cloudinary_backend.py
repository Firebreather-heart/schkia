import cloudinary.exceptions
import cloudinary.uploader
import cloudinary.api
import cloudinary
from django.conf import settings
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


@deconstructible
class CustomCloudinaryStorage(Storage):
    def __init__(self):
        self.cloud_name = settings.CLOUDINARY_STORAGE['CLOUD_NAME']
        self.api_key = settings.CLOUDINARY_STORAGE['API_KEY']
        self.api_secret = settings.CLOUDINARY_STORAGE['API_SECRET']
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            api_proxy="http://proxy.server:3128"
        )

    def _open(self, name, mode='rb'):
        # Opening files directly from Cloudinary is not implemented
        raise NotImplementedError(
            "This backend does not support opening files.")

    def _save(self, name, content):
        # Upload content to Cloudinary
        upload_data = cloudinary.uploader.upload(content)
        return upload_data['public_id']

    def delete(self, name):
        # Delete a file from Cloudinary
        cloudinary.uploader.destroy(name)

    def exists(self, name):
        # Check if a file exists in Cloudinary
        try:
            cloudinary.api.resource(name)
            return True
        except cloudinary.exceptions.NotFound:
            return False

    def url(self, name):
        # Get the URL of the file in Cloudinary
        return cloudinary.CloudinaryImage(name).build_url()
