"""Storage boundaries for files that must not be served as public media."""

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible
from django.utils.functional import cached_property


@deconstructible
class PrivateAttachmentStorage(FileSystemStorage):
    """Use a separate root with no public URL for chat attachments."""

    @cached_property
    def base_location(self):
        return str(settings.PRIVATE_MEDIA_ROOT)

    @cached_property
    def base_url(self):
        return None
