from diagrams import Cluster
from diagrams import Diagram
from diagrams.gcp.analytics import PubSub
from diagrams.gcp.compute import Run
from diagrams.gcp.database import Datastore
from diagrams.generic.device import Tablet

filename: str = __file__.removesuffix(".py")

with Diagram(filename=filename, show=False):
    client = Tablet("client")

    with Cluster("GCP"):
        api = Run("Cloud Run\nLight API")
        db = Datastore("Datastore")
        worker = Run("Cloud Run\n Heavy Worker")
        pubsub = PubSub("PubSub")
        api >> db
        api >> pubsub
        pubsub >> worker
        db << worker

    client >> api
