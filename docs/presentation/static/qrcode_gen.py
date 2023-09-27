from pathlib import Path

import qrcode

script_dir = Path(__file__).resolve().parent
file_path = script_dir / "qrcode.png"

data = "https://github.com/TobKed/fastapi_cloudrun_pubsub"
img = qrcode.make(data)
img.save(file_path)
