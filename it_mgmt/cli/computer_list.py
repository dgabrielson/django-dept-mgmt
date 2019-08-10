#######################
from __future__ import print_function, unicode_literals

import codecs

# set unicode piping/output:
import sys
from optparse import make_option

from django.conf import settings
from django.utils.encoding import force_text
from django.utils.text import slugify

from ..models import Computer as Model
from ..models import NetworkInterface

#######################
"""
Generate a list of computer objects.
"""
#######################################################################

HELP_TEXT = __doc__.strip()
DJANGO_COMMAND = "main"
OPTION_LIST = (
    make_option(
        "-f",
        "--fields",
        dest="field_list",
        help='Specify a comma delimited list of fields to include, e.g., -f "get_primary_net_iface.mac_address,room"',
    ),
    make_option(
        "--ssh-config",
        action="store_true",
        default=False,
        help="Specify to output in ssh_config format (-f ignored)",
    ),
    make_option(
        "--nagios-host",
        action="store_true",
        default=False,
        help="Output in nagios host .cfg format (-f ignored); specifing a flags filter is a good idea",
    ),
    make_option(
        "--nagios-hostgroup",
        action="store_true",
        default=False,
        help="Output in nagios hostgroup .cfg format (-f ignored); specifing a flags filter is a good idea",
    ),
    make_option(
        "--flags",
        help="Specify a comma delimited list of computer flag slugs to filter the list",
    ),
    make_option(
        "--net",
        action="store_true",
        default=False,
        help="A short-hand for adding network related information to the field list.",
    ),
)
# ARGS_USAGE = '...'

#######################################################################

sys.stdout = codecs.getwriter("utf-8")(sys.stdout)

#######################################################################


def hostname_slugify(s):
    return ".".join([slugify(e) for e in s.split(".")])


#######################################################################


def _resolve_lookup(object, name):
    """
    This function originally found in django.templates.base.py, modified
    for arbitrary nested field lookups from the command line -F argument.
    
    Performs resolution of a real variable (i.e. not a literal) against the
    given context.

    As indicated by the method's name, this method is an implementation
    detail and shouldn't be called by external code. Use Variable.resolve()
    instead.
    """
    current = object
    try:  # catch-all for silent variable failures
        for bit in name.split("."):
            if current is None:
                return ""
            try:  # dictionary lookup
                current = current[bit]
            except (TypeError, AttributeError, KeyError, ValueError):
                try:  # attribute lookup
                    current = getattr(current, bit)
                except (TypeError, AttributeError):
                    try:  # list-index lookup
                        current = current[int(bit)]
                    except (
                        IndexError,  # list index out of range
                        ValueError,  # invalid literal for int()
                        KeyError,  # current is a dict without `int(bit)` key
                        TypeError,
                    ):  # unsubscriptable object
                        return "Failed lookup for [{0}]".format(
                            bit
                        )  # missing attribute
            if callable(current):
                if getattr(current, "do_not_call_in_templates", False):
                    pass
                elif getattr(current, "alters_data", False):
                    current = "<< invalid -- no data alteration >>"
                else:
                    try:  # method call (assuming no args required)
                        current = current()
                    except TypeError:  # arguments *were* required
                        # GOTCHA: This will also catch any TypeError
                        # raised in the function itself.
                        current = (
                            settings.TEMPLATE_STRING_IF_INVALID
                        )  # invalid method call
    except Exception as e:
        if getattr(e, "silent_variable_failure", False):
            current = "<< invalid -- exception >>"
        else:
            raise

    return force_text(current)


#######################################################################


def safe_get_networking(computer, default_domain=".ad.umanitoba.ca"):
    """
    Get the primary hostname for the computer, 
    but return None if things are funky.
    """
    hostname = None
    ip_address = None
    try:
        iface = computer.get_primary_net_iface()
    except NetworkInterface.DoesNotExist:
        hostname = hostname_slugify(computer.common_name) + default_domain
        ip_address = hostname
    else:
        if iface.ip_address is None:
            hostname = hostname_slugify(computer.common_name) + default_domain
            ip_address = hostname
        elif iface.ip_address.hostname.startswith("."):
            hostname = (
                hostname_slugify(computer.common_name) + iface.ip_address.hostname
            )
            ip_address = iface.ip_address.number
        else:
            hostname = iface.ip_address.hostname
            ip_address = iface.ip_address.number
    return hostname, ip_address


#######################################################################


def ssh_config_format(computer):
    def _has_whitespace(s):
        return any([c.isspace() for c in s])

    def _host(host, hostname, user, port):
        s = """Host {host}\n    HostName {hostname}\n""".format(**locals())
        if port and port not in [22, "22"]:
            s += "    Port {port}\n".format(**locals())
        if user and not _has_whitespace(user):
            s += "    User {user}\n".format(**locals())
        return s

    hostname, ip_address = safe_get_networking(computer)
    user = computer.admin_user
    port = computer.ssh_port
    result = ""
    cname = computer.common_name.strip()
    if not _has_whitespace(cname):
        result += _host(cname, hostname, user, port)
    else:
        cname = None
    host = hostname.split(".", 1)[0]
    if host != cname:
        result += _host(host, hostname, user, port)
    return result


#######################################################################


def nagios_host_format(computer):

    hostname, ip_address = safe_get_networking(computer)
    user = computer.admin_user
    port = computer.ssh_port
    result = ""
    cname = hostname_slugify(computer.common_name.strip())
    result = """define host {{
    use         generic-host
    host_name   {hostname}
    alias       {cname}
    address     {ip_address}
    }}
    """.format(
        **locals()
    )
    return result


#######################################################################


def nagios_hostgroup_format(computer_list, flag_slug_list):
    """
    For each flag slug, create a hostgroup for computers in the 
    computer list which have that flag.
    """
    from ..models import ComputerFlag

    result = ""
    for flag_slug in flag_slug_list:
        try:
            flag = ComputerFlag.objects.active().get(slug=flag_slug)
        except ComputerFlag.DoesNotExist:
            import sys

            sys.stderr.write("ComputerFlag {0!r} does not exist.\n".format(flag_slug))
            sys.stderr.write(
                "Valid flags are: "
                + ",".join(ComputerFlag.objects.active().values_list("slug", flat=True))
                + "\n"
            )
            return ""
        alias = flag.verbose_name
        hostgroup_list = computer_list.filter(flags=flag)
        hostname_list = set(
            [
                safe_get_networking(c)[0]
                for c in hostgroup_list
                if safe_get_networking(c)[0] is not None
            ]
        )
        members = ",".join(hostname_list)
        if members:
            result += """define hostgroup {{
            hostgroup_name  {flag_slug}
            alias           {alias}
            members         {members}
        }}

""".format(
                **locals()
            )
    return result


#######################################################################


def make_field_list(options):
    """
    From the options, return a list of fields.
    """
    results = []
    if options["net"]:
        results += [
            "get_primary_net_iface.mac_address",
            "get_primary_net_iface.ip_address.hostname",
            "get_primary_net_iface.ip_address.number",
        ]
    if options["field_list"]:
        results += options["field_list"].split(",")
    return results


#######################################################################


def main(options, args):
    queryset = Model.objects.active()
    if options["flags"]:
        queryset = queryset.filter(flags__slug__in=options["flags"].split(","))

    if options["nagios_hostgroup"]:
        print(nagios_hostgroup_format(queryset, options["flags"].split(",")))
        return

    for item in queryset:

        if options["ssh_config"]:
            value = ssh_config_format(item)
            if value:
                print(value)
        elif options["nagios_host"]:
            value = nagios_host_format(item)
            if value:
                print(value)
        else:
            value_list = [_resolve_lookup(item, "pk"), "{}".format(item)]
            for field in make_field_list(options):
                value_list.append(_resolve_lookup(item, field))

            s = "\t".join(value_list) + "\n"
            sys.stdout.write(s)


#######################################################################
