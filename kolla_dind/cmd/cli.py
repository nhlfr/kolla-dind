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

import sys

from oslo_config import cfg
from oslo_log import log as logging

from kolla_dind import dind


CONF = cfg.CONF


def add_action_parsers(subparsers):
    subparsers.add_parser('start')
    subparsers.add_parser('stop')
    subparsers.add_parser('remove')


opts = [
    cfg.BoolOpt('multinode'),
    cfg.IntOpt('mesos-master-nodes',
               default=1),
    cfg.IntOpt('controller-nodes',
               default=1),
    cfg.IntOpt('compute-nodes',
               default=1),
    cfg.IntOpt('network-nodes',
               default=1),
    cfg.IntOpt('storage-nodes',
               default=1),
    cfg.SubCommandOpt('action',
                      handler=add_action_parsers)
]
CONF.register_cli_opts(opts)
CONF.register_opts(opts)

logging.register_options(CONF)


def main():
    CONF(sys.argv[1:])
    logging.setup(CONF, 'kolla-dind')
    function = getattr(dind, CONF.action.name)
    function()


if __name__ == '__main__':
    main()
