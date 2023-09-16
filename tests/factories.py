import factory

from src.enums.image import ImageAnnotationsGenerationStatus
from src.schemas.image import ImageClassification


class ImageClassificationFactory(factory.Factory):
    class Meta:
        model = ImageClassification

    image_hash = factory.Faker("uuid4")
    image_url = factory.Faker("url")
    status = factory.Faker("enum", enum_cls=ImageAnnotationsGenerationStatus)
    annotations = [
        {"index": 1, "label": "Egyptian cat", "confidence": 0.94},
        {"index": 2, "label": "tabby, tabby cat", "confidence": 0.038},
        {"index": 3, "label": "tiger cat", "confidence": 0.014},
        {"index": 4, "label": "lynx, catamount", "confidence": 0.0033},
        {"index": 5, "label": "Siamese cat, Siamese", "confidence": 0.00068},
    ]
