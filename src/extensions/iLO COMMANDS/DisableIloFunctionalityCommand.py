###
# Copyright 2017 Hewlett Packard Enterprise, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###

# -*- coding: utf-8 -*-
""" iLO Functionality Command for rdmc """
import sys

from optparse import OptionParser
from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineError, \
                    InvalidCommandLineErrorOPTS, \
                    NoContentsFoundForOperationError, \
                    IncompatableServerTypeError

class DisableIloFunctionalityCommand(RdmcCommandBase):
    """ Disables iLO functionality to the server """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='disableilofunctionality',\
            usage='disableilofunctionality [OPTIONS]\n\n\t'\
                'Disable iLO functionality on the current logged in server.' \
                '\n\texample: disableilofunctionality\n\n\tWARNING: this will' \
                ' render iLO unable to respond to network operations.',\
            summary="disables iLO's accessibility via the network and resets "\
            "iLO. WARNING: This should be used with caution as it will "\
            "render iLO unable to respond to further network operations "\
            "(including REST operations) until iLO is re-enabled using the"\
            " RBSU menu.",\
            aliases=None,\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)
        self.selobj = rdmcObj.commands_dict["SelectCommand"](rdmcObj)
        self.getobj = rdmcObj.commands_dict["GetCommand"](rdmcObj)

    def run(self, line):
        """ Main DisableIloFunctionalityCommand function

        :param line: string of arguments passed in
        :type line: str.
        """
        try:
            (options, args) = self._parse_arglist(line)
        except:
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        if args:
            raise InvalidCommandLineError("disableilofunctionality command " \
                                                        "takes no arguments.")

        self.ilofunctionalityvalidation(options)

        self.selobj.selectfunction("Chassis.")
        chassistype = self.getobj.getworkerfunction("ChassisType", options, \
									"ChassisType", results=True, uselist=True)

        if chassistype['ChassisType'].lower() == 'blade':
            raise IncompatableServerTypeError("disableilofunctionality command"\
                                    " is not available on blade server types.")

        select = 'Manager.'
        results = self._rdmc.app.filter(select, None, None)

        try:
            results = results[0]
        except:
            pass

        if results:
            path = results.resp.request.path
        else:
            raise NoContentsFoundForOperationError("Manager. not found.")

        bodydict = results.resp.dict['Oem'][self.typepath.defs.oemhp]

        try:
            for item in bodydict['Actions']:
                if 'iLOFunctionality' in item:
                    if self.typepath.defs.isgen10:
                        action = item.split('#')[-1]
                    else:
                        action = "iLOFunctionality"

                    path = bodydict['Actions'][item]['target']
                    body = {"Action": action}
                    break
        except:
            body = {"Action": "iLOFunctionality", \
                                "Target": "/Oem/Hp"}

        sys.stdout.write(u"Disabling iLO functionality. iLO will be unavailable"\
                         " on the logged in server until it is re-enabled "\
                         "manually.\n")

        results = self._rdmc.app.post_handler(path, body, silent=True, service=True, \
                                    response=True)

        if results.status == 200:
            sys.stdout.write(u"[%d] The operation completed " \
                                            "successfully.\n" % results.status)
        else:
            sys.stdout.write(u"[%d] No message returned by iLO.\n" % results.status)

        return ReturnCodes.SUCCESS

    def ilofunctionalityvalidation(self, options):
        """ ilofunctionalityvalidation method validation function

        :param options: command line options
        :type options: list.
        """
        client = None
        inputline = list()

        try:
            client = self._rdmc.app.get_current_client()
            if options.user and options.password:
                if not client.get_username():
                    client.set_username(options.user)
                if not client.get_password():
                    client.set_password(options.password)
        except:
            if options.user or options.password or options.url:
                if options.url:
                    inputline.extend([options.url])
                if options.user:
                    inputline.extend(["-u", options.user])
                if options.password:
                    inputline.extend(["-p", options.password])
            else:
                if self._rdmc.app.config.get_url():
                    inputline.extend([self._rdmc.app.config.get_url()])
                if self._rdmc.app.config.get_username():
                    inputline.extend(["-u", \
                                  self._rdmc.app.config.get_username()])
                if self._rdmc.app.config.get_password():
                    inputline.extend(["-p", \
                                  self._rdmc.app.config.get_password()])

        if inputline or not client:
            if not inputline:
                sys.stdout.write(u'Local login initiated...\n')
            self.lobobj.loginfunction(inputline)
        elif not client:
            raise InvalidCommandLineError("Please login or pass credentials" \
                                          " to complete the operation.")

    def definearguments(self, customparser):
        """ Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return
        customparser.add_option(
            '--url',
            dest='url',
            help="Use the provided iLO URL to login.",
            default=None,
        )
        customparser.add_option(
            '-u',
            '--user',
            dest='user',
            help="If you are not logged in yet, including this flag along"\
            " with the password and URL flags can be used to log into a"\
            " server in the same command.""",
            default=None,
        )
        customparser.add_option(
            '-p',
            '--password',
            dest='password',
            help="""Use the provided iLO password to log in.""",
            default=None,
        )
