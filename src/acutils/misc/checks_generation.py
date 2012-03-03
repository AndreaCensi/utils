""" These are very "meta" utils for creating nose tests on the fly. """
from nose.tools import istest
import sys


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


def add_checker_f(f, x, arguments, attributes):
    @istest
    def test_caller():
        args = arguments(x)
        f(*args)

    name = 'test_%s_%s' % (f.__name__, x)
    test_caller.__name__ = name

    if False: #XXX
        for k, v in attributes(x).items():
            test_caller.__dict__[k] = v

    add_to_module(test_caller, f.__module__)


# TODO: add debug info function
def fancy_test_decorator(lister,
                       arguments=lambda x:x,
                       attributes=lambda x:{'id': str(x)}):
    ''' 
        Creates a fancy decorator for adding checks.
        
        :param lister: a function that should give a list of objects
        :param arguments: from object to arguments
        :param attributes: (optional) set of attributes for the test
        
        Returns a function that can be used as a decorator.
        
    '''

    def for_all_stuff(check):
        for x in lister():
            add_checker_f(check, x, arguments, attributes)


    return for_all_stuff


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

@for_all_thinghies
def check_good_flavor(id_thinghy, flavor):
    print('test for %s %s' % (id_thinghy, flavor))


