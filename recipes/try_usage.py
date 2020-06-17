"""
Prints stats on what percentage of try pushes are being scheduled with various
different mechanisms over the last week. The date range can be modified the
same as the `hours_on_try` recipe.

.. code-block:: bash

    adr try_usage

`View Results <https://mozilla.github.io/active-data-recipes/#try-usage>`__
"""
from __future__ import absolute_import, print_function

from collections import OrderedDict, defaultdict
from itertools import chain

from adr.query import run_query


def subcommand(name):
    return {
        name: {
            'test': 'Pushed via `mach try {}`'.format(name),
            'method': 'mach try {}'.format(name),
        }
    }


def run(args):

    data = run_query('try_commit_messages', args)['data']

    # Order is important as the search stops after the first successful test.
    d = OrderedDict()
    d.update(subcommand('syntax'))
    d['vanilla'] = {
        'test': 'try:',
        'method': 'vanilla try syntax',
    }
    d.update(subcommand('again'))
    d.update(subcommand('auto'))
    d.update(subcommand('chooser'))
    d.update(subcommand('coverage'))
    d.update(subcommand('empty'))
    d.update(subcommand('fuzzy'))
    d.update(subcommand('perftest'))
    d.update(subcommand('release'))
    d.update(subcommand('scriptworker'))
    d['other'] = {
        'test': '',
        'method': 'other',
    }
    d['total'] = {
        'test': None,
        'method': 'total',
    }

    data = zip(data['user'], data['message'])

    count = defaultdict(int)
    users = defaultdict(lambda: defaultdict(int))

    for user, message in data:
        for k, v in d.items():
            if v['test'] in message:
                count[k] += 1
                users[k][user] += 1
                break

    selector = "syntax"
    return [["users", selector, "total"]] + sorted([
        [user, users[selector][user],
         sum((users[k][user] for k in users)),
         users[selector][user]/sum((users[k][user] for k in users)),
         {k: users[k][user] for k in users if users[k][user] > 0 and k != selector}
         ]
        for user in users[selector]
        # if users[selector][user]/sum((users[k][user] for k in users)) > 0.5
    ], key=lambda r: (round(r[1], -1), r[3]))

    count['total'] = sum(count.values())
    users['total'] = set(chain(*users.values()))

    def fmt(key):
        percent = round(float(count[key]) / count['total'] * 100, 1)
        return [d[key]['method'], count[key], percent, len(users[key]), round(float(count[key]) / len(users[key]), 2)]  # noqa

    data = [['Method', 'Pushes', 'Percent', 'Users', 'Push / User']]
    for k, v in sorted(count.items(), key=lambda t: t[1], reverse=True):
        data.append(fmt(k))
    return data
