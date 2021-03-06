#!/usr/bin/env python

import argparse
import os
import string
import sys

try:
    import configparser
    from prettytable import PrettyTable
except Exception as e:
    print e
    sys.exit(2)


def file_exists(inifile):
    if os.path.isfile(inifile):
        return True
    else:
        return False


def replace_dot(var):
    return string.replace(var, ".", "_")


def print_conf_table(config_file, namespace, config_parser):
    config_parser.read(config_file)

    table = PrettyTable(["Section", "Config Key", "Value", "Ansible Var's"])
    table.align["Section"] = "l"
    table.align["Config Key"] = "r"
    table.align["Ansible Variable"] = "l"

    for x in config_parser.sections():
        for item in config_parser.items(x):
            ansible_variable = namespace + "_" + replace_dot(x) + "_" + item[0]
            table.add_row([x.upper(), item[0], item[1], ansible_variable])

    print table


def write_ansible_defaults(config_file, namespace, config_parser):
    config_parser.read(config_file)

    var_filename = config_file + ".yaml"
    defaults_file = open(var_filename, "wb")
    defaults_file.write("---\n\n")

    for x in config_parser.sections():
        if config_parser.items(x):
            for item in config_parser.items(x):
                variable = namespace + "_" + replace_dot(x) + "_" + item[0]

                if item[1].lower() not in ["true", "false"]:
                    value = "\"" + item[1] + "\""
                else:
                    value = item[1]

                line = variable + ": " + value

                defaults_file.write(line + "\n")

            defaults_file.write("\n")
        else:
            continue

    defaults_file.close()


def write_ansible_template(config_file, namespace, config_parser):

    template_file = config_file + ".j2"

    for x in config_parser.sections():
        for item in config_parser.items(x):
            variable = namespace + "_" + replace_dot(x) + "_" + item[0]
            template_variable = "{{ " + variable + " }}"

            config_parser.set(x, item[0], template_variable)

            with open(template_file, "wb") as f:
                config_parser.write(f)


def main():

    """Convert config files to var files and templates for Ansible."""

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-c", "--conf", required=True,
                            help="config file to convert to template")

    arg_parser.add_argument("-n", required=True,
                            help="namespace to prepend for variables")

    group = arg_parser.add_mutually_exclusive_group()
    group.add_argument("-p",
                       help="print a table with ansible variables",
                            action="store_true")

    group.add_argument("-o", "--out",
                       help="name for the generated ansible var file")
    args = arg_parser.parse_args()

    config_parser = configparser.RawConfigParser()

    if file_exists(args.conf):
        if args.p:
            print_conf_table(args.conf, args.n, config_parser)

        if args.out:
            write_ansible_defaults(args.conf, args.n, config_parser)
            write_ansible_template(args.conf, args.n, config_parser)


if __name__ == "__main__":
    main()
