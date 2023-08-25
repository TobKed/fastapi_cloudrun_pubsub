from base64 import b64decode
from typing import Any

from pydantic import Base64Str
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Extra


class GooglePubSubMessageBase(BaseModel):
    data: Base64Str
    messageId: str  # noqa: N815
    attributes: Any = None

    model_config = ConfigDict(extra=Extra.ignore)

    def decode(self) -> str:
        return b64decode(self.data).decode("utf8")


class GooglePubSubPushRequestBase(BaseModel):
    message: GooglePubSubMessageBase

    model_config = ConfigDict(extra=Extra.ignore)


class GooglePubSubMessageGenerateThumbnailsAttributes(BaseModel):
    image_hash: str
    image_url: str


class GooglePubSubMessageGenerateThumbnails(GooglePubSubMessageBase):
    attributes: GooglePubSubMessageGenerateThumbnailsAttributes


class GooglePubSubPushRequestGenerateThumbnails(GooglePubSubPushRequestBase):
    message: GooglePubSubMessageGenerateThumbnails
