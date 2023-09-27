from diagrams import Cluster
from diagrams import Diagram
from diagrams.gcp.compute import Run
from diagrams.gcp.database import Datastore
from diagrams.generic.device import Tablet

filename: str = __file__.removesuffix(".py")

with Diagram(filename=filename, show=False):
    client = Tablet("client")

    with Cluster("GCP"):
        api = Run("Cloud Run - API")
        db = Datastore("Datastore")
        api >> db

    client >> api
