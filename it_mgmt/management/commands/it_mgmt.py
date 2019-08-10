"""
Django management interface for running CLI programs for an app.

Create a cli module in your app.

Create python scripts in your cli module.
These scripts require:

DJANGO_COMMAND = 'main'   # enable this as a CLI command

And they *can* have:
# Metadata about this subcommand, for integration.
OPTION_LIST = (
     make_option('--year',
         dest='year',
         help='Specify a year to load '),
     make_option('--term',
         dest='term',
         help='Specify a term to load (fall, winter, or summer)'),
     )
ARGS_USAGE = '[--year YYYY --term TTTT]'
HELP_TEXT = 'Populate course information from aurora/banner'

The entry point will be your script's 'main' function (in this case).

If OPTION_LIST is defined in your script, you will need:
def main(options, args):
    '''options is a dict(), args is a list()'''

Otherwise, you need:
def main(args):
    '''args is a flag list of unprocessed options'''
"""
###############################################################
from __future__ import print_function, unicode_literals

import codecs
import locale
import os
import sys
from argparse import RawDescriptionHelpFormatter
from importlib import import_module

from django.core.management.base import (
    BaseCommand,
    CommandError,
    handle_default_options,
)
from django.utils import six

################################################################

# Unicode piping:
if six.PY2:
    sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
if six.PY3:
    sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout.detach())

###############################################################

path = __file__
for i in range(4):
    path, app_name = os.path.split(path)

###############################################################


def is_valid_cli_command(app_name, command_name):
    """
    Validate the given command in the given namespace.
    If valid, this function returns the entrypoint for the command.
    If invalid, returns None
    """
    mod_name = app_name + ".cli." + command_name
    mod = import_module(mod_name)
    command = getattr(mod, "DJANGO_COMMAND", None)
    if not command:
        return None
    main = getattr(mod, command, None)
    if main is None:
        return None  # no main
    return main


###############################################################


def get_optional_cli_info(app_name, command_name):
    """
    return option_list, args_usage, help_text for the given subcommand.
    """
    mod_name = app_name + ".cli." + command_name
    mod = import_module(mod_name)
    use_argparse = getattr(mod, "USE_ARGPARSE", False)
    option_list = getattr(mod, "OPTION_LIST", None)
    args_usage = getattr(mod, "ARGS_USAGE", None)
    help_text = getattr(mod, "HELP_TEXT", None)
    return use_argparse, option_list, args_usage, help_text


###############################################################


def discover_cli_scripts(path, name=None):
    """
    Recursively discover scripts.
    """
    if not os.path.exists(os.path.join(path, "__init__.py")):
        return []
    listdir = sorted(os.listdir(path))
    pyfiles = [
        os.path.splitext(f)[0]
        for f in listdir
        if f.endswith(".py") and f != "__init__.py"
    ]
    if name is None:
        name = ""
    else:
        name += "."
    # this CLI runner script has the same filename as the appname:
    appname = os.path.splitext(os.path.basename(__file__))[0]
    scripts = [name + s for s in pyfiles if is_valid_cli_command(appname, name + s)]
    listpath = [os.path.join(path, f) for f in listdir]
    sublist = [
        (subname, subpath)
        for subname, subpath in zip(listdir, listpath)
        if os.path.isdir(subpath)
    ]
    for subname, subpath in sublist:
        # recursion!
        scripts += discover_cli_scripts(subpath, name + subname)
    return scripts


###############################################################


def print_available_commands(app_name):
    """
    Prints a list of the available subcommands.
    """
    mod_name = app_name + ".cli"
    try:
        mod = import_module(mod_name)
    except:
        print("There was an error loading the CLI script module.", file=sys.stderr)
        return
    path = os.path.dirname(mod.__file__)
    scripts = discover_cli_scripts(path)
    print(Command.help)
    print("")
    print("Available CLI scripts are:")
    print("")
    print("\t" + "\n\t".join(scripts))
    print("")


###############################################################


class Command(BaseCommand):
    """
    This is a polymorphic-ish class, which can update metadata
    based on the subcommand called.
    """

    help = "Run CLI programs for %s app." % app_name
    use_argparse = True

    def create_parser(self, *args, **kwargs):
        parser = super(Command, self).create_parser(*args, **kwargs)
        parser.formatter_class = RawDescriptionHelpFormatter
        return parser

    def run_from_argv(self, full_args):
        """
        Do the command!
        """
        args = full_args[2:]  # first two look like ['manage.py', app_name,]

        if not args:
            # show available subcommands
            print_available_commands(app_name)
            return

        if args[0] in ["--help", "-h", "-?"]:
            print_available_commands(app_name)
            return

        subcommand = args[0]
        # check that this is a valid subcommand
        cli_main = is_valid_cli_command(app_name, subcommand)
        if cli_main is None:
            print("Error: not a valid subcommand", file=sys.stderr)
            print_available_commands(app_name)
            return

        self.use_argparse, option_list, args_usage, help_text = get_optional_cli_info(
            app_name, subcommand
        )
        if args_usage is not None:
            setattr(Command, "args", args_usage)
        if help_text is not None:
            setattr(Command, "help", help_text)
        if getattr(BaseCommand, "option_list", None) is None:
            self.use_argparse = True

        if option_list is not None:
            option_list = list(getattr(BaseCommand, "option_list", [])) + list(
                option_list
            )
            setattr(Command, "option_list", option_list)
            # process options here.
            parser = self.create_parser(full_args[0], full_args[1] + " " + subcommand)
            if self.use_argparse:
                for a, k in option_list:
                    parser.add_argument(*a, **k)
                options = parser.parse_args(args[1:])
                cmd_options = vars(options)
                # Move positional args out of options to mimic legacy argparse
                args = cmd_options.pop("args", ())
            else:
                options, args = parser.parse_args(args[1:])
                cmd_options = vars(options)
            handle_default_options(options)
            return cli_main(cmd_options, args)
        else:
            # dispatch to subcommand
            cli_args = args[1:]
            # TODO: find a way to strip out --settings= and --pythonpath=
            return cli_main(cli_args)


###############################################################
