#!/usr/bin/python

import argparse
import subprocess
import os


DIFFCALC_ROOT = os.path.split(os.path.realpath(__file__))[0]


def main():
    parser = argparse.ArgumentParser(description='Diffcalc: A diffraction condition calculator of x-ray and neutron crystalography')
    parser.add_argument('--modules', dest='show_modules', action='store_true',
                        help='list available modules')
    parser.add_argument('--python', dest='use_python', action='store_true',
                        help='run within python rather than ipython')
    parser.add_argument('--debug', dest='debug', action='store_true',
                        help='run in debug mode')
    parser.add_argument('module', type=str, nargs='?',
                        help='the module to startup with')
    args = parser.parse_args()
    
    # Create list of available modules
    module_files = os.listdir(os.path.join(DIFFCALC_ROOT, 'startup'))
    module_names = set([s.split('.')[0] for s in module_files])
    
    if args.show_modules:
        print_available_modules(module_names)
        exit(1)      
    
    if not args.module:   
        print "A module name should be provided. Choose one of:"
        print_available_modules(module_names)
        exit(1)
        
    if args.module not in module_names:
        print "The provided argument '%s' is not one of:" % args.module
        print_available_modules(module_names)
        exit(1)
    
    module_path = os.path.join(DIFFCALC_ROOT, 'startup', args.module) + '.py'
    if args.use_python:
        cmd = "python -i %s" % module_path
    else:
        cmd = "ipython -i %s" % module_path
    env = create_environent_dict(args.debug, args.module)
    print "Running command: '%s'" % cmd
    subprocess.call(cmd, env=env, shell=True)
    
 
def print_available_modules(module_names):           
    lines = []
    for m in sorted(module_names):
        lines.append('   ' + m)
    print '\n'.join(lines)


def create_environent_dict(debug, module_name): 
    env = os.environ.copy()
    
    if 'PYTHONPATH' not in env:
        env['PYTHONPATH'] = ''
    env['PYTHONPATH'] = DIFFCALC_ROOT + ':' + env['PYTHONPATH']
    
    env['DIFFCALC_DEBUG'] = str(debug)
    
    env['DIFFCALC_VAR'] = os.path.join(os.path.expanduser('~'), '.diffcalc', module_name)
    
    for var in ('PYTHONPATH', 'DIFFCALC_DEBUG', 'DIFFCALC_VAR'):
        print '%s: %s' % (var, env[var])
    
    return env


if __name__ == '__main__':
    main()
# 