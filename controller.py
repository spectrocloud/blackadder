import logging
import random
import time

import lorem
import munch
import pykube
import requests


from pykube import Pod, Deployment, ConfigMap

logger = logging.getLogger("chaos-controller")


def list_objects(self, k8s_obj, exclude_namespaces):

    exclude_namespaces = ",".join("metadata.namespace!=" + ns
                                  for ns in exclude_namespaces)
    return list(
            k8s_obj.objects(api).filter(namespace=pykube.all,
                                        field_selector=exclude_namespaces

                                        ))


config = pykube.KubeConfig.from_env()


pykube.HTTPClient.list_objects = list_objects


api = pykube.HTTPClient(config)

ChaosAgent = pykube.object_factory(api, "blackadder.io/v1beta1", "ChaosAgent")

# retrieves our agent configuraton from the kube-api-server
agent = list(ChaosAgent.objects(api, namespace=pykube.all))[0]

agent.config = munch.munchify(agent.obj["spec"])

exclude_namespaces = agent.config.excludedNamespaces


def randomly_kill_pods(pods, tolerance, eagerness):
    if len(pods) < tolerance:
        return

    for p in pods:
        if random.randint(0, 100) < eagerness:
            p.delete()
            logger.info(f"Deleted {p.namespace}/{p.name}")


def randomly_scale_deployments(deployments, eagerness):
    for d in deployments:
        if random.randint(0, 100) < eagerness:
            while True:
                try:
                    if d.replicas < 128:
                        d.replicas = min(d.replicas * 2, 128)
                    d.update()
                    logger.info(f"scaled {d.namespace}/{d.name} to {d.replicas}")
                    break
                except (requests.exceptions.HTTPError, pykube.exceptions.HTTPError):
                    logger.info(f"error scaling {d.namespace}/{d.name} to {d.replicas}")
                    d.reload()
                    continue


def randomly_write_configmaps(configmaps, eagerness):
    for cm in configmaps:
        logger.info(f"Checking {cm.namespace}/{cm.name}")
        if cm.obj.get("immutable"):
            continue

        if random.randint(0, 100) < eagerness:
            for k, v in cm.obj["data"].items():
                cm.obj["data"][k] = lorem.paragraph()

            logger.info(f"Lorem Impsum in {cm.namespace}/{cm.name}")


while True:
    pods = api.list_objects(Pod, exclude_namespaces)
    deployments = api.list_objects(Deployment, exclude_namespaces)
    configmaps = api.list_objects(ConfigMap, exclude_namespaces)

    if agent.config.tantrumMode:
        randomly_kill_pods(pods,
                           agent.config.podTolerance,
                           agent.config.eagerness)

    if agent.config.cancerMode:
        randomly_scale_deployments(deployments,
                                   agent.config.eagerness)

    if agent.config.ipsumMode:
        randomly_write_configmaps(configmaps,
                                  agent.config.eagerness)

    time.sleep(agent.config.pauseDuration)
