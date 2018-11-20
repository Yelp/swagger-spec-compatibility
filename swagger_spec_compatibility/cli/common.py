# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import typing  # noqa: F401
from argparse import ArgumentTypeError
from os.path import abspath
from os.path import exists
from os.path import expanduser
from os.path import expandvars

import typing_extensions
from six.moves.urllib.parse import urljoin
from six.moves.urllib.parse import urlsplit
from six.moves.urllib.request import pathname2url
from six.moves.urllib.request import url2pathname

from swagger_spec_compatibility.rules.common import BaseRule  # noqa: F401
from swagger_spec_compatibility.rules.common import RuleRegistry  # noqa: F401


class CLIProtocol(typing_extensions.Protocol):
    command = None  # type: typing.Text
    func = None  # type: typing.Callable[['CLIProtocol'], int]


class CLIRulesProtocol(typing_extensions.Protocol):
    rules = None  # type: typing.Iterable[typing.Text]


def uri(param):
    # type: (str) -> str
    if urlsplit(param).scheme:
        return param

    path = expanduser(expandvars(url2pathname(param)))
    if exists(path):
        return urljoin('file:', pathname2url(abspath(path)))

    raise ArgumentTypeError('`{param}` is not an existing file and either a valid URI'.format(param=param))


def cli_rules():
    # type: () -> typing.List[typing.Text]
    return list(RuleRegistry.rule_names())


def rules(cli_args):
    # type: (CLIRulesProtocol) -> typing.Set[typing.Type[BaseRule]]
    return {RuleRegistry.rule(rule_name) for rule_name in cli_args.rules}
