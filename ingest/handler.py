from mangum import Mangum
from ingest.app import app

# AWS Lambda entry point
handler = Mangum(app)
