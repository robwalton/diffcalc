from diffcalc.utils import getMessageFromException
try:
    from gda.device.scannable import ScannableMotionBase
except ImportError:
    from diffcalc.gdasupport.minigda.scannable.scannable import Scannable as ScannableMotionBase
    
# TODO: Split into a base class when making other scannables

class DiffractometerScannableGroup(ScannableMotionBase):
    """"Wraps up a scannableGroup of axis to tweak the way the resulting object is
    displayed and to add a simulate move to method.
    
    The scannable group should have the same geometry as that expected by the
    diffractometer hardware geometry used in the diffraction calculator.
    
    The optional parameter slaveDriver can be used to provide a slave_driver. This is useful for
    triggering a move of an incidental axis whose position depends on that of the diffractometer, but whose
    position need not be included in the DiffractometerScannableGroup itself. This parameter is exposed
    as a field and can be set or cleared to null at will without effecting the core calculation code.
    """
    
    def __init__(self , name , diffcalcObject, scannableGroup, slave_driver=None):
        # if motorList is None, will create a dummy __group
        self.__diffcalc = diffcalcObject
        self.__group = scannableGroup
        self.slave_driver = slave_driver
        self.setName(name)

    def getInputNames(self):
        return self.__group.getInputNames()
        
    def getExtraNames(self):
        return [] if self.slave_driver is None else self.slave_driver.getScannableNames()
        
    def getOutputFormat(self):
        slave_formats = [] if self.slave_driver is None else self.slave_driver.getOutputFormat()
        return list(self.__group.getOutputFormat()) + slave_formats
        
    
    def setDiffcalcObject(self, diffcalcObject):
        self.__diffcalc = diffcalcObject
    
    def asynchronousMoveTo(self, position):
        self.__group.asynchronousMoveTo(position)
        if self.slave_driver is not None:
            self.slave_driver.triggerAsynchronousMove(position)
        
    def getPosition(self):
        slave_positions = [] if self.slave_driver is None else self.slave_driver.getPositions()
        return list(self.__group.getPosition()) + list(slave_positions)
        
    def isBusy(self):
        if self.slave_driver is None:
            return self.__group.isBusy()
        else:
            return self.__group.isBusy() or self.slave_driver.isBusy() 
        
    def waitWhileBusy(self):
        self.__group.waitWhileBusy()
        if self.slave_driver is not None:
            self.slave_driver.waitWhileBusy() 
    
    def simulateMoveTo(self, pos):
        if len(pos) != len(self.getInputNames()): raise ValueError('Wrong number of inputs')
        try:
            (hkl, params) = self.__diffcalc._anglesToHkl(pos)
        except Exception, e:
            return "Error: %s" % getMessageFromException(e)
        width = max(len(k) for k in params)
        
        lines = ['  ' + 'hkl'.rjust(width) + ' : % 9.4f  %.4f  %.4f' % (hkl[0], hkl[1], hkl[2])]
        lines[-1] =  lines[-1] + '\n'
        fmt = '  %' + str(width) + 's : % 9.4f'     
        for k in sorted(params):
            lines.append(fmt % (k, params[k]))
        return '\n'.join(lines)
    
    def __repr__(self):
        position = self.getPosition()
        names = list(self.getInputNames()) + list(self.getExtraNames())

        lines = [self.name + ':']
        width = max(len(k) for k in names)
        fmt = '  %' + str(width) + 's : % 9.4f' 
        for name, pos in zip(names, position):
            lines.append(fmt % (name, pos))
        lines[len(self.getInputNames())] =  lines[len(self.getInputNames())] + '\n'
        return '\n'.join(lines)
