from diagrams import Cluster
from diagrams import Diagram
from diagrams.gcp.analytics import PubSub
from diagrams.gcp.compute import Run
from diagrams.gcp.database import Datastore
from diagrams.gcp.network import LoadBalancing
from diagrams.gcp.storage import GCS
from diagrams.generic.device import Tablet

filename: str = __file__.removesuffix(".py")


with Diagram(filename=filename, show=False):
    client = Tablet("client")

    with Cluster("GCP"):
        LB = LoadBalancing("Load Balancer")

        api = Run("API")
        worker = Run("Worker")
        pubsub = PubSub("PubSub")
        storage = GCS("Storage")
        db = Datastore("Datastore")

        LB >> api

        api >> storage
        api >> pubsub
        api >> db

        storage << worker
        pubsub >> worker
        db << worker

    client >> LB
