import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Qt5Agg')
# import pyqtgraph as pg
# from pyqtgraph import PlotWidget, plot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from qgis.PyQt import uic, QtWidgets
from qgis.PyQt.QtCore import Qt

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        # self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)

class PlotWindow(QtWidgets.QDialog):

    def __init__(self,values,cmpInit,percentFlag,metricName,feedback):
        super().__init__()
        self.values = values
        self.cmpInit = cmpInit
        self.percentFlag = percentFlag
        self.metricName = metricName
        self.feedback = feedback
        self.initValues()

        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        # self.canvas.axes.plot([0,1,2,3,4], [10,1,20,3,40])
        self.plotByScenario()
        self.canvas.fig.tight_layout()

        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        toolbar = NavigationToolbar(self.canvas, self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.canvas)

        # Create a placeholder widget to hold our toolbar and canvas.
        # widget = QtWidgets.QWidget()
        self.setLayout(layout)
        # self.setCentralWidget(widget)
        
    # def getValuesByScenario(self):
        # res = []
        # for sc, spDict in self.values.iteritems():
            # res.append(spDict.values())
        # return res
        
    def initValues(self):
        self.scLabels = list(self.values.keys())
        self.nbSc = len(self.scLabels)
        self.spView = {}
        for scName, spDict in self.values.items():
            for spName, val in spDict.items():
                if spName not in self.spView:
                    self.spView[spName] = {}
                self.spView[spName][scName] = val
        self.spLabels = list(self.spView.keys())
        self.nbSp = len(self.spLabels)
        self.feedback.pushDebugInfo("scLabels = " + str(self.scLabels))
        self.feedback.pushDebugInfo("spLabels = " + str(self.spLabels))
        self.feedback.pushDebugInfo("spView = " + str(self.spView))
        
    def get_cmap(self,n, name='hsv'):
        return plt.cm.get_cmap(name, n)
        
    def getYLabel(self):
        if self.cmpInit:
            s = "\u0394 " + self.metricName + " with initial state"
            if self.percentFlag:
                s =  "% of " + s
        else:
            s = self.metricName
        return s
        
    def plotByScenario(self):
        toPlot = []
        self.feedback.pushDebugInfo("values = " + str(self.values))
        # for sc, spDict in self.values.items():
            # self.feedback.pushDebugInfo("sc = " + str(sc))
            # for sp, val in spDict.items():
                # self.feedback.pushDebugInfo("sp = " + str(sp))
                # self.feedback.pushDebugInfo("val = " + str(val))
            # toPlot.append(list(spDict.values()))
        # self.feedback.pushDebugInfo("toPlot = " + str(toPlot))
        # self.feedback.pushDebugInfo("df = " + str(df))
        bins = list(range(1,self.nbSc + 1))
        self.feedback.pushDebugInfo("bins = " + str(bins))
        x = range(self.nbSc)
        yLabel = self.getYLabel()
        cpt = 1
        for sp, scDict in self.spView.items():
            splot = self.canvas.fig.add_subplot(self.nbSp,1,cpt)
            splot.set_xlabel("Scenarios")
            splot.set_ylabel(yLabel)
            keys = list(scDict.keys())
            values = list(scDict.values())
            col = (np.random.random(), np.random.random(), np.random.random())
            splot.set_title(sp)
            # splot.ylabel("Connectivity")
            # splot.bar(keys,values,color=col,width=0.1,align='center')
            splot.bar(keys,values,color=col)#,width=0.1,align='edge')#,labels=self.scLabels)
            cpt+=1
        # toPlot = [(0,1,2,3,4), (10,1,20,3,40)]
        colors = ['red', 'tan']
        # colors = [self.get_cmap(i) for i in range(nbSc)]
        # self.canvas.axes.hist(df,bins,histtype='bar')
        # self.canvas.axes.hist(toPlot, 10 density=True, histtype='bar', color=colors, label=colors)
        # self.canvas.legend(prop={'size': 10})
        # self.canvas.set_title('bars with legend')

        # self.show()

# class PlotWindow(QtWidgets.QMainWindow):

    # def __init__(self):
        # super(MainWindow, self).__init__()

        # self.graphWidget = pg.PlotWidget()
        # self.setCentralWidget(self.graphWidget)

        # hour = [1,2,3,4,5,6,7,8,9,10]
        # temperature = [30,32,34,32,33,31,29,32,35,45]

        # self.graphWidget.plot(hour, temperature)