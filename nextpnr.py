# Copyright (C) 2024 Hansem Ro <hansemro@outlook.com>
# Copyright (C) 2018-2020 Claire Xenia Wolf <claire@yosyshq.com>
# Copyright (C) 2018-2020 gatecat <gatecat@ds0.me>
# Copyright (C) 2018-2020 Dan Gisselquist <dan@symbioticeda.com>
# Copyright (C) 2018-2020 Serge Bazanski <q3k@q3k.org>
# Copyright (C) 2018-2020 Miodrag Milanovic <micko@yosyshq.com>
# Copyright (C) 2018-2020 Eddie Hung <eddieh@ece.ubc.ca>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from enum import Enum
import re

class NextpnrNet:
    def __init__(self, name):
        self.name = name;
        self.params = dict() # parameter name --> parameter value as string
        self.attrs = dict() # attribute name --> attribute value as string
        self.driver = None  # NextpnrCellPort
        # Below added as a hack to allow IOB PAD cell to be registered as a driver
        self.drivers = list() # list of NextpnrCellPort
        self.users = list() # list of NextpnrCellPort
        self.rwNet = None;

class PortDirection(Enum):
    PORT_IN = 0
    PORT_OUT = 1
    PORT_INOUT = 2

    @staticmethod
    def parsePortDir(s:str):
        if s == "output":
            return PortDirection.PORT_OUT;
        elif s == "inout":
            return PortDirection.PORT_INOUT;
        return PortDirection.PORT_IN

class NextpnrCell:
    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.ports = dict() # port name --> NextpnrCellPort
        self.params = dict() # parameter name --> parameter value as string
        self.attrs = dict() # attribute name --> attribute value as string
        self.rwCell = None

class NextpnrCellPort:
    def __init__(self, cell:NextpnrCell, name:str, pin_dir:PortDirection):
        self.cell = cell
        self.name = name
        self.type = pin_dir
        self.net = None

class NextpnrDesign:
    def __init__(self):
        self.nets = dict() # net index --> NextpnrNet
        self.cells = dict() # cell name -> NextpnrCell
        self.rwd = None

    @staticmethod
    def parseParam(param_value:str):
        # assumes binary or string formats
        # TODO: parse other formats?
        binary_pattern = re.compile(r'^[01xz]+$', re.IGNORECASE)
        binary_match = re.match(binary_pattern, param_value)
        if binary_match is not None:
            param_value = re.sub(r'[xz]', '0', param_value)
            num = int(param_value, 2)
            size = max(num.bit_length(), 1)
            return f"{size}'h{hex(num)[2:]}"
        return param_value

    def load(self, json_data):
        top = json_data["modules"]["top"]
        for net_name, net_props in top["netnames"].items():
            index = int(net_props["bits"][0])
            net = NextpnrNet(net_name)
            for attr, attr_value in net_props["attributes"].items():
                net.attrs[attr] = attr_value
            self.nets[index] = net
        for cell_name, cell_props in top["cells"].items():
            cell = NextpnrCell(cell_name, cell_props["type"])
            for port_name, port_dir in cell_props["port_directions"].items():
                cell.ports[port_name] = NextpnrCellPort(cell, port_name, PortDirection.parsePortDir(port_dir))
            for port_name, conn_arr in cell_props["connections"].items():
                port = cell.ports[port_name]
                if len(conn_arr) > 0:
                    # When does size become greater than 1?
                    assert len(conn_arr) <= 1
                    port.net = self.nets[conn_arr[0]]
                    if port.type == PortDirection.PORT_OUT:
                        port.net.driver = port
                        port.net.drivers += [port]
                    elif port.type == PortDirection.PORT_IN:
                        port.net.users += [port]
                    else: # PortDirection.PORT_INOUT
                        # IOB PAD cells are inout, so we need to declare as driver and user
                        # to allow IBUF/OBUF cells find its associated PAD cell
                        port.net.drivers += [port]
                        port.net.users += [port]
            for attr, attr_value in cell_props["attributes"].items():
                cell.attrs[attr] = str(attr_value)
            for param, param_value in cell_props["parameters"].items():
                cell.params[param] = self.parseParam(param_value)
            self.cells[cell_name] = cell

import json
from argparse import ArgumentParser, FileType

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('nextpnr_json', type=FileType('r'))

    args = parser.parse_args()

    ndes = NextpnrDesign()
    ndes.load(json.load(args.nextpnr_json))
