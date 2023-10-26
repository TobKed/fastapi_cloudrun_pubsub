from diagrams import Cluster
from diagrams import Diagram
from diagrams.gcp.analytics import PubSub
from diagrams.gcp.compute import Run
from diagrams.gcp.database import Datastore
from diagrams.gcp.network import LoadBalancing
from diagrams.generic.device import Tablet

filename: str = __file__.removesuffix(".py")

with Diagram(filename=filename, show=False):
    client = Tablet("client")

    with Cluster("GCP"):
        LB = LoadBalancing("Load Balancer")

        with Cluster("Region 1"):
            api = Run("Cloud Run\nLight API")
            db = Datastore("Datastore")
            worker = Run("Cloud Run\nHeavy Worker")
            pubsub = PubSub("PubSub")
            api >> db
            api >> pubsub
            pubsub >> worker
            db << worker

        with Cluster("Region 2"):
            api_2 = Run("Cloud Run\nLight API")
            db_2 = Datastore("Datastore")
            worker_2 = Run("Cloud Run\nHeavy Worker")
            pubsub_2 = PubSub("PubSub")
            api_2 >> db_2
            api_2 >> pubsub_2
            pubsub_2 >> worker_2
            db_2 << worker_2

        LB >> api
        LB >> api_2

    client >> LB
