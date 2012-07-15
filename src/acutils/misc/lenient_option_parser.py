__version__ = '1.0'

from . import UserError
from optparse import IndentedHelpFormatter
import optparse


class LenientOptionParser(optparse.OptionParser):
    
    def parse_args(self, args):
        self.arguments = list(args)
        return optparse.OptionParser.parse_args(self, args)
    
    def error(self, msg):
        #msg = '%s: %s' % (self.get_prog_name(), msg)
        msg += ('\nArguments: %s %s' % 
                (self.get_prog_name(), " ".join(self.arguments)))
        raise UserError(msg)


def OptionParser(prog, usage):
    formatter = IndentedHelpFormatter(
                 indent_increment=2,
                 max_help_position=80,
                 width=100,
                 short_first=1)                               
    return LenientOptionParser(formatter=formatter, usage=usage, prog=prog)

