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
""" Status Command for RDMC """

import sys

from optparse import OptionParser, SUPPRESS_HELP
from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineErrorOPTS, Encryption, \
                                                    NoCurrentSessionEstablished

class StatusCommand(RdmcCommandBase):
    """ Constructor """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='status',\
            usage='status\n\n\tRun to display all pending changes within'\
                    ' the currently\n\tselected type that need to be' \
                    ' committed\n\texample: status',\
            summary='Displays all pending changes within a selected type'\
                    ' that need to be committed.',\
            aliases=[],\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.selobj = rdmcObj.commands_dict["SelectCommand"](rdmcObj)

    def run(self, line):
        """ Main status worker function

        :param line: command line input
        :type line: string.
        """
        try:
            (options, _) = self._parse_arglist(line)
        except:
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        if options.encode and options.user and options.password:
            options.user = Encryption.decode_credentials(options.user)
            options.password = Encryption.decode_credentials(options.password)

        self.statusvalidation(options)
        contents = self._rdmc.app.status()
        selector = self._rdmc.app.get_selector()

        if contents:
            self.outputpatches(contents, selector)
        else:
            sys.stdout.write("No changes found\n")

        #Return code
        return ReturnCodes.SUCCESS

    def outputpatches(self, contents, selector):
        """ Helper function for status for use in patches

        :param contents: contents for the selection
        :type contents: string.
        :param selector: type selected
        :type selector: string.
        """
        sys.stdout.write("Current changes found:\n")
        for item in contents:
            moveoperation = ""
            for key, value in item.iteritems():
                if selector and key.lower().startswith(selector.lower()):
                    sys.stdout.write("%s (Currently selected)\n" % key)
                else:
                    sys.stdout.write("%s\n" % key)

                for content in value:
                    try:
                        if content['op'] == 'move':
                            moveoperation = '/'.join(content['path'].split('/')[1:-1])
                            continue
                    except:
                        if content[0]['op'] == 'move':
                            moveoperation = '/'.join(content[0]['path'].split('/')[1:-1])
                            continue
                    try:
                        if isinstance(content[0]["value"], int):
                            sys.stdout.write(u'\t%s=%s' % \
                                 (content[0]["path"][1:], content[0]["value"]))
                        elif not isinstance(content[0]["value"], bool) and \
                                            not len(content[0]["value"]) == 0:
                            if content[0]["value"][0] == '"' and \
                                                content[0]["value"][-1] == '"':
                                sys.stdout.write(u'\t%s=%s' % \
                                                    (content[0]["path"][1:], \
                                                    content[0]["value"][1:-1]))
                            else:
                                sys.stdout.write(u'\t%s=%s' % \
                                                    (content[0]["path"][1:], \
                                                     content[0]["value"]))
                        else:
                            output = content[0]["value"]

                            if not isinstance(output, bool):
                                if len(output) == 0:
                                    output = '""'

                            sys.stdout.write(u'\t%s=%s' % \
                                             (content[0]["path"][1:], output))
                    except:
                        if isinstance(content["value"], int):
                            sys.stdout.write(u'\t%s=%s' % \
                                 (content["path"][1:], content["value"]))
                        elif not isinstance(content["value"], bool) and \
                                                not len(content["value"]) == 0:
                            if content["value"][0] == '"' and \
                                                    content["value"][-1] == '"':
                                sys.stdout.write(u'\t%s=%s' % \
                                                        (content["path"][1:], \
                                                        content["value"]))
                            else:
                                sys.stdout.write(u'\t%s=%s' % \
                                                        (content["path"][1:], \
                                                        content["value"]))
                        else:
                            output = content["value"]

                            if not isinstance(output, bool):
                                if len(output) == 0:
                                    output = '""'

                            sys.stdout.write(u'\t%s=%s' % \
                                                (content["path"][1:], output))
                    sys.stdout.write('\n')
            if moveoperation:
                sys.stdout.write(u"\t%s=List Manipulation\n" % moveoperation)

    def statusvalidation(self, options):
        """ Status method validation function """
        try:
            client = self._rdmc.app.get_current_client()
            if options.user and options.password:
                if not client.get_username():
                    client.set_username(options.user)
                if not client.get_password():
                    client.set_password(options.password)
        except:
            raise NoCurrentSessionEstablished("Please login and make setting" \
                                      " changes before using status command.")

    def definearguments(self, customparser):
        """ Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return
        customparser.add_option(
            '-u',
            '--user',
            dest='user',
            help="Pass this flag along with the password flag if you are"\
            "running in local higher security modes.""",
            default=None,
        )
        customparser.add_option(
            '-p',
            '--password',
            dest='password',
            help="Pass this flag along with the username flag if you are"\
            "running in local higher security modes.""",
            default=None,
        )
        customparser.add_option(
            '-e',
            '--enc',
            dest='encode',
            action='store_true',
            help=SUPPRESS_HELP,
            default=False,
        )
