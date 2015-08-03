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



# OPT parsing
# -----------
parser = optparse.OptionParser(
    "%prog [options]", version="%prog " + version)

#add default parser
parser = ElasticSearchCheckHelpers.add_default_parser_options(parser)


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


    try:
        #get stats
        stats = ElasticSearchStatsHelpers.cluster_statistics(
            scheme=scheme,
            hostname=hostname,
            port=port,
            debug=debug
        )

        if debug:
            print(stats)

        #Get stats
        cluster_status = ElasticSearchStatsEvalHelpers.get_cluster_status(stats)
        if debug:
            print("cluster status")
            print("--------------")
            print(cluster_status)
            print("--------------")

        
        #check logic
        status = 'OK'
        comment='green, super green'
        cluster_status_template="cluster status is {c} "

        if cluster_status != 'green':
            status = 'Critical'
            comment = 'not green'

        if debug:
            print(status)

        cluster_status_comment=cluster_status_template.format(
        c=comment
        )

        #format OUtput
        perfdata = None
        output = OutputFormatHelpers.check_output_string(
            status,
            cluster_status_comment,
            [perfdata]
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
        sys.exit(0)
