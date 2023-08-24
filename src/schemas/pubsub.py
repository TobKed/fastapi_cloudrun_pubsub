from base64 import b64decode

from pydantic import Base64Str
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Extra


class GooglePubSubMessage(BaseModel):
    data: Base64Str
    messageId: str  # noqa: N815

    model_config = ConfigDict(extra=Extra.ignore)

    def decode(self) -> str:
        return b64decode(self.data).decode("utf8")


class GooglePubSubPushRequest(BaseModel):
    message: GooglePubSubMessage

    model_config = ConfigDict(extra=Extra.ignore)
