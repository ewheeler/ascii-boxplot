#!/usr/bin/env python
#
# Copyright 2013 Evan Wheeler
#
# based on bitly's data_hacks https://github.com/bitly/data_hacks
# and David Golden's https://github.com/dagolden/text-boxplot
#
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
Generate an ascii box-and-whiskers chart for input data

"""
import sys
import itertools
from optparse import OptionParser


def percentile(a, p):
    n = len(a)
    i = int(n * p)
    if abs((n * p) - i) < 0.000001:
        q = (a[i] + a[i - 1]) / 2.
    else:
        q = a[i]
    return q

def str_to_number(s):
    try:
        return int(s)
    except ValueError:
        return float(s)

class Dataset(object):
    def __init__(self, name, data):
        self.data = [str_to_number(d) for d in data]
        self.name = name
        self.minimum = min(self.data)
        self.q1 = percentile(self.data, 0.25)
        self.q2 = percentile(self.data, 0.5)
        self.q3 = percentile(self.data, 0.75)
        self.maximum = max(self.data)

    def scale(self, factor):
        self.minimum = int(factor * self.minimum)
        self.q1 = int(factor * self.q1)
        self.q2 = int(factor * self.q2)
        self.q3 = int(factor * self.q3)
        self.maximum = int(factor * self.maximum)

    def __repr__(self):
        return "<Dataset %(name)s: min=%(minimum)s, q1=%(q1)s, q2=%(q2)s, q3=%(q3)s, max=%(maximum)s>" %\
               {"name": self.name, "minimum": self.minimum, "q1": self.q1,
               "q2": self.q2, "q3": self.q3, "maximum": self.maximum}


def _render_one(data=None, origin=None, edge=None, adj_width=None, label_width=None):
    out = ""
    out += (" " * int(max((data.minimum - origin), 0)))
    out += ("-" * int(data.q1 - max(data.minimum, origin)))
    out += ("=" * int(data.q2 - data.q1))
    out += "0"
    out += ("=" * int(data.q3 - data.q2))
    out += ("-" * int(min(data.maximum, edge) - data.q3))
    out += (" " * int(max((edge - data.maximum), 0)))

    # cast to list so we can assign by index
    out = list(out[0:adj_width])
    # add arrows to indicate clipped whiskers
    if out[0] == "-":
        out[0] = "<"
    if out[-1] == "-":
        out += ">"

    out = "".join(out).rstrip()
    name = data.name[0:label_width]
    return "%*s %s" % (label_width, name, out)


def load_stream(input_stream):
    for line in input_stream:
        clean_line = line.strip()
        if not clean_line:
            # skip empty lines (ie: newlines)
            continue
        if clean_line[0] in ['"', "'"]:
            clean_line = clean_line.strip('"').strip("'")
        if clean_line:
            yield clean_line


def run(input_stream, options):
    datasets = []
    counter = itertools.count(1)
    for row in input_stream:
        datasets.append(Dataset('series-%s' % counter.next(), row.split(',')))

    if not datasets:
        print "Error: no data"
        sys.exit(1)


    gamma = 2 * max(0, options.box_weight or 1)
    adj_width = options.width - options.label_width - 2

    smallest_q1 = min(map(lambda d: d.q1, datasets))
    biggest_q3 = max(map(lambda d: d.q3, datasets))

    span = (biggest_q3 - smallest_q1) or 1
    factor = ((adj_width * gamma) / (2 + gamma)) / span

    origin = int(factor * (smallest_q1 - (span / gamma)))
    edge = int(factor * (biggest_q3 + (span / gamma)))

    output = ""
    if options.with_scale:
        output += (" " * options.label_width)
        output += "|%-*g%*g|" % ((adj_width / 2), (origin / factor), (adj_width / 2), (edge / factor))

    for dataset in datasets:
        dataset.scale(factor)
        output += "\n" + _render_one(dataset, origin, edge, adj_width, options.label_width)
    print output


if __name__ == "__main__":
    parser = OptionParser()
    parser.usage = "cat data | %prog [options]"

    parser.add_option("-w", "--width", dest="width", default=72, action="store_true",
                        help="output width")
    parser.add_option("-l", "--label-width", dest="label_width", default=10, action="store_true",
                        help="width of series label")
    parser.add_option("-b", "--box-weight", dest="box_weight", default=1, action="store_true",
                        help="output scale")
    parser.add_option("-s", "--with-scale", dest="with_scale", default=True, action="store_true",
                        help="show min and max values")

    (options, args) = parser.parse_args()

    if sys.stdin.isatty():
        parser.print_usage()
        print "for more help use --help"
        sys.exit(1)
    run(load_stream(sys.stdin), options)
