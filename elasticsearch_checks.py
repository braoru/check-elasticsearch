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

import collections
import time

from requests import Request, Session
from pprint import pprint

class ElasticSearchCheckHelpers(object):

    @classmethod
    def add_default_parser_options(
            cls,
            parser
    ):
        parser.add_option('-H', '--hostname',
                          dest="hostname",
                          help='Hostname to connect to')
        parser.add_option('-p', '--port',
                          dest="port", type="int", default=9200,
                          help='ElasticSearch HTTP port to connect to. Default : HTTPS - 9200')
        parser.add_option('-s', '--http-scheme',
                          dest="scheme", default="http",
                          help='ElasticSearch HTTP scheme to connect to. Default : http://')
        parser.add_option('--debug',
                          dest="debug", default=False, action="store_true",
                          help='Enable debug')

        return parser

class ElasticSearchStatsHelpers(object):
    """
        Basic elasticsearch stats query helpers
    """

    #required URL
    URI_TEMPLATE = "{scheme}://{host}:{port}{url}"
    URL_NODE_STATS_TEMPLATE = "/_nodes/{node}/stats"
    URL_CLUSTER_STATS_TEMPLATE = "/_cluster/stats"

    @classmethod
    def _cluster_statistics_uri(
            cls,
            scheme='http',
            hostname='127.0.0.1',
            port=9200
    ):
        """
        Generate cluster stats uri from params
        :param scheme: HTTP scheme to use
        :type scheme: str
        :param hostname: Hostname where to execute the query
        :type hostname: str
        :param port: Port to connect to
        :type port : int
        :return: Complete query as a string
        """
        url = cls.URL_CLUSTER_STATS_TEMPLATE
        uri = cls.URI_TEMPLATE.format(
            scheme=scheme,
            host=hostname,
            port=port,
            url=url
        )
        return uri


    @classmethod
    def _node_statistics_uri(
            cls,
            scheme='http',
            hostname='127.0.0.1',
            port=9200,
            node_id='127.0.0.1'
    ):
        """
        Generate node stats uri from params
        :param scheme: HTTP scheme to use
        :type scheme: str
        :param hostname: Hostname where to execute the query
        :type hostname: str
        :param port: Port to connect to
        :type port : int
        :param node_id: target node id
        :type node_id : str
        :type port : int
        :return: Complete query as a string
        """
        url = cls.URL_NODE_STATS_TEMPLATE.format(node_id=node_id)
        uri = cls.URI_TEMPLATE.format(
            scheme=scheme,
            host=hostname,
            port=port,
            url=url
        )
        return uri


    @classmethod
    def cluster_statistics(
            cls,
            scheme='http',
            hostname='127.0.0.1',
            port=9200,
            debug=False
    ):
        """
        Get cluster stats from hostname
        :param scheme: HTTP scheme to use
        :type scheme: str
        :param hostname: Hostname where to execute the query
        :type hostname: str
        :param port: Port to connect to
        :type port : int
        :param debug: is debug enabled
        :type port : bool
        :return: JSON stats
        """
        uri = cls._cluster_statistics_uri(
            scheme=scheme,
            hostname=hostname,
            port=port
        )

        stats =  cls._http_query(
            uri=uri,
            debug=debug
        )

        if debug:
            print("Stats")
            print("-----")
            pprint(stats)
            print("-----")

        return stats

    @classmethod
    def node_statistics(
            cls,
            scheme='http',
            hostname='127.0.0.1',
            port=9200,
            node_id='127.0.0.1',
            debug=False
    ):
        """
        Get cluster stats from hostname for a given node_id
        :param scheme: HTTP scheme to use
        :type scheme: str
        :param hostname: Hostname where to execute the query
        :type hostname: str
        :param port: Port to connect to
        :type port : int
        :param debug: is debug enabled
        :type port : bool
        :param node_id: target node_id
        :type node_id: str
        :return:JSON stats
        """
        uri = cls._node_statistics_uri(
            scheme=scheme,
            hostname=hostname,
            port=port,
            node_id=node_id
        )

        stats =  cls._http_query(
            uri=uri,
            debug=debug
        )

        if debug:
            print("Stats")
            print("-----")
            pprint(stats)
            print("-----")

        return stats

    @classmethod
    def _http_query(
            cls,
            uri,
            debug=False
    ):
        """
        Execute the stats query then return the complete stats json object
        :param url: complete url to query
        :type url : str
        :return: json object
        """
        #ask for stats
        s = Session()
        req = Request(
            method='GET',
            url=uri,
        )
        prepared_request = req.prepare()

        if debug:
            print("uri")
            print("-------")
            pprint(uri)
            print("-------")

        response = s.send(prepared_request)

        #check for http error
        response.raise_for_status()

        if debug:
            print("response")
            print("---------")
            pprint(response)
            print("---------")

        #get the result back
        stats = response.json()



        return stats


    @classmethod
    def _delayed(
            cls,
            results,
            delay,
    ):
        """
        Just a delay
        :param results: result to forward
        :rype results: json object
        :param delay: time to wait in [s]
        :type delay: int
        :return: intput result
        """
        time.sleep(delay)
        return results


    @classmethod
    def sampled_node_statistics(
            cls,
            scheme='http',
            hostname='127.0.0.1',
            port=9200,
            node_id='127.0.0.1',
            sample_interval=1,
            nb_sample=5,
            debug=False
    ):
        """
        Query sampled node stats
        :param scheme: HTTP scheme to use
        :type scheme: str
        :param hostname: Hostname where to execute the query
        :type hostname: str
        :param port: Port to connect to
        :type port : int
        :param debug: is debug enabled
        :type port : bool
        :param node_id: target node_id
        :type node_id: str
        :param sample_interval: time in [s] between to probe
        :type sample_interval: int
        :param nb_sample: Number of sample to get
        :type nb_sample : int
        :return: JSON stats array
        """
        stats = [
            cls._delayed(
                results=cls.node_statistics(
                    scheme=scheme,
                    hostname=hostname,
                    port=port,
                    node_id=node_id,
                    debug=debug
                ),
                delay=sample_interval
            )
            for element in range(nb_sample)
        ]
        return stats

    @classmethod
    def sampled_cluster_statistics(
            cls,
            scheme='http',
            hostname='127.0.0.1',
            port=9200,
            sample_interval=1,
            nb_sample=5,
            debug=False
    ):
        """
        Query sampled cluster stats
        :param scheme: HTTP scheme to use
        :type scheme: str
        :param hostname: Hostname where to execute the query
        :type hostname: str
        :param port: Port to connect to
        :type port : int
        :param debug: is debug enabled
        :type port : bool
        :param sample_interval: time in [s] between to probe
        :type sample_interval: int
        :param nb_sample: Number of sample to get
        :type nb_sample : int
        :return: JSON stats array
        """
        stats = [
            cls._delayed(
                results=cls.cluster_statistics(
                    scheme=scheme,
                    hostname=hostname,
                    port=port,
                    debug=debug
                ),
                delay=sample_interval
            )
            for element in range(nb_sample)
        ]
        return stats


class ElasticSearchStatsEvalHelpers(object):

    @classmethod
    def get_nb_indexed_docs(
            cls,
            stats
    ):
        return stats['indices']['docs']['count']


    @classmethod
    def filter_nb_indexed_docs(
            cls,
            stats
    ):
        if not isinstance(stats, collections.Iterable):
            raise Exception('Provided input is not an Iterable')

        return [
            cls.get_nb_indexed_docs(element) for element in stats
        ]


class OutputFormatHelpers(object):

    @classmethod
    def perf_data_string(
            cls,
            label,
            value,
            warn,
            crit,
            UOM='',
            min='',
            max=''

    ):
        """
        Generate perf data string from perf data input
        http://docs.icinga.org/latest/en/perfdata.html#formatperfdata
        :param label: Name of the measured data
        :type label: str
        :param value: Value of the current measured data
        :param warn: Warning level
        :param crit: Critical level
        :param UOM: Unit of the value
        :param min: Minimal value
        :param max: maximal value
        :return: formated perf_data string
        """
        if UOM:
            perf_data_template = "'{label}'={value}[{UOM}];{warn};{crit};{min};{max};"
        else:
            perf_data_template = "'{label}'={value};{warn};{crit};{min};{max};"

        return perf_data_template.format(
            label=label,
            value=value,
            warn=warn,
            crit=crit,
            UOM=UOM,
            min=min,
            max=max
        )

    @classmethod
    def check_output_string(
            cls,
            state,
            message,
            perfdata
    ):
        """
        Generate check output string with perf data
        :param state: State of the check in  ['Critical', 'Warning', 'OK', 'Unknown']
        :type state: str
        :param message: Output message
        :type message: str
        :param perfdata: Array of perf data string
        :type perfdata: Array
        :return: check output formated string
        """
        if state not in  ['Critical', 'Warning', 'OK', 'Unknown']:
            raise Exception("bad check output state")

        if not message:
            message = '-'

        if perfdata is not None:
            if not hasattr(perfdata, '__iter__'):
                raise Exception("Submited perf data list is not iterable")

            perfdata_string = ''.join(' {s} '.format(s=data) for data in perfdata)
            output_template = "{s}: {m} |{d}"
        else:
            output_template = "{s}: {m} "
            perfdata_string = ''

        return output_template.format(
            s=state,
            m=message,
            d=perfdata_string
        )