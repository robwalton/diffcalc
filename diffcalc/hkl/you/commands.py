###
# Copyright 2008-2011 Diamond Light Source Ltd.
# This file is part of Diffcalc.
#
# Diffcalc is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Diffcalc is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Diffcalc.  If not, see <http://www.gnu.org/licenses/>.
###

from diffcalc.hkl.common import getNameFromScannableOrString
from diffcalc.util import command
from numbers import Number


class YouHklCommands(object):

    def __init__(self, hklcalc):
        self._hklcalc = hklcalc
        self.commands = ['CONSTRAINTS',
                         self.con,
                         self.uncon,
                         self.cons]

    def __str__(self):
        return self._hklcalc.__str__()

    @command
    def con(self, *args):
        """
        con -- list available constraints and values
        con <name> {val}-- constrains and optionally sets one constraint
        con <name> {val} <name> {val} <name> {val}-- clears and then fully constrains
        """
        args = list(args)
        msg = self.handle_con(args)
        if msg:
            print msg
 
    def handle_con(self, args):
        if not args:
            raise TypeError("Arguments expected")
        
        if len(args) > 6:
            raise TypeError("Unexpected args: " + str(args))
        
        cons_value_pairs = []
        while args:
            scn_or_str = args.pop(0)
            name = getNameFromScannableOrString(scn_or_str)
            if args and isinstance(args[0], Number):
                value = args.pop(0)
            else:
                value = None
            cons_value_pairs.append((name, value))
        
        if len(cons_value_pairs) == 1:
            pass
        elif len(cons_value_pairs) == 3:
            self._hklcalc.constraints.clear_constraints()
        else:
            raise TypeError("Either one or three constraints must be specified")
        for name, value in cons_value_pairs:
            self._hklcalc.constraints.constrain(name)
            if value is not None:
                self._hklcalc.constraints.set_constraint(name, value)
        return '\n'.join(self._hklcalc.constraints.report_constraints_lines())


    @command
    def uncon(self, scn_or_string):
        """uncon <constraint> -- remove constraint
        """
        name = getNameFromScannableOrString(scn_or_string)
        self._hklcalc.constraints.unconstrain(name)
        print '\n'.join(self._hklcalc.constraints.report_constraints_lines())

    @command
    def cons(self):
        """cons -- list available constraints and values

        Select three constraints using 'con' and 'uncon'. Choose up to one
        from each of the sample and detector columns and up to three from
        the sample column.

        Not all constraint combinations are currently available:

            1 x samp:              all 80 of 80
            2 x samp and 1 x ref:  chi & phi
                                   mu & eta
                                   chi=90 & mu=0 (2.5 of 6)
            2 x samp and 1 x det:  0 of 6
            3 x samp:              0 of 4

        See also 'con' and 'uncon'
        """
        print self._hklcalc.constraints
