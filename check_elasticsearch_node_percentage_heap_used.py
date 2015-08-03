#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2013:
#     Sébastien Pasche, sebastien.pasche@leshop.ch
#     Raphael Anthamatten  raphael.anthamatten@leshop.ch
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

author = "Sebastien Pasche"
maintainer = "Sebastien Pasche"
version = "0.0.1"

import optparse
import sys
import os
import traceback

from pprint import pprint
from statistics import mean


#Ok try to load our directory to load the plugin utils.
my_dir = os.path.dirname(__file__)
sys.path.insert(0, my_dir)

try:
    from elasticsearch_checks import \
        ElasticSearchCheckHelpers, ElasticSearchStatsHelpers, \
        ElasticSearchStatsEvalHelpers, OutputFormatHelpers
except ImportError:
    print "ERROR : this plugin needs the local elasticsearch_checks lib. Please install it"
    sys.exit(2)


#DEFAULT LIMITS
#--------------
DEFAULT_WARNING = 80
DEFAULT_CRITICAL = 90


# OPT parsing
# -----------
parser = optparse.OptionParser(
    "%prog [options]", version="%prog " + version)

#add default parser
parser = ElasticSearchCheckHelpers.add_default_parser_options(parser)

parser.add_option('--node-id',
                  dest="node_id",default=None,
                  help='get this specific node stats')
parser.add_option('-w', '--warning',
                  dest="warning", type="int",default=None,
                  help='Warning value for heap percentage usage. Default : 80')
parser.add_option('-c', '--critical',
                  dest="critical", type="int",default=None,
                  help='Critical value for for heap percentage usage. Default : 90')

if __name__ == '__main__':
    # Ok first job : parse args
    opts, args = parser.parse_args()
    if args:
        parser.error("Does not accept any argument.")

    # connection parameters
    port = opts.port
    hostname = opts.hostname or ''
    scheme = opts.scheme
    debug = opts.debug

    if opts.node_id is None:
        parser.error("You must speciffy a node id.")
    node_id = opts.node_id

    # Try to get numeic warning/critical values
    s_warning = opts.warning or DEFAULT_WARNING
    s_critical = opts.critical or DEFAULT_CRITICAL


    try:
        #get stats
        stats = ElasticSearchStatsHelpers.node_statistics(
            scheme=scheme,
            hostname=hostname,
            port=port,
            node_id=node_id,
            debug=debug
        )

        if debug:
            pprint(stats)

        #Get stats
        percentage_heap_used = ElasticSearchStatsEvalHelpers.get_heap_used_percent(stats)
        if debug:
            print("Percentage heap used")
            print("--------------")
            print(percentage_heap_used)
            print("--------------")

        #check logic
        status = 'OK'
        comment='within the limits'
        heap_used_comment_tempalte="Heap usage is {c} {v}%"
        heap_used_message_template="{s}: {m}"

        if percentage_heap_used >= s_warning:
            status = 'Warning'
            comment='too high'
        if percentage_heap_used >= s_critical:
            status = 'Critical'
            comment='too hgih'

        #format output
        heap_usage_comment=heap_used_comment_tempalte.format(
            c=comment,
            v=percentage_heap_used
        )


        #Format perf data string
        con_perf_data_string = OutputFormatHelpers.perf_data_string(
            label='heap_used',
            value=percentage_heap_used,
            warn=s_warning,
            crit=s_critical,
            min=0,
            max=100,
            UOM='%'
        )


        #format OUtput
        output = OutputFormatHelpers.check_output_string(
            status,
            heap_usage_comment,
            [con_perf_data_string]
        )

        print(output)

    except Exception as e:
        if debug:
            print(e)
            the_type, value, tb = sys.exc_info()
            traceback.print_tb(tb)
        print("Error: {m}".format(m=e))
        sys.exit(2)

    finally:
        if status == "Critical":
            sys.exit(2)
        if status == "Warning":
            sys.exit(1)
        sys.exit(0)
