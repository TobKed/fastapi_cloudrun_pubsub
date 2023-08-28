import factory

from src.enums.image import ImageThumbnailsGenerationStatus
from src.schemas.image import ImageThumbnails


class ImageThumbnailsFactory(factory.Factory):
    class Meta:
        model = ImageThumbnails

    image_hash = factory.Faker("uuid4")
    image_url = factory.Faker("url")
    status = factory.Faker("enum", enum_cls=ImageThumbnailsGenerationStatus)
    thumbnails = [
        "http://thumbnai1.jpeg",
        "http://thumbnai2.jpeg",
    ]
