import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np
import matplotlib

class ParameterScan (object):
    def __init__(self, rr):
        self.startTime = 0
        self.endTime = 20
        self.numberOfPoints = 50
        self.polyNumber = 10
        self.startValue = None
        self.endValue = None
        self.value = None
        self.independent = None
        self.selection = None
        self.dependent = None
        self.integrator = "cvode"
        self.rr = rr
        self.color = None
        self.width = 2.5
        self.alpha = 0.7
        self.title = None
        self.xlabel = 'toSet'
        self.ylabel = 'toSet'
        self.zlabel = 'toSet'
        self.colormap = "seismic"
        self.colorbar = True
        self.antialias = True
        self.sameColor = False

    
    def sim(self):
        """Runs a simulation and returns the result for a plotting function. Not intended to
        be called by user."""
        if self.selection is None:
            result = self.rr.simulate(self.startTime, self.endTime, self.numberOfPoints,
                                      integrator = self.integrator)
        else:
            result = self.rr.simulate(self.startTime, self.endTime, self.numberOfPoints,
                                      self.selection, integrator = self.integrator)
        return result

    def plotArray(self):
        """Plots result of simulation with options for linewdith and line color.

        p.plotArray()"""
        result = self.sim()
        if self.color is None:
            plt.plot(result[:,0], result[:,1:], linewidth = self.width)
        else:
            if len(self.color) != result.shape[1]:
                self.color = self.colorCycle()
            for i in range(result.shape[1] - 1):
                plt.plot(result[:,0], result[:,(i+1)],
                         color = self.color[i], linewidth = self.width)

#        if self.ylabel is not None:
#            plt.ylabel(self.ylabel)
#        if self.xlabel is not None:
#            plt.xlabel(self.xlabel)
            
        if self.xlabel == 'toSet':
            plt.xlabel('time')
        elif self.xlabel:
            plt.xlabel(self.xlabel)
        if self.ylabel == 'toSet':
            plt.ylabel('concentration')
        elif self.ylabel:
            plt.ylabel(self.ylabel)
            
        if self.title is not None:
            plt.suptitle(self.title)
        plt.show()

    def graduatedSim(self):
        """Runs successive simulations with incremental changes in one species, and returns
        results for a plotting function. Not intended to be called by user."""
        if self.value is None:
            self.value = self.rr.model.getFloatingSpeciesIds()[0]
            print 'Warning: self.value not set. Using self.value = %s' % self.value
        if self.startValue is None:
            self.startValue = self.rr.model[self.value]
        else:
            self.startValue = float(self.startValue)
        if self.endValue is None:
            self.endValue = self.startValue + 5
        else:
            self.endValue = float(self.endValue)
        if self.selection is None:
            self.selection = self.value
#        if self.value is None:
#            self.value = self.rr.model.getFloatingSpeciesIds()[0]
#            print 'Warning: self.value not set. Using self.value = %s' % self.value
        self.rr.model[self.value] = self.startValue
        m = self.rr.simulate(self.startTime, self.endTime, self.numberOfPoints,
                             ["Time", self.selection], integrator = self.integrator)
        interval = ((self.endValue - self.startValue) / (self.polyNumber))
        start = self.startValue
        while start < self.endValue:
            self.rr.reset()
            self.rr.model[self.value] = start
            m1 = self.rr.simulate(self.startTime, self.endTime, self.numberOfPoints,
                                  [self.selection], integrator = self.integrator)
            m = np.hstack((m, m1))
            start += interval
        return m

    def plotGraduatedArray(self):
        """Plots array with either default multiple colors or user sepcified colors using
        results from graduatedSim().

        p.plotGraduatedArray()"""
        result = self.graduatedSim()
        if self.color is None and self.sameColor is True:
            plt.plot(result[:,0], result[:,1:], linewidth = self.width, color = 'b')
        elif self.color is None:
            plt.plot(result[:,0], result[:,1:], linewidth = self.width)
        else:
            if len(self.color) != self.polyNumber:
                self.color = self.colorCycle()
            for i in range(self.polyNumber):
                plt.plot(result[:,0], result[:,(i+1)], color = self.color[i],
                             linewidth = self.width)
                         
         
#        if self.ylabel is not None:
#            plt.ylabel(self.ylabel)
#        if self.xlabel is not None:
#            plt.xlabel(self.xlabel)
        if self.title is not None:
            plt.suptitle(self.title)
        if self.xlabel == 'toSet':
            plt.xlabel('time')
        elif self.xlabel:
            plt.xlabel(self.xlabel)
        if self.ylabel == 'toSet':
            plt.ylabel('concentration')
        elif self.ylabel:
            plt.ylabel(self.ylabel)
        plt.show()

    def plotPolyArray(self):
        """Plots results as individual graphs parallel to each other in 3D space using results
        from graduatedSim().

        p.plotPolyArray()"""
        result = self.graduatedSim()
        interval = ((self.endValue - self.startValue) / (self.polyNumber - 1))
        self.rr.reset()
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        if self.startValue is None:
            self.startValue = self.rr.model[self.value]
        columnNumber = int((((self.endValue - self.startValue) / self.polyNumber)) + 2)
        columnNumber = self.polyNumber
        lastPoint = [self.endTime]
        for i in range(columnNumber):
            lastPoint.append(0)
        lastPoint = np.array(lastPoint)
        lastPoint = np.vstack((result, lastPoint))
        zs = []
        result = []
        for i in range(columnNumber):
            zs.append(i)
            result.append(zip(lastPoint[:,0], lastPoint[:,(i+1)]))
        if self.color is None:
            poly = PolyCollection(result)
        else:
            if len(self.color) != self.polyNumber:
                self.color = self.colorCycle()
            poly = PolyCollection(result, facecolors = self.color)

        poly.set_alpha(self.alpha)
        ax.add_collection3d(poly, zs=zs, zdir='y')
        ax.set_xlim3d(0, self.endTime)
        ax.set_ylim3d(0, (columnNumber - 1))
        ax.set_zlim3d(0, (self.endValue + interval))
        if self.xlabel == 'toSet':
            ax.set_xlabel(self.independent[0])
        elif self.xlabel:
            ax.set_xlabel(self.xlabel)
        if self.ylabel == 'toSet':
            ax.set_ylabel(self.independent[1])
        elif self.ylabel:
            ax.set_ylabel(self.ylabel)
        if self.zlabel == 'toSet':
            ax.set_zlabel(self.dependent)
        elif self.zlabel:
            ax.set_zlabel(self.zlabel)
#        ax.set_xlabel('Time') if self.xlabel is None else ax.set_xlabel(self.xlabel)
#        ax.set_ylabel('Trial Number') if self.ylabel is None else ax.set_ylabel(self.ylabel)
#        ax.set_zlabel(self.value) if self.zlabel is None else ax.set_zlabel(self.zlabel)
        if self.title is not None:
            ax.set_title(self.title)
        plt.show()

    def plotSurface(self):
        """ Plots results of simulation as a colored surface. Takes three variables, two
        independent and one dependent. Legal colormap names can be found at
        http://matplotlib.org/examples/color/colormaps_reference.html.

        p.plotSurface()"""
        try:
#            if self.independent is None and self.dependent is None:
#                self.independent = ['Time']
#                defaultParameter = self.rr.model.getGlobalParameterIds()[0]
#                self.independent.append(defaultParameter)
#                defaultSpecies = self.rr.model.getFloatingSpeciesIds()[0]
#                self.dependent = [defaultSpecies]
#                print 'Warning: self.independent and self.dependent not set. Using' \
#                ' self.independent = %s and self.dependent = %s' % (self.independent, self.dependent)
            if self.independent is None:
                self.independent = ['Time']
                defaultParameter = self.rr.model.getGlobalParameterIds()[0]
                self.independent.append(defaultParameter)
                print 'Warning: self.independent not set. Using: {0}'.format(self.independent)
            if self.dependent is None:
                defaultSpecies = self.rr.model.getFloatingSpeciesIds()[0]
                self.dependent = defaultSpecies
                print 'Warning: self.dependent not set. Using: {0}'.format(self.dependent)
                
            if len(self.independent) < 2:
                raise Exception('self.independent must contain two independent variables')
            
#            if not isinstance(self.independent, list) or not isinstance(self.dependent, list):
#                raise Exception('self.indpendent and self.dependent must be lists of strings')
            if not isinstance(self.independent, list):
                raise Exception('self.independent must be a list of strings')
            if not isinstance(self.dependent, str):
                raise Exception('self.dependent must be a string')
            if self.startValue is None:
                if self.independent[0] != 'Time' and self.independent[0] != 'time':
                    self.startValue = self.rr.model[self.independent[0]]
                else:
                    self.startValue = self.rr.model[self.independent[1]]
            if self.endValue is None:
                self.endValue = self.startValue + 5
    
    
            fig = plt.figure()
            ax = fig.gca(projection='3d')
            interval = (self.endTime - self.startTime) / float(self.numberOfPoints - 1)
            X = np.arange(self.startTime, (self.endTime + (interval - 0.001)), interval)
            interval = (self.endValue - self.startValue) / float(self.numberOfPoints - 1)
            Y = np.arange(self.startValue, (self.endValue + (interval - 0.001)), interval)
            X, Y = np.meshgrid(X, Y)
            self.rr.reset()
            self.rr.model[self.independent[1]] = self.startValue
            Z = self.rr.simulate(self.startTime, self.endTime, (self.numberOfPoints),
                                 [self.dependent], integrator = self.integrator)
            Z = Z.T
            for i in range(self.numberOfPoints - 1):
                self.rr.reset()
                self.rr.model[self.independent[1]] = self.startValue + ((i + 1) * interval)
                Z1 = self.rr.simulate(self.startTime, self.endTime, (self.numberOfPoints),
                                     [self.dependent], integrator = self.integrator)
                Z1 = Z1.T
                Z = np.concatenate ((Z, Z1))
    
            if self.antialias is False:
                surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap = self.colormap,
                                       antialiased = False, linewidth=0)
            else:
                surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap = self.colormap,
                                       linewidth=0)
    
            ax.yaxis.set_major_locator(LinearLocator((6)))
            ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
            if self.xlabel == 'toSet':
                ax.set_xlabel(self.independent[0])
            elif self.xlabel:
                ax.set_xlabel(self.xlabel)
            if self.ylabel == 'toSet':
                ax.set_ylabel(self.independent[1])
            elif self.ylabel:
                ax.set_ylabel(self.ylabel)
            if self.zlabel == 'toSet':
                ax.set_zlabel(self.dependent)
            elif self.zlabel:
                ax.set_zlabel(self.zlabel)
#            ax.set_xlabel(self.independent[0]) if self.xlabel is None else ax.set_xlabel(self.xlabel)
#            ax.set_ylabel(self.independent[1]) if self.ylabel is None else ax.set_ylabel(self.ylabel)
#            ax.set_zlabel(self.dependent) if self.zlabel is None else ax.set_zlabel(self.zlabel)
            if self.title is not None:
                ax.set_title(self.title)
    
            if self.colorbar:
                fig.colorbar(surf, shrink=0.5, aspect=4)
    
            plt.show()
        
        except Exception as e:
            print 'error: {0}'.format(e.message)

    def plotMultiArray(self, param1, param1Range, param2, param2Range):
        """Plots separate arrays for each possible combination of the contents of param1range and
        param2range as an array of subplots. The ranges are lists of values that determine the
        initial conditions of each simulation.

        p.multiArrayPlot('S1', [1, 2, 3], 'S2', [1, 2])"""
        f, axarr = plt.subplots(
            len(param1Range),
            len(param2Range),
            sharex='col',
            sharey='row')

        if self.color is None:
            self.color = ['b', 'g', 'r', 'k']

        for i, k1 in enumerate(param1Range):
            for j, k2 in enumerate(param2Range):
                self.rr.reset()
                self.rr.model[param1], self.rr.model[param2] = k1, k2
                if self.selection is None:
                    result = self.rr.simulate(self.startTime, self.endTime, self.numberOfPoints,
                                              integrator = self.integrator)
                else:
                     result = self.rr.simulate(self.startTime, self.endTime, self.numberOfPoints,
                                               self.selection, integrator = self.integrator)
                columns = result.shape[1]
                legendItems = self.rr.selections[1:]
                if columns-1 != len(legendItems):
                    raise Exception('Legend list must match result array')
                for c in range(columns-1):
                    axarr[i, j].plot(
                        result[:, 0],
                        result[:, c+1],
                        linewidth = self.width,
                        label = legendItems[c])

                if (i == (len(param1Range) - 1)):
                    axarr[i, j].set_xlabel('%s = %.2f' % (param2, k2))
                if (j == 0):
                    axarr[i, j].set_ylabel('%s = %.2f' % (param1, k1))
                if self.title is not None:
                    plt.suptitle(self.title)


    def createColormap(self, color1, color2):
        """Creates a color map for plotSurface using two colors as RGB tuplets, standard color
        names, e.g. 'aqua'; or hex strings.

        p.colormap = p.createColorMap([0,0,0], [1,1,1])"""

        if isinstance(color1, str) is True:
            color1 = matplotlib.colors.colorConverter.to_rgb('%s' % color1)
        if isinstance(color2, str) is True:
            color2 = matplotlib.colors.colorConverter.to_rgb('%s' % color2)

        print color1, color2

        cdict = {'red': ((0., 0., color1[0]),
                         (1., color2[0], 0.)),

                 'green': ((0., 0., color1[1]),
                           (1., color2[1], 0.)),

                 'blue': ((0., 0., color1[2]),
                          (1., color2[2], 0.))}
        my_cmap = matplotlib.colors.LinearSegmentedColormap('my_colormap',cdict,256)
        return my_cmap


    def colorCycle(self):
        """Adjusts contents of self.color as needed for plotting methods."""
        if len(self.color) < self.polyNumber:
            for i in range(self.polyNumber - len(self.color)):
                self.color.append(self.color[i])
        else:
            for i in range(len(self.color) - self.polyNumber):
                del self.color[-(i+1)]
        return self.color

    def createColorPoints(self):
        """Sets self.color to a set of values that allow plotPolyArray, plotArray,
        or plotGraduatedArray to take on colors from a colormap. The colormap can either
        be user-defined using createColormap or one of the standard colormaps.

        p.createColorPoints() """
        color = []
        interval = 1.0 / self.polyNumber
        count = 0
        if isinstance(self.colormap, str) is True:
            for i in range(self.polyNumber):
                color.append(eval('matplotlib.pylab.cm.%s(%s)' % (self.colormap, count)))
                count += interval
        else:
            for i in range(self.polyNumber):
                color.append(self.colormap(count))
                count += interval
        self.color = color
        


class SteadyStateScan (object):
    def __init__(self, rr):
        self.startTime = 0
        self.endTime = 20
        self.numberOfPoints = 50
        self.polyNumber = 10
        self.startValue = None
        self.endValue = None
        self.value = None
        self.independent = None
        self.selection = None
        self.dependent = None
        self.integrator = "cvode"
        self.rr = rr
        self.color = None
        self.width = 2.5
        self.alpha = 0.7
        self.title = None
        self.xlabel = None
        self.ylabel = None
        self.zlabel = None
        self.colormap = "seismic"
        self.colorbar = True
        self.antialias = True
        self.sameColor = False

    def steadyStateSim(self):
        if self.value is None:
            self.value = self.rr.model.getFloatingSpeciesIds()[0]
            print 'Warning: self.value not set. Using self.value = %s' % self.value
        if self.startValue is None:
            self.startValue = self.rr.model[self.value]
        if self.endValue is None:
            self.endValue = self.startValue + 5
        interval = (float(self.endValue - self.startValue) / float(self.numberOfPoints - 1))
        a = []
        for i in range(len(self.selection) + 1):
            a.append(0.)
        result = np.array(a)
        start = self.startValue
        for i in range(self.numberOfPoints):
            self.rr.reset()
            start += interval
            self.rr.model[self.value] = start
            self.rr.steadyState()
            b = [self.rr.model[self.value]]
            for i in range(len(self.selection)):
                b.append(self.rr.model[self.selection[i]])
            result = np.vstack((result, b))
        result = np.delete(result, 0, 0)
        return result

    def plotArray(self):
        result = self.steadyStateSim()
        print result
        if self.color is None:
            plt.plot(result[:,0], result[:,1:], linewidth = self.width)
        else:
            if len(self.color) != result.shape[1]:
                self.color = self.colorCycle()
            for i in range(result.shape[1] - 1):
                plt.plot(result[:,0], result[:,i], color = self.color[i], linewidth = self.width)
