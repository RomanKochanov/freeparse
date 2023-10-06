import sys
from time import time
from jeanny3 import Collection, uuid

from freeparse import ET, ParsingTree

from unittests import runtest 

def do_test(XML,BUFFER):
    t = time()
    # parse XML file
    TMPFILE = '~.xml'
    with open(TMPFILE,'w') as f:
        f.write(XML)
    xmltree = ET.parse(TMPFILE)
    xmlroot = xmltree.getroot()
    # create parse tree from the XML node
    print('\n-----------------------------------')
    print('----- CREATING TREE ----------------')
    print('------------------------------------\n')
    parse_tree = ParsingTree.create_tree(xmlroot)
    parse_tree.print_tree(show_buffer=False)
    # get grammar and empty container structure
    print('\n-----------------------------------')
    print('----- CREATING GRAMMAR/DIAGRAM -----')
    print('------------------------------------\n')
    grammar = parse_tree.getGrammar()
    # create railroad diagram
    grammar.create_diagram("grammar.html",
        show_results_names=True,show_groups=True,vertical=3)
    # parse buffer
    print('\n-----------------------------------')
    print('----- SEARCHING STRING -------------')
    print('------------------------------------\n')
    res = grammar.parse_string(BUFFER)
    # print results
    print('------------------------------- parse result')
    print(res)
    print('------------------------------- input text')
    print(BUFFER)
    print('------------------------------- pyparsing grammar')
    print(grammar)
    print('------------------------------- buffer tree')
    parse_tree.print_tree(show_buffer=True)
    t = time()-t
    return t,Collection()

def test0():
    XML = """
<DICT>
    par1=<FLOAT name="par1"/><EOL/>
    par2=<FLOAT name="par2"/><EOL/>
    <LOOP name="mylist">
        <FLOAT/><EOL/>
        <DICT name="dicta">
            a1=<FLOAT name="a1"/> a2=<INT name="a2"/>
        </DICT><EOL/>
        <DICT name="dictb">
            b1=<FLOAT name="b1"/> b2=<INT name="b2"/>
        </DICT><EOL/>
    </LOOP>
</DICT>
"""
    BUFFER = """    
par1=1.0
par2=2.0E-10
15.0
a1=2.5 a2=900
b1=0.5 b2=0.000001
150.0
a1=20.0 a2=-1
b1=-0.5 b2=-300
"""
    return do_test(XML,BUFFER)

def test1():
    XML = """
<DICT>

    <DICT name="dict_outer">
        Fnorm= <FLOAT name="Fnorm"/> xi= <FLOAT name="xi"/> rms= <FLOAT name="rms"/><EOL/>        

        <LOOP name="inner_list">
            <DICT name="dict_inner">
                iter= <INT name="iter"/> Nfun= <INT name="Nfun"/> Jrank=<INT name="Jrank"/> scgrad= <FLOAT name="scgrad"/> scstep= <FLOAT name="scstep"/><EOL/>
            </DICT>
        </LOOP>

    </DICT>
    
</DICT>
"""
    BUFFER = """
Fnorm= 0.2262E+06 xi=    2.06 rms=    1.80
iter= 1 Nfun= 2 Jrank=144 scgrad=  0.2E+05 scstep=  0.4E-04
iter= 2 Nfun= 3 Jrank=144 scgrad=  0.6E+04 scstep=  0.1E-04
iter= 3 Nfun= 3 Jrank=144 scgrad=  0.6E+04 scstep=  0.1E-04
iter= 4 Nfun= 3 Jrank=144 scgrad=  0.6E+04 scstep=  0.1E-04
iter= 5 Nfun= 3 Jrank=144 scgrad=  0.6E+04 scstep=  0.1E-04
iter= 6 Nfun= 3 Jrank=144 scgrad=  0.6E+04 scstep=  0.1E-04
iter= 7 Nfun= 3 Jrank=144 scgrad=  0.6E+04 scstep=  0.1E-04
"""
    return do_test(XML,BUFFER)

def test1a():
    XML = """
<DICT>
    <DICT name="dict1">
        <LOOP name="inner_list">
            a=<INT/><EOL/>
            <DICT>
                iter= <INT name="iter"/> Nfun= <INT name="Nfun"/> Jrank=<INT name="Jrank"/> scgrad= <FLOAT name="scgrad"/> scstep= <FLOAT name="scstep"/><EOL/>
            </DICT>
        </LOOP>
    </DICT>
</DICT>
"""
    BUFFER = """
a=1000
iter= 1 Nfun= 2 Jrank=144 scgrad=  0.2E+05 scstep=  0.4E-04
a=2000
iter= 2 Nfun= 3 Jrank=144 scgrad=  0.6E+04 scstep=  0.1E-04
a=3000
iter= 3 Nfun= 3 Jrank=144 scgrad=  0.6E+04 scstep=  0.1E-04
"""
    return do_test(XML,BUFFER)

def test2():
    XML = """
<DICT>
SVD of dimensionless Fisher matrix:
scaling factor  <FLOAT name="sf"/>
number of the computed nonzero singular value <INT name="nsv"/>
number of the computed singular values that are larger than the underflow threshold <INT name="nsvt"/>
number of sweeps of Jacobi rotations needed for numerical convergence <INT name="nswee"/>
</DICT>
"""
    BUFFER = """
SVD of dimensionless Fisher matrix:
scaling factor  0.1E+01
number of the computed nonzero singular value 144
number of the computed singular values that are larger than the underflow threshold 144
number of sweeps of Jacobi rotations needed for numerical convergence      11
"""
    return do_test(XML,BUFFER)

def test3():
    XML = """<DICT>
    
<DICT name="part1">
SVD of dimensionless Fisher matrix:
scaling factor  <FLOAT name="sf"/>
number of the computed nonzero singular value <INT name="nsv"/>
number of the computed singular values that are larger than the underflow threshold <INT name="nsvt"/>
number of sweeps of Jacobi rotations needed for numerical convergence <INT name="nswee"/>
</DICT>

<DICT name="part2">
    <DICT name="dict1">
        Fnorm= <FLOAT name="Fnorm"/> xi= <FLOAT name="xi"/> rms= <FLOAT name="rms"/><EOL/>        
        <LOOP name="inner_list">
            <DICT>
                iter= <INT name="iter"/> Nfun= <INT name="Nfun"/> Jrank=<INT name="Jrank"/> scgrad= <FLOAT name="scgrad"/> scstep= <FLOAT name="scstep"/><EOL/>
            </DICT>
        </LOOP>
    </DICT>   
</DICT>

SVD: singular numbers:
<LOOP name="part3">
    <DICT>
        <INT name="id"/> <FLOAT name="val"/><EOL/>
    </DICT>
</LOOP>

<LOOP name="part4">
    <FLOAT/>
</LOOP>

<DICT name="part5">
conditional number of Fisher matrix  <FLOAT name="condfish"/>

SVD: right eigenvectors (V)
cumulative contribution of outputted Heff parms is <FLOAT name="cumd"/>
</DICT>

<LOOP name="part6">
    <DICT>
    singular number: <FLOAT name="singular_number"/>
    <LOOP name="inner">
        <DICT>
            <FLOAT name="v1"/> <STR name="v2"/> <FLOAT name="v3"/>
        </DICT>
    </LOOP>
    </DICT>
</LOOP>

<DICT name="part7">
sse                                  <FLOAT name="sse"/>
dimensionless standard deviation           <FLOAT name="chi2"/>
RMS(mK)                                    <FLOAT name="rms"/>

 Conditional number of the Jt*J matrix  <FLOAT name="cond"/>
</DICT>

                                   *** PARAMETERS  ***

    Name          Parameter             Estimate         Error    Sensit.   Est/Err Inflat.  Weight Tags  Gradient    Step
---------- R--M1-M2-M3-D--1--2--3--L--J- ---------------- --------  -------  -------- ------- ------- ----  --------    ----

<LOOP name="part8">
    <DICT>
        <STR name="par"/>
        <INT name="v1"/>  
        <INT name="v2"/>    
        <INT name="l2"/>    
        <INT name="v3"/>    
        <INT name="r"/>    
        <INT name="v1_"/>  
        <INT name="v2_"/>    
        <INT name="l2_"/>    
        <INT name="v3_"/>    
        <INT name="r_"/>    
        <FLOAT name="val"/>     
        <FLOAT name="x1"/> 
        <FLOAT name="x2"/>   
        <FLOAT name="x3"/> 
        <STR name="inflat"/> 
        <FLOAT name="wht"/>   
        <OPTIONAL><LITERAL name="tags" input="T"/></OPTIONAL>
        <FLOAT name="grad"/>        
        <FLOAT name="step"/>        
    </DICT><EOL/>
</LOOP>

                              *** LARGEST PAIR CORRELATIONS ***

<DICT name="part9">
correlation_output_threshold   <FLOAT name="corr_out_thresh"/>
</DICT>

<LOOP name="part10">
<DICT>
    <STR name='par1'/>       
    <INT name='x1'/>  
    <INT name='x2'/>  
    <INT name='x3'/>  
    <INT name='x4'/>  
    <INT name='x5'/>  
    <INT name='x6'/>  
    <INT name='x7'/>  
    <INT name='x8'/>  
    <INT name='x9'/>  
    <INT name='x10'/>  
    <STR name='par2'/>       
    <INT name='y1'/>  
    <INT name='y2'/>  
    <INT name='y3'/>  
    <INT name='y4'/>  
    <INT name='y5'/>  
    <INT name='y6'/>  
    <INT name='y7'/>  
    <INT name='y8'/>  
    <INT name='y9'/>  
    <INT name='y10'/>  
    <FLOAT name="val"/>
</DICT>
</LOOP>

                              *** LINE STATISTICS ***
<DICT name="part11">
Fmax input    <FLOAT name="Fmax"/>
Pmax input<STR name="Pmax"/>
</DICT>
tag
 ===
O - outlier
I - influental data point
C - point which has large affection on parameters of the model

 ref iso upper lower             Fobs       Fcalc  residual   unc  wht_res      --- upper -- --- lower ---                    Fobs            res.
                                (cm-1)      (cm-1)    (mK)    (mK)              p   j c   n   p   j c    n comment            (MHz)           (KHz)

<LOOP name="part12">
    <DICT>
        <INT name="tag"/>
        <INT name="ref"/>
        <INT name="iso"/>
        <STR name="upper"/>
        <STR name="lower"/>
        <WORD name="branch" input="PQR"/>
        <STR name="Je"/>
        <FLOAT name="Fobs"/>
        <FLOAT name="Fcalc"/>
        <FLOAT name="residual"/>
        <FLOAT name="unc"/>
        <FLOAT name="wht_res"/>
        <OPTIONAL><WORD name="flags" input="OIC"/></OPTIONAL>
        <INT name="p"/>
        <INT name="j"/>
        <INT name="c"/>
        <INT name="n"/>
        <INT name="p_"/>
        <INT name="j_"/>
        <INT name="c_"/>
        <INT name="n_"/>
        <RESTOFLINE name="comment"/>
    </DICT><EOL/>
</LOOP>

***** BAND STATISTICS *****
 iso          band        ref Nlin  Jm  JM  fm      fM       dfm        dfM       mean       rms      uncert

<LOOP name="part13">
    <DICT>
        <INT name="iso"/>
        <INT name="v1"/>
        <INT name="v2"/>
        <INT name="l2"/>
        <INT name="v3"/>
        <INT name="r"/>
        <INT name="v1_"/>
        <INT name="v2_"/>
        <INT name="l2_"/>
        <INT name="v3_"/>
        <INT name="r_"/>
        <INT name="ref"/>
        <INT name="Nlin"/>
        <INT name="Jmin"/>
        <INT name="Jmax"/>
        <FLOAT name="Fmin"/>
        <FLOAT name="Fmax"/>
        <FLOAT name="dFmin"/>
        <FLOAT name="dFmax"/>
        <FLOAT name="mean"/>
        <FLOAT name="rms"/>
        <FLOAT name="uncert"/>
    </DICT><EOL/>
</LOOP>

***** J STATISTICS *****

iso  J     N    mean_res         rms   rms/max_res   max_res

<LOOP name="part14">
    <DICT>
        <INT name="iso"/>
        <INT name="J"/>
        <INT name="N"/>
        <FLOAT name="mean_res"/>
        <FLOAT name="rms"/>
        <FLOAT name="rms_upon_max_res"/>
        <FLOAT name="max_res"/>
    </DICT><EOL/>
</LOOP>

***** SOURCE STATISTICS *****

src lines  jm  jM   mean_unc mean_res      rms

<LOOP name="part15">
    <DICT>
        <INT name="src"/>
        <INT name="lines"/>
        <INT name="jmin"/>
        <INT name="jmax"/>
        <FLOAT name="mean_unc"/>
        <FLOAT name="mean_res"/>  
        <FLOAT name="rms"/>
        <RESTOFLINE name="refs"/>                                                                                                                  
    </DICT><EOL/>
</LOOP>

***** ISOTOPS *****
 # name symm    mass1       mass2       mass3      lines  rms (mK)v1 v2 v3   j    f_min    f_max    e_max

<LOOP name="part16">
    <DICT>
        <INT name="i"/>
        <INT name="name"/>
        <INT name="symm"/>
        <FLOAT name="mass1"/>
        <FLOAT name="mass2"/>  
        <FLOAT name="mass3"/>
        <INT name="lines"/>
        <FLOAT name="rms"/>
        <INT name="v1"/>
        <INT name="v2"/>
        <INT name="v3"/>
        <INT name="j"/>
        <FLOAT name="f_min"/>
        <FLOAT name="f_max"/>
        <FLOAT name="e_max"/>
    </DICT><EOL/>
</LOOP>

<DICT name="total_stat">
total lines   <INT name="lines"/>

total data:    <INT name="data"/>

energy levels: <INT name="elevels"/>
outliers:        <INT name="outliers"/>
influentals:    <INT name="influentals"/>
cooks:            <INT name="cooks"/>
</DICT>

 Residual plot
 =============

<DICT name="cumul_plot">
    <!--<REGEX name="plot" input="Probability plot for normal distribution[\s\S]+Cumulative Probability"/>-->
    <TEXT name="plot" begin="Probability plot for normal distribution" end="Cumulative Probability"/>
</DICT>

</DICT>
"""
    BUFFER = """
SVD of dimensionless Fisher matrix:
scaling factor  0.1E+01
number of the computed nonzero singular value 144
number of the computed singular values that are larger than the underflow threshold 144
number of sweeps of Jacobi rotations needed for numerical convergence      11

Fnorm= 0.2262E+06 xi=    2.06 rms=    1.80
iter= 1 Nfun= 2 Jrank=144 scgrad=  0.2E+05 scstep=  0.4E-04
iter= 2 Nfun= 3 Jrank=144 scgrad=  0.6E+04 scstep=  0.1E-04
iter= 3 Nfun= 3 Jrank=144 scgrad=  0.6E+04 scstep=  0.1E-04
iter= 4 Nfun= 3 Jrank=144 scgrad=  0.6E+04 scstep=  0.1E-04
iter= 5 Nfun= 3 Jrank=144 scgrad=  0.6E+04 scstep=  0.1E-04
iter= 6 Nfun= 3 Jrank=144 scgrad=  0.6E+04 scstep=  0.1E-04
iter= 7 Nfun= 3 Jrank=144 scgrad=  0.6E+04 scstep=  0.1E-04

SVD: singular numbers:
   1  0.3396E+13
   2  0.8691E+12
   3  0.1147E+12
   4  0.2038E+11
   5  0.1277E+11
   6  0.2870E+10
   7  0.1786E+10
   8  0.1209E+10
   9  0.7080E+09
  0.3396E+13  0.8691E+12  0.1147E+12  0.2038E+11  0.1277E+11  0.2870E+10  0.1786E+10  0.1209E+10  0.7080E+09  0.5054E+09
  0.3768E+09  0.9393E+08  0.7875E+08  0.4759E+08  0.3299E+08  0.2602E+08  0.1281E+08  0.1013E+08  0.8242E+07  0.4962E+07
  0.4100E+07  0.2268E+07  0.1543E+07  0.1314E+07  0.1101E+07  0.8536E+06  0.4532E+06  0.3760E+06  0.2851E+06  0.2425E+06
  0.1629E+06  0.1279E+06  0.1001E+06  0.9929E+05  0.8406E+05  0.7847E+05  0.6989E+05  0.5685E+05  0.5419E+05  0.4919E+05

conditional number of Fisher matrix  0.9213E+13

SVD: right eigenvectors (V)
cumulative contribution of outputted Heff parms is  0.90


singular number:  0.3396E+13
             0.878  O3         2396.256880    
             0.068  O2         672.8359749    

singular number:  0.8691E+12
             0.647  O1         1353.674614    
             0.240  O2         672.8359749    
             0.113  O3         2396.256880    

singular number:  0.1147E+12
             0.526  O2         672.8359749    
             0.242  F=26.606  -26.60473481    
             0.222  O1         1353.674614    

singular number:  0.2038E+11
             0.966  B         0.3916319972    

singular number:  0.1277E+11
             0.712  F=26.606  -26.60473481    
             0.159  O2         672.8359749    
             0.075  O1         1353.674614    

singular number:  0.2870E+10
             0.274  X13       -19.12604455    
             0.213  X22        1.680785128    
             0.183  X12       -5.497292670    
             0.138  X23       -12.54333659    
             0.092  X11       -2.908999749    


sse                                  0.1102E+07
dimensionless standard deviation           4.54
RMS(mK)                                    1.83

 Conditional number of the Jt*J matrix  0.3288E+28

                                   *** PARAMETERS  ***

    Name          Parameter             Estimate         Error    Sensit.   Est/Err Inflat.  Weight Tags  Gradient    Step
---------- R--M1-M2-M3-D--1--2--3--L--J- ---------------- --------  -------  -------- ------- ------- ----  --------    ----
 O1        0  0  0  0  0  1  0  0  0  0   1353.674614     0.74E-03 0.94E-09   0.2E+07 ******* 0.55E-01   -0.12E+06  0.14E+04
 O2        0  0  0  0  0  0  1  0  0  0   672.8359749     0.39E-03 0.50E-09   0.2E+07 ******* 0.24E-01    0.11E+06  0.67E+03
 O3        0  0  0  0  0  0  0  1  0  0   2396.256880     0.25E-03 0.55E-09   0.1E+08 ******* 0.79E-03   -0.17E+06  0.24E+04
 Y2ll      0  0  0  0  0  0  1  0  1  0  0.1797463930E-01 0.66E-04 0.55E-08   0.3E+03 ******* 0.60E-02    0.48E+03  0.18E-01
 Y3ll      0  0  0  0  0  0  0  1  1  0  0.6115504738E-02 0.43E-04 0.85E-08   0.1E+03 656509. 0.65E-02   -0.69E+02  0.61E-02
 Z1112     0  0  0  0  0  3  1  0  0  0  0.1435569470E-02 0.72E-04 0.44E-10   0.2E+02 ******* 0.71E-01    0.61E+07  0.14E-02
 W11122    0  0  0  0  0  3  2  0  0  0 -0.4108335693E-05 0.94E-05 0.99E-11   0.4E+00 ******* 0.14E-03 T  0.17E+08 -0.41E-05
 W13333    0  0  0  0  0  1  0  4  0  0  0.4825897770E-04 0.40E-05 0.13E-09   0.1E+02 ******* 0.82E-04   -0.84E+06  0.48E-04
 W11333    0  0  0  0  0  2  0  3  0  0 -0.1676935506E-03 0.24E-04 0.70E-10   0.7E+01 ******* 0.65E-03   -0.12E+07 -0.17E-03
 W11133    0  0  0  0  0  3  0  2  0  0  0.8612975753E-04 0.24E-04 0.29E-10   0.4E+01 ******* 0.20E-02   -0.13E+07  0.86E-04
 W22333    0  0  0  0  0  0  2  3  0  0  0.3772486897E-05 0.11E-05 0.33E-10   0.3E+01 ******* 0.46E-04   -0.29E+07  0.38E-05
 W22233    0  0  0  0  0  0  3  2  0  0  0.6192668208E-05 0.15E-05 0.71E-11   0.4E+01 ******* 0.66E-06    0.31E+08  0.62E-05
 W12333    0  0  0  0  0  1  1  3  0  0  0.5298090416E-04 0.13E-04 0.11E-09   0.4E+01 ******* 0.27E-04   -0.19E+07  0.53E-04
 W12233    0  0  0  0  0  1  2  2  0  0 -0.6142495698E-05 0.13E-04 0.46E-10   0.5E+00 ******* 0.96E-05 T -0.28E+07 -0.61E-05
 W12223    0  0  0  0  0  1  3  1  0  0 -0.1678982044E-05 0.50E-05 0.11E-10   0.3E+00 ******* 0.15E-02 T  0.76E+07 -0.17E-05
 W11233    0  0  0  0  0  2  1  2  0  0  0.4135264157E-04 0.30E-04 0.68E-10   0.1E+01 ******* 0.16E-02    0.26E+07  0.41E-04

                              *** LARGEST PAIR CORRELATIONS ***

correlation_output_threshold   0.90

X13       0  0  0  0  0  1  0  1  0  0     O3        0  0  0  0  0  0  0  1  0  0   -0.946
Y111      0  0  0  0  0  3  0  0  0  0     X11       0  0  0  0  0  2  0  0  0  0   -0.949
Y123      0  0  0  0  0  1  1  1  0  0     X23       0  0  0  0  0  0  1  1  0  0   -0.908
Y133      0  0  0  0  0  1  0  2  0  0     X33       0  0  0  0  0  0  0  2  0  0   -0.932
Y222      0  0  0  0  0  0  3  0  0  0     O2        0  0  0  0  0  0  1  0  0  0    0.928
Y1ll      0  0  0  0  0  1  0  0  1  0     Y112      0  0  0  0  0  2  1  0  0  0    0.915

                              *** LINE STATISTICS ***

Fmax input    5000000.
Pmax input***
tag
 ===
O - outlier
I - influental data point
C - point which has large affection on parameters of the model

 ref iso upper lower             Fobs       Fcalc  residual   unc  wht_res      --- upper -- --- lower ---                    Fobs            res.
                                (cm-1)      (cm-1)    (mK)    (mK)              p   j c   n   p   j c    n comment            (MHz)           (KHz)
0   1   1 10011 00001 P   6e  3710.00467  3710.00469   -0.02    0.02   -0.93      5   5 1    9  0   6 1    1                 111223141.91     -511.38
0   1   1 10011 00001 P  12e  3705.00127  3705.00129   -0.02    0.02   -0.95      5  11 1    9  0  12 1    1                 111073143.81     -577.21
0   1   1 10011 00001 P  18e  3699.77319  3699.77320   -0.02    0.01   -1.25      5  17 1    9  0  18 1    1                 110916409.81     -501.80
0   1   1 10011 00001 P  20e  3697.98092  3697.98093   -0.02    0.02   -0.83      5  19 1    9  0  20 1    1                 110862678.84     -455.05
0   1   1 10011 00001 R   8e  3721.52153  3721.52154   -0.02    0.02   -0.82      5   9 1    9  0   8 1    1                 111568408.56     -467.91
0   1   1 10011 00001 R  14e  3725.73029  3725.73034   -0.04    0.04   -1.11      5  15 1    9  0  14 1    1                 111694584.29    -1217.50
0   1   1 10011 00001 R  16e  3727.08275  3727.08280   -0.05    0.02   -2.34      5  17 1    9  0  16 1    1                 111735129.97    -1381.77
0   1   1 10011 00001 R  22e  3730.98927  3730.98929   -0.02    0.01   -1.61      5  23 1    9  0  22 1    1                 111852244.29     -644.54
0   1   1 10011 00001 R  26e  3733.46837  3733.46839   -0.02    0.02   -1.04      5  27 1    9  0  26 1    1                 111926565.89     -720.11
0   2   1 00021 10011 P  11e   949.69886   949.69885    0.00    0.00    3.49  I   6  10 1   14  5  11 1    9                  28471255.43       69.86
0   2   1 00021 10011 P  13e   948.01291   948.01291    0.00    0.00    2.28  I   6  12 1   14  5  13 1    9                  28420712.03       45.65
0   2   1 00021 10011 P  15e   946.30299   946.30299    0.00    0.00    1.02  I   6  14 1   14  5  15 1    9                  28369449.94       20.44
0   2   1 00021 10011 P  17e   944.56907   944.56907   -0.00    0.00   -0.27  I   6  16 1   14  5  17 1    9                  28317468.37       -5.48
0   2   1 00021 10011 P  19e   942.81112   942.81112   -0.00    0.00   -1.56  I   6  18 1   14  5  19 1    9                  28264766.30      -31.12
0  95   1 50014 00001 R  36e  8853.26611  8853.26194    4.17    3.90    1.07     13  37 1   26  0  36 1    1                 
0  95   1 50014 00001 R  38e  8854.05211  8854.05156    0.56    3.90    0.14     13  39 1   26  0  38 1    1                 
0 104   1 00011 00001 R  60e  2384.99422  2384.99422    0.00    0.00    5.28 OIC  3  61 1    4  0  60 1    1                  71500327.99       42.26
0 108   1 10052 00001 P   2e 12670.69873 12670.69259    6.14   10.00    0.61     17   1 1   32  0   2 1    1                 
0 108   1 10052 00001 P   4e 12668.99873 12668.98593   12.81   10.00    1.28     17   3 1   58  0   4 1    1                 
0 165   1 60016 10002 R  22e  8611.66236  8611.65889    3.47    0.50    6.95  I  15  23 1   20  2  22 1    1 0               
0 165   1 60016 10002 R  24e  8613.13567  8613.13114    4.53    0.50    9.06 OI  15  25 1   20  2  24 1    1 0               
0 165   1 60016 10002 R  26e  8614.59154  8614.58626    5.28    0.50   10.56 OI  15  27 1   20  2  26 1    1 0               

***** BAND STATISTICS *****
 iso          band        ref Nlin  Jm  JM  fm      fM       dfm        dfM       mean       rms      uncert
   1  1 0 0 1 1  0 0 0 0 1   1   9   5  27  3698.0  3733.5  1.33E-05  3.67E-05 -2.401E-05  2.631E-05  3.561E-05
   1  0 0 0 2 1  1 0 0 1 1   2  35   5  45   917.7   983.5  6.67E-07  6.67E-07 -7.716E-08  2.781E-06  2.782E-06
   1  0 0 0 2 1  1 0 0 1 2   2  31   5  37  1027.3  1082.8  6.67E-07  6.67E-07 -6.503E-07  3.904E-06  3.958E-06
   1  0 0 0 1 1  1 0 0 0 1   3  50   3  54   910.0   992.5  1.03E-07  2.13E-07  1.683E-07  2.652E-07  3.141E-07
   1  0 0 0 1 1  1 0 0 0 2   3  49   1  50  1016.7  1093.9  1.20E-07  1.43E-07  1.847E-07  2.601E-07  3.190E-07
   1  0 0 0 2 1  1 0 0 1 1   4  40   3  45   917.7   984.5  5.34E-04  5.34E-04 -1.185E-05  7.731E-05  7.821E-05
   1  0 0 0 2 1  1 0 0 1 2   4  37   4  45  1019.0  1084.9  5.34E-04  5.34E-04  9.188E-06  5.221E-05  5.302E-05

***** J STATISTICS *****

iso  J     N    mean_res         rms   rms/max_res   max_res

 1   0    25      -78.60     2469.04      -31.41    -4930.28
 1   1   522      248.45     4771.48       19.21    96321.22
 1   2   463       42.30     2163.36       51.15   -11314.44
 1   3   896     -152.31     5021.01      -32.97  -136955.82
 1   4   617       27.13     2192.98       80.84   -15300.82

***** SOURCE STATISTICS *****

src lines  jm  jM   mean_unc mean_res      rms
  1     9   5  27     0.020    -0.024     0.026 Groh JMS 146 161 (1991)                                                                                                                     
  2    66   5  45     0.001    -0.000     0.003 Chou JMS 172 233 (1995)                                                                                                                     
  3    99   1  54     0.000     0.000     0.000 Bradley IEEE QE-22 234(1986)                                                                                                                
  4    93   3  45     0.534     0.089     0.232 Siemsen OptComm 22 11 (1977)                                                                                                                

***** ISOTOPS *****
 # name symm    mass1       mass2       mass3      lines  rms (mK)v1 v2 v3   j    f_min    f_max    e_max
 1  626    4  0.00000000  0.00000000  0.00000000  53713      1.83  5 12 12 177    562.1  14075.3  26800.3

total lines   63549

total data:    53713

energy levels: 10264
outliers:        620
influentals:    4342
cooks:            12

 Residual plot
 =============


              Probability plot for normal distribution

     4.00E+02 +:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::.
              .                                                           .
              .                                                           .
              .                                                           .
              .                                                           .
     3.20E+02 +                                                           .
              .                                                           .
              .                                                           .
              .                                                           .
              .                                                           .
     2.40E+02 +                                                           *
              .                                                         * .
              .                                                           .
              .                                                           .
              .                                                        ** .
     1.60E+02 +                                                           .
              .                                                        *  .
              .                                                           .
              .                                                       *   .
 O            .                                                      **   .
 b   8.00E+01 +                                                      *    .
 s            .                                                           .
 e            .                                                    ***    .
 r            .                                                   **      .
 v            .                                               *****       .
 a   0.00E+00 +------------************************************-----------.
 t            .      *******                                              .
 i            .     **                                                    .
 o            .     *                                                     .
 n            .    **                                                     .
 s  -8.00E+01 +    *                                                      .
              .    *                                                      .
              .    *                                                      .
              .   **                                                      .
              .   *                                                       .
    -1.60E+02 +  *                                                        .
              .  *                                                        .
              .                                                           .
              . *                                                         .
              .                                                           .
    -2.40E+02 +                                                           .
              .                                                           .
              .                                                           .
              .                                                           .
              .                                                           .
    -3.20E+02 +                                                           .
              . *                                                         .
              .                                                           .
              *                                                           .
              .                                                           .
    -4.00E+02 +::::::::::::+::::+::+:::+::::+::::+:::+::+::::+::::::::::::.
                           .01  .05.10 .25  .50  .75 .90.95  .99           

              Cumulative Probability

"""
    return do_test(XML,BUFFER)

def test4():
    XML = """
<DICT>

    <DICT name="dict_outer">
        Fnorm= <FLOAT name="Fnorm"/> xi= <FLOAT name="xi"/> <OPTIONAL>rms= <FLOAT name="rms"/></OPTIONAL>
        a=<FLOAT name="a"/> <OPTIONAL>b= <FLOAT name="b"/></OPTIONAL>

        <LOOP name="inner_list">
            <DICT name="dict_inner">
                iter= <INT name="iter"/> Nfun= <INT name="Nfun"/> <OPTIONAL>Jrank=<INT name="Jrank"/></OPTIONAL> scgrad= <FLOAT name="scgrad"/> scstep= <FLOAT name="scstep"/><EOL/>
            </DICT>
        </LOOP>

    </DICT>
    
</DICT>
"""
    BUFFER = """
Fnorm= 0.2262E+06 xi=    2.06 rms=    1.80
a=1 b=2
iter= 1 Nfun= 2 Jrank=144 scgrad=  0.2E+05 scstep=  0.4E-04
iter= 2 Nfun= 3           scgrad=  0.6E+04 scstep=  0.1E-04
"""
    return do_test(XML,BUFFER)

def test5():
    XML = """
<DICT>
    
<DICT name="part7">
sse                                  <FLOAT name="sse"/>
dimensionless standard deviation           <FLOAT name="chi2"/>
RMS(mK)                                    <FLOAT name="rms"/>

 Conditional number of the Jt*J matrix  <FLOAT name="cond"/>
</DICT>

                                   *** PARAMETERS  ***

    Name          Parameter             Estimate         Error    Sensit.   Est/Err Inflat.  Weight Tags  Gradient    Step
---------- R--M1-M2-M3-D--1--2--3--L--J- ---------------- --------  -------  -------- ------- ------- ----  --------    ----

<LOOP name="part8">
    <DICT>
        <STR name="par"/>
        <INT name="v1"/>  
        <INT name="v2"/>    
        <INT name="l2"/>    
        <INT name="v3"/>    
        <INT name="r"/>    
        <INT name="v1_"/>  
        <INT name="v2_"/>    
        <INT name="l2_"/>    
        <INT name="v3_"/>    
        <INT name="r_"/>    
        <FLOAT name="val"/>     
        <FLOAT name="x1"/> 
        <FLOAT name="x2"/>   
        <FLOAT name="x3"/> 
        <STR name="inflat"/> 
        <FLOAT name="wht"/>   
        <OPTIONAL><LITERAL name="f1" input="T"/></OPTIONAL>
        <OPTIONAL><LITERAL name="f2" input="C"/></OPTIONAL>
        <FLOAT name="grad"/>        
        <FLOAT name="step"/>        
    </DICT><EOL/>
</LOOP>

</DICT>
"""
    BUFFER = """

sse                                  0.1102E+07
dimensionless standard deviation           4.54
RMS(mK)                                    1.83

 Conditional number of the Jt*J matrix  0.3288E+28

                                   *** PARAMETERS  ***

    Name          Parameter             Estimate         Error    Sensit.   Est/Err Inflat.  Weight Tags  Gradient    Step
---------- R--M1-M2-M3-D--1--2--3--L--J- ---------------- --------  -------  -------- ------- ------- ----  --------    ----
 O1        0  0  0  0  0  1  0  0  0  0   1353.674614     0.74E-03 0.94E-09   0.2E+07 ******* 0.55E-01   -0.12E+06  0.14E+04
 O2        0  0  0  0  0  0  1  0  0  0   672.8359749     0.39E-03 0.50E-09   0.2E+07 ******* 0.24E-01    0.11E+06  0.67E+03
 O3        0  0  0  0  0  0  0  1  0  0   2396.256880     0.25E-03 0.55E-09   0.1E+08 ******* 0.79E-03   -0.17E+06  0.24E+04
 Y2ll      0  0  0  0  0  0  1  0  1  0  0.1797463930E-01 0.66E-04 0.55E-08   0.3E+03 ******* 0.60E-02    0.48E+03  0.18E-01
 Y3ll      0  0  0  0  0  0  0  1  1  0  0.6115504738E-02 0.43E-04 0.85E-08   0.1E+03 656509. 0.65E-02   -0.69E+02  0.61E-02
 Z1112     0  0  0  0  0  3  1  0  0  0  0.1435569470E-02 0.72E-04 0.44E-10   0.2E+02 ******* 0.71E-01    0.61E+07  0.14E-02
 W11122    0  0  0  0  0  3  2  0  0  0 -0.4108335693E-05 0.94E-05 0.99E-11   0.4E+00 ******* 0.14E-03 TC 0.17E+08 -0.41E-05
 W13333    0  0  0  0  0  1  0  4  0  0  0.4825897770E-04 0.40E-05 0.13E-09   0.1E+02 ******* 0.82E-04   -0.84E+06  0.48E-04
 W11333    0  0  0  0  0  2  0  3  0  0 -0.1676935506E-03 0.24E-04 0.70E-10   0.7E+01 ******* 0.65E-03   -0.12E+07 -0.17E-03
 W11133    0  0  0  0  0  3  0  2  0  0  0.8612975753E-04 0.24E-04 0.29E-10   0.4E+01 ******* 0.20E-02   -0.13E+07  0.86E-04
 W22333    0  0  0  0  0  0  2  3  0  0  0.3772486897E-05 0.11E-05 0.33E-10   0.3E+01 ******* 0.46E-04   -0.29E+07  0.38E-05
 W22233    0  0  0  0  0  0  3  2  0  0  0.6192668208E-05 0.15E-05 0.71E-11   0.4E+01 ******* 0.66E-06    0.31E+08  0.62E-05
 W12333    0  0  0  0  0  1  1  3  0  0  0.5298090416E-04 0.13E-04 0.11E-09   0.4E+01 ******* 0.27E-04   -0.19E+07  0.53E-04
 W12233    0  0  0  0  0  1  2  2  0  0 -0.6142495698E-05 0.13E-04 0.46E-10   0.5E+00 ******* 0.96E-05 T -0.28E+07 -0.61E-05
 W12223    0  0  0  0  0  1  3  1  0  0 -0.1678982044E-05 0.50E-05 0.11E-10   0.3E+00 ******* 0.15E-02 T  0.76E+07 -0.17E-05
 W11233    0  0  0  0  0  2  1  2  0  0  0.4135264157E-04 0.30E-04 0.68E-10   0.1E+01 ******* 0.16E-02    0.26E+07  0.41E-04


"""
    return do_test(XML,BUFFER)

def test6():
    XML = """
<DICT>

 Residual plot
 =============

<DICT name="cumul_plot">
    <REGEX name="plot" input="Probability plot for normal distribution[\s\S]+Cumulative Probability"/>
</DICT>    

</DICT>
"""
    BUFFER = """
    
 Residual plot
 =============


              Probability plot for normal distribution

     4.00E+02 +:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::.
              .                                                           .
              .                                                           .
              .                                                           .
              .                                                           .
     3.20E+02 +                                                           .
              .                                                           .
              .                                                           .
              .                                                           .
              .                                                           .
     2.40E+02 +                                                           *
              .                                                         * .
              .                                                           .
              .                                                           .
              .                                                        ** .
     1.60E+02 +                                                           .
              .                                                        *  .
              .                                                           .
              .                                                       *   .
 O            .                                                      **   .
 b   8.00E+01 +                                                      *    .
 s            .                                                           .
 e            .                                                    ***    .
 r            .                                                   **      .
 v            .                                               *****       .
 a   0.00E+00 +------------************************************-----------.
 t            .      *******                                              .
 i            .     **                                                    .
 o            .     *                                                     .
 n            .    **                                                     .
 s  -8.00E+01 +    *                                                      .
              .    *                                                      .
              .    *                                                      .
              .   **                                                      .
              .   *                                                       .
    -1.60E+02 +  *                                                        .
              .  *                                                        .
              .                                                           .
              . *                                                         .
              .                                                           .
    -2.40E+02 +                                                           .
              .                                                           .
              .                                                           .
              .                                                           .
              .                                                           .
    -3.20E+02 +                                                           .
              . *                                                         .
              .                                                           .
              *                                                           .
              .                                                           .
    -4.00E+02 +::::::::::::+::::+::+:::+::::+::::+:::+::+::::+::::::::::::.
                           .01  .05.10 .25  .50  .75 .90.95  .99           

              Cumulative Probability

"""
    return do_test(XML,BUFFER)

def test7():
    XML = """<DICT>

    Name          Parameter             Estimate         Error    Sensit.   Est/Err Inflat.  Weight Tags  Gradient    Step
---------- R--M1-M2-M3-D--1--2--3--L--J- ---------------- --------  -------  -------- ------- ------- ----  --------    ----

<FIXCOL name="WTF">
//HEADER
0 name STR
1 R INT
2 M1 INT
3 M2 INT
4 M3 INT
5 D INT
6 a1 INT
7 a2 INT
8 a3 INT
9 L INT
A J FLOAT
B estimate FLOAT
C error FLOAT
D sensit FLOAT
E est_err FLOAT
F inflat STR
G weight FLOAT
H tags STR
I gradient FLOAT
J step FLOAT

//DATA
0_________1_2__3__4__5__6__7__8__9__A__B_________________C________D________E_________F_______G________H__I_________J________
<!--
    Name          Parameter             Estimate         Error    Sensit.   Est/Err Inflat.  Weight Tags  Gradient    Step
           R M1 M2 M3  D  1  2  3  L  J
 O1        0  0  0  0  0  1  0  0  0  0   1353.674539     0.35E-03 0.42E-09   0.4E+07 ******* 0.55E-01   -0.57E+06  0.14E+04
 Z1112     0  0  0  0  0  3  1  0  0  0  0.1444336305E-02 0.33E-04 0.20E-10   0.4E+02 ******* 0.71E-01   -0.42E+07  0.14E-02
 W11122    0  0  0  0  0  3  2  0  0  0 -0.1701685787E-05 0.43E-05 0.45E-11   0.4E+00 ******* 0.60E-04 T  0.85E+07 -0.17E-05
-->
</FIXCOL>

</DICT>
"""
    BUFFER = """

    Name          Parameter             Estimate         Error    Sensit.   Est/Err Inflat.  Weight Tags  Gradient    Step
---------- R--M1-M2-M3-D--1--2--3--L--J- ---------------- --------  -------  -------- ------- ------- ----  --------    ----
 O1        0  0  0  0  0  1  0  0  0  0   1353.674614     0.74E-03 0.94E-09   0.2E+07 ******* 0.55E-01   -0.12E+06  0.14E+04
 O2        0  0  0  0  0  0  1  0  0  0   672.8359749     0.39E-03 0.50E-09   0.2E+07 ******* 0.24E-01    0.11E+06  0.67E+03
 O3        0  0  0  0  0  0  0  1  0  0   2396.256880     0.25E-03 0.55E-09   0.1E+08 ******* 0.79E-03   -0.17E+06  0.24E+04
 X11       0  0  0  0  0  2  0  0  0  0  -2.908999749     0.43E-03 0.33E-09   0.7E+04 ******* 0.11E+00    0.13E+06 -0.29E+01
 X12       0  0  0  0  0  1  1  0  0  0  -5.497292670     0.40E-03 0.43E-09   0.1E+05 ******* 0.18E+00    0.44E+06 -0.55E+01
 X13       0  0  0  0  0  1  0  1  0  0  -19.12604455     0.66E-03 0.82E-09   0.3E+05 ******* 0.24E-01   -0.40E+06 -0.19E+02
 X22       0  0  0  0  0  0  2  0  0  0   1.680785128     0.84E-04 0.11E-09   0.2E+05 ******* 0.16E-02   -0.54E+06  0.17E+01
 X23       0  0  0  0  0  0  1  1  0  0  -12.54333659     0.15E-03 0.60E-09   0.8E+05 ******* 0.31E-01    0.35E+05 -0.13E+02
 X33       0  0  0  0  0  0  0  2  0  0  -12.52856465     0.14E-03 0.27E-09   0.9E+05 ******* 0.82E-02   -0.15E+06 -0.13E+02
 Z3333     0  0  0  0  0  0  0  4  0  0  0.1565034608E-03 0.18E-05 0.11E-09   0.9E+02 ******* 0.13E-04   -0.12E+05  0.16E-03
 W12222    0  0  0  0  0  1  4  0  0  0 -0.1474469486E-05 0.89E-06 0.15E-11   0.2E+01 ******* 0.39E-03    0.15E+08 -0.15E-05
 W11222    0  0  0  0  0  2  3  0  0  0  0.6058590368E-05 0.38E-05 0.62E-11   0.2E+01 ******* 0.26E-02   -0.10E+08  0.61E-05
 W11122    0  0  0  0  0  3  2  0  0  0 -0.4108335693E-05 0.94E-05 0.99E-11   0.4E+00 ******* 0.14E-03 T  0.17E+08 -0.41E-05
 W13333    0  0  0  0  0  1  0  4  0  0  0.4825897770E-04 0.40E-05 0.13E-09   0.1E+02 ******* 0.82E-04   -0.84E+06  0.48E-04
 W11333    0  0  0  0  0  2  0  3  0  0 -0.1676935506E-03 0.24E-04 0.70E-10   0.7E+01 ******* 0.65E-03   -0.12E+07 -0.17E-03
 W11133    0  0  0  0  0  3  0  2  0  0  0.8612975753E-04 0.24E-04 0.29E-10   0.4E+01 ******* 0.20E-02   -0.13E+07  0.86E-04
 W22333    0  0  0  0  0  0  2  3  0  0  0.3772486897E-05 0.11E-05 0.33E-10   0.3E+01 ******* 0.46E-04   -0.29E+07  0.38E-05
 W22233    0  0  0  0  0  0  3  2  0  0  0.6192668208E-05 0.15E-05 0.71E-11   0.4E+01 ******* 0.66E-06    0.31E+08  0.62E-05
 W12333    0  0  0  0  0  1  1  3  0  0  0.5298090416E-04 0.13E-04 0.11E-09   0.4E+01 ******* 0.27E-04   -0.19E+07  0.53E-04
 W12233    0  0  0  0  0  1  2  2  0  0 -0.6142495698E-05 0.13E-04 0.46E-10   0.5E+00 ******* 0.96E-05 T -0.28E+07 -0.61E-05
 W12223    0  0  0  0  0  1  3  1  0  0 -0.1678982044E-05 0.50E-05 0.11E-10   0.3E+00 ******* 0.15E-02 T  0.76E+07 -0.17E-05
 W11233    0  0  0  0  0  2  1  2  0  0  0.4135264157E-04 0.30E-04 0.68E-10   0.1E+01 ******* 0.16E-02    0.26E+07  0.41E-04
 W11223    0  0  0  0  0  2  2  1  0  0 -0.9151101008E-05 0.17E-04 0.30E-10   0.5E+00 ******* 0.18E-03 T  0.65E+06 -0.92E-05
 W11123    0  0  0  0  0  3  1  1  0  0 -0.3101785865E-04 0.27E-04 0.28E-10   0.1E+01 ******* 0.32E-02    0.12E+08 -0.31E-04
 W22222    0  0  0  0  0  0  5  0  0  0 -0.8897081454E-08 0.11E-06 0.13E-12   0.8E-01 ******* 0.35E-02 T -0.16E+10 -0.89E-08

"""
    return do_test(XML,BUFFER)

TEST_CASES = [
    test0,
    test1,
    test1a,
    test2,
    test4,
    test3,
    test5,
    test6,
    test7,
]

def do_tests(TEST_CASES,testgroup=None,session_name=None): # test all functions    

    if testgroup is None:
        testgroup = __file__

    session_uuid = uuid()
    
    for test_fun in TEST_CASES:        
        runtest(test_fun,testgroup,session_name,session_uuid,save=True)
        
if __name__=='__main__':
    
    try:
        session_name = sys.argv[1]
    except IndexError:
        session_name = '__not_supplied__'
        
    do_tests(TEST_CASES,session_name=session_name)
    
