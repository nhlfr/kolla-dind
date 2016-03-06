# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import operator

from docker import errors as docker_errors
from oslo_config import cfg
from oslo_log import log as logging
import six

from kolla_dind import docker_client


CONF = cfg.CONF

LOG = logging.getLogger(__name__)

DIND_PREFIX = 'kolla_dind_dev'
DIND_MAP = {
    'mesos_master_nodes': '%s_mesos_master_%d',
    'controller_nodes': '%s_controller_%d',
    'compute_nodes': '%s_compute_%d',
    'network_nodes': '%s_network_%d',
    'storage_nodes': '%s_storage_%d'
}


@docker_client.docker_client
def start(dc):
    if CONF.multinode:
        for opt, pattern in DIND_MAP.items():
            number_of_instances = getattr(CONF, opt)
            for i in range(number_of_instances):
                name = pattern % (DIND_PREFIX, i)
                try:
                    dc.create_container(
                        image='kollaglue/centos-binary-dind:2.0.0',
                        name=name)
                except docker_errors.APIError:
                    pass
                LOG.info("Starting container %s", name)
                dc.start(name)
    else:
        name = '%s_aio' % DIND_PREFIX
        try:
            dc.create_container(image='kollaglue/centos-binary-dind:2.0.0',
                                name=name)
        except docker_errors.APIError:
            pass
        LOG.info("Starting container %s", name)
        dc.start(name)


def get_dind_containers(dc):
    containers = six.moves.filter(
        lambda container: container['Names'][0].startswith('/' + DIND_PREFIX),
        dc.containers(all=True))
    ids = six.moves.map(operator.itemgetter('Id'), containers)
    return ids


@docker_client.docker_client
def stop(dc):
    container_ids = get_dind_containers(dc)
    for container_id in container_ids:
        LOG.info("Stopping container %s", container_id)
        dc.stop(container_id)


@docker_client.docker_client
def remove(dc):
    container_ids = get_dind_containers(dc)
    for container_id in container_ids:
        LOG.info("Removing container %s", container_id)
        dc.remove_container(container_id, force=True)
