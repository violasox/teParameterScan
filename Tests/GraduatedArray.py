import tellurium as te
import imp

ps = imp.load_source('ParameterScan', 'D:/ParameterScan/ParameterScan.py')

r = te.loada('''
    $Xo -> S1; vo;
    S1 -> S2; k1*S1 - k2*S2;
    S2 -> $X1; k3*S2;

    vo = 1
    k1 = 2; k2 = 0; k3 = 3;
''')

p = ps.ParameterScan(r)

p.startTime = 0
p.endTime = 4
p.numberOfPoints = 50
p.polyNumber = 6
p.startValue = 1.5
p.endValue = 7.9999
p.value = 'S2'
p.width = 2
p.xlabel = 'Time'
p.ylabel = 'Concentration'
p.title = 'Cell'

p.plotGraduatedArray() 