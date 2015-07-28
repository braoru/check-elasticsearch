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
DEFAULT_WARNING = 5000
DEFAULT_CRITICAL = 2000


# OPT parsing
# -----------
parser = optparse.OptionParser(
    "%prog [options]", version="%prog " + version)

#add default parser
parser = ElasticSearchCheckHelpers.add_default_parser_options(parser)

parser.add_option('-w', '--warning',
                  dest="warning", type="int",default=None,
                  help='Warning value for number of indexed documents. Default : 5000')
parser.add_option('-c', '--critical',
                  dest="critical", type="int",default=None,
                  help='Critical value for number of unresponsive nodes. Default : 2000')
parser.add_option('--sample-interval',
                  dest="sample_interval", type="int", default=1,
                  help='Cpu sampling interval. In [s]. Default : 1 [s]')
parser.add_option('--max-sample',
                  dest="max_sample", type="int", default=5,
                  help='Cpu sampling number. In [number]. Default : 5')

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

    #sampling parameters
    sample_interval = opts.sample_interval
    max_sample = opts.max_sample

    # Try to get numeic warning/critical values
    s_warning = opts.warning or DEFAULT_WARNING
    s_critical = opts.critical or DEFAULT_CRITICAL


    try:
        #get stats
        stats = ElasticSearchStatsHelpers.sampled_cluster_statistics(
            scheme=scheme,
            hostname=hostname,
            port=port,
            sample_interval=sample_interval,
            nb_sample=max_sample,
            debug=debug
        )

        if debug:
            pprint(stats)

        #Get stats
        nb_docs_sample = ElasticSearchStatsEvalHelpers.filter_nb_indexed_docs(stats)
        if debug:
            print("NB docs Sample")
            print("--------------")
            print(nb_docs_sample)
            print("--------------")

        #Process data
        measurement_time = max_sample * sample_interval
        first = nb_docs_sample[0]
        last = nb_docs_sample[-1]
        nb_docs_diff = last - first

        #check logic
        status = 'OK'
        nb_docs_message = "{l} docs indexed in {t}s ".format(
            l=nb_docs_diff,
            t=measurement_time
        )
        if nb_docs_diff <= s_warning:
            status = 'Warning'
        if nb_docs_diff <= s_critical:
            status = 'Critical'


        #Format perf data string
        con_perf_data_string = OutputFormatHelpers.perf_data_string(
            label="{t}s_indexed_doc".format(t=measurement_time),
            value=nb_docs_diff,
            warn=s_warning,
            crit=s_critical
        )

        #format OUtput
        output = OutputFormatHelpers.check_output_string(
            status,
            nb_docs_message,
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
