""" 
    These are very "meta" utils for creating nose tests on the fly. 

    Here is an example use: ::

        thinghies = {'banana': 'yellow', 'apple': 'red', 'sky': 'blue'}

        def thinghies_list():
            return thinghies.keys()
        
        def thinghies_args(x):
            return (x, thinghies[x])
        
        def thinghies_attrs(x):
            return dict(thinghy_name='%s' % x, flavor=thinghies[x])
        
        for_all_thinghies = fancy_test_decorator(lister=thinghies_list,
                                                 arguments=thinghies_args,
                                                 attributes=thinghies_attrs)
                                                 
                                           
    And this is the proper test: ::

        @for_all_thinghies
        def check_good_flavor(id_thinghy, flavor):
            print('test for %s %s' % (id_thinghy, flavor))

        
"""
from contracts import describe_value
__all__ = ['fancy_test_decorator']

from nose.tools import istest, nottest
import sys
from .. import logger


def add_to_module(function, module_name):
    module = sys.modules[module_name]
    name = function.__name__

    if not 'test' in name:
        raise Exception('No "test" in function name %r' % name)

    if not 'test' in module_name:
        raise Exception('While adding %r in %r: module does not have "test"'
                        ' in it, so nose will not find the test.' % 
                        (name, module_name))

    if name in module.__dict__:
        raise Exception('Already created test %r.' % name)

    module.__dict__[name] = function

    #logger.debug('Added test %s:%s' % (module.__name__, name))


def add_checker_f(f, x, arguments, attributes, naming):
    name = 'test_%s_%s' % (f.__name__, naming(x))

    @istest
    def caller():
        try: 
            args = arguments(x)
        except Exception as e:
            msg = 'Error while preparing test case: %s.\n' % e
            msg += 'Error while calling %s with argument %r' % (arguments, x)
            logger.error(msg)
            raise  
         
        try:
            f(*args)
        except:
            msg = 'Error while executing test %r.\n' % name
            msg += ' f = %s\n' % f
            msg += ' f.__module__ = %s\n' % f.__module__
            msg += ' x = %s\n' % str(x)
            msg += ' arguments() = %s\n' % str(arguments)
            msg += ' arguments(x) has size %d\n' % len(args)
            for i, a in enumerate(args):
                msg += '  arg %d = %s\n' % (i, describe_value(a))
            logger.error(msg)
            raise

    caller.__name__ = name

    for k, v in attributes(x).items():
        caller.__dict__[k] = v

    caller.__dict__['test'] = f.__name__

    add_to_module(caller, f.__module__)


# TODO: add debug info function
@nottest
def fancy_test_decorator(lister,
                       arguments=lambda x: x,
                       attributes=lambda x: {'id': str(x)},
                       naming=lambda x: str(x),
                       debug=False):
    ''' 
        Creates a fancy decorator for adding checks.
        
        :param lister: a function that should give a list of objects
        :param arguments: from object to arguments
        :param attributes: (optional) set of attributes for the test
        
        Returns a function that can be used as a decorator.
        
    '''

    def for_all_stuff(check):
        for x in lister():
            if debug:
                logger.info('add test %s / %s ' % (check, x))
            add_checker_f(check, x, arguments, attributes, naming)
        return check
    
    return for_all_stuff

