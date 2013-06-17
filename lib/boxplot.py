#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from numbers import Number


def percentile(a, p):
    n = len(a)
    i = int(n * p)
    if abs((n * p) - i) < 0.000001:
        q = (a[i] + a[i - 1]) / 2.
    else:
        q = a[i]
    return q


class Dataset(object):
    def __init__(self, name, data):
        assert all((isinstance(d, Number) for d in data)), "data must be numbers"
        self.name = name
        self.minimum = min(data)
        self.q1 = percentile(data, 0.25)
        self.q2 = percentile(data, 0.5)
        self.q3 = percentile(data, 0.75)
        self.maximum = max(data)

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


# list_of_tuples = [('name', []),...]
def render(list_of_tuples, width=72, label_width=10, box_weight=1, with_scale=True):
    datasets = []
    for tup in list_of_tuples:
        if tup[0]:
            # if series name is provided, use it
            datasets.append(Dataset(tup[0], tup[1]))
        else:
            # otherwise generate a name
            datasets.append(Dataset('series-%s' % (list_of_tuples.index(tup) + 1), tup[1]))

    gamma = 2 * max(0, box_weight or 1)
    adj_width = width - label_width - 2

    smallest_q1 = min(map(lambda d: d.q1, datasets))
    biggest_q3 = max(map(lambda d: d.q3, datasets))

    span = (biggest_q3 - smallest_q1) or 1
    factor = ((adj_width * gamma) / (2 + gamma)) / span

    origin = int(factor * (smallest_q1 - (span / gamma)))
    edge = int(factor * (biggest_q3 + (span / gamma)))

    output = ""
    if with_scale:
        output += (" " * label_width)
        output += "|%-*g%*g|" % ((adj_width / 2), (origin / factor), (adj_width / 2), (edge / factor))

    for dataset in datasets:
        dataset.scale(factor)
        output += "\n" + _render_one(dataset, origin, edge, adj_width, label_width)
    return output


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

if __name__ == "__main__":

    print render([
        ("test data", [-2.5, -1, 0, 1, 2.5]),
        ("", [-1, 0, 1, 2, 3.5]),
        ("", [0, 1.5, 2, 2.5, 5.5]),
    ])
