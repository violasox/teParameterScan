import tellurium as te
import imp

ps = imp.load_source('ParameterScan', 'D:/ParameterScan/ParameterScan.py')
#foo.MyClass()


cell = '''
    $Xo -> S1; vo;
    S1 -> S2; k1*S1 - k2*S2;
    S2 -> $X1; k3*S2;
    
    vo = 1
    k1 = 2; k2 = 0; k3 = 3;
'''

rr = te.loadAntimonyModel(cell)
p = ps.ParameterScan(rr)

p.endTime = 3
p.colormap = p.createColormap([.12,.56,1], [.86,.08,.23])
#p.dependent = 'S1'
#p.independent = ['time', 'k1']
p.startValue = 0.5
p.endValue = 5
p.title = 'Concentration of S1'
p.zlabel = None

p.plotSurface()
