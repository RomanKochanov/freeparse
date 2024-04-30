import os
import sys
import json

import argparse

from time import time
from jeanny3 import Collection, uuid

from freeparse import ET, ParsingTree, VARSPACE

from unittests import runtest 

def do_test1(XML,BUFFER):
    """ simple tests without back-loop """
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
    #grammar.create_diagram("grammar.html",
    #    show_results_names=True,show_groups=True,vertical=3)
    # parse buffer
    print('\n-----------------------------------')
    print('----- SEARCHING STRING -------------')
    print('------------------------------------\n')
    res = grammar.parse_string(BUFFER,parse_all=VARSPACE['parse_all'])
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

def do_test2(XML,BUFFER):
    """ tests with back-loop, i.e. with comparing re-parsed data structure
    form re-generated war file with the original input datastructure """
    t = time()
    ##############################################################
    # 1ST STEP - PARSE DATA STRUCTURE FROM THE ORIGINAL RAW FILE.
    ##############################################################
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
    #grammar.create_diagram("grammar.html",
    #    show_results_names=True,show_groups=True,vertical=3)
    # parse buffer
    print('\n-----------------------------------')
    print('----- SEARCHING STRING -------------')
    print('------------------------------------\n')
    #res = grammar.parseString(BUFFER,parse_all=VARSPACE['parse_all'])
    res = grammar.parseString(BUFFER)
    # print results
    print('------------------------------- parse result')
    print(res)
    print('------------------------------- input text')
    print(BUFFER)
    print('------------------------------- pyparsing grammar')
    print(grammar)
    print('------------------------------- buffer tree')
    parse_tree.print_tree(show_buffer=True)
    print('\n-----------------------------------')
    print('----- SAVING TO JSON ---------------')
    print('------------------------------------\n')
    data = parse_tree.get_data()
    outfile = '~data1.json'
    with open(outfile,'w') as f:
        f.write(json.dumps(data,indent=2))
    print('1st stage data saved to',outfile)
    print('\n-----------------------------------')
    print('----- SAVING BUFFER ----------------')
    print('------------------------------------\n')
    filebuf = 'buffer1.txt'
    with open(filebuf,'w') as f:
        f.write(BUFFER)
    print('1st stage buffer saved to',filebuf)
    ##############################################################
    # 2ND STEP - GENERATE NEW RAW FILE FROM THE DATA STRUCTURE,
    # PARSE IT AGAIN AND COMPARE THE RESULTING DATA STRUCTURE 
    # WITH THE ORIGINAL ONE.
    ##############################################################
    # Import data from file.
    with open(outfile) as f:
        data = json.load(f)
    # Generate new raw file from it.
    rawbuf = parse_tree.generate(data)
    print('\n-----------------------------------')
    print('----- SAVING NEW BUFFER ------------')
    print('------------------------------------\n')
    filebuf = 'buffer2.txt'
    with open(filebuf,'w') as f:
        f.write(rawbuf)
    print('1st stage buffer saved to',filebuf)
    print('\n-----------------------------------')
    print('----- GENERATING NEW DATA-----------')
    print('------------------------------------\n')
    print(rawbuf)
    print('------------------------------------\n')
    # Parse the newly generated raw file.
    #parse_tree = ParsingTree.create_tree(xmlroot)
    parse_tree.parse_string(rawbuf,parse_all=VARSPACE['parse_all'])
    data_ = parse_tree.get_data()
    #print('DATA')
    #print(data_)
    # Save data structure to different file.
    outfile_ = '~data2.json'
    with open(outfile_,'w') as f:
        f.write(json.dumps(data_,indent=2))
    print('2st stage data saved to',outfile_)
    # Compare two data structures and 
    data_compare_flag = data==data_
    print('\n-----------------------------------')
    print('----- DATA #1 ----------------------')
    print('------------------------------------\n')
    print(json.dumps(data,indent=3))
    print('\n-----------------------------------')
    print('----- DATA #2 ----------------------')
    print('------------------------------------\n')
    print(json.dumps(data_,indent=3))
    print('\n-----------------------------------')
    print('----- BACK-LOOP COMPARISON ---------')
    print('------------------------------------\n')
    print('data_compare_flag=',data_compare_flag)
    if not data_compare_flag:
        print('ERROR: DATA STRUCTURES ARE NOT SAME, CHECK %s, %s'%(outfile,outfile_))
    # Create a summary collection.
    col = Collection()
    col.update([{'data_compare_flag':data_compare_flag}])
    ##################
    # RETURN RESULTS
    ##################
    t = time()-t
    return t,col

#do_test = do_test1
do_test = do_test2

def test_stub():
    XML = """
<DICT>



</DICT>
"""
    BUFFER = """
    
"""
    return do_test(XML,BUFFER)

def test_part0a():
    XML = """
<DICT>

inputted lines:

<EOL2/>

<LOOP name="part0a">
    <DICT>
        <INT name="i" format="%2d"/>
        <WORD name="flag" input="TF" format="%2s"/> 
        <INT name="n" format="%7d"/>
    </DICT> <EOL/>
</LOOP>

<EOL5/>

*** LEAST SQUARES ITERATIONS***

</DICT>
"""
    BUFFER = """inputted lines:

 0 F  53713
 1 T      0
 2 T      0
 3 T      0
 4 T      0
 5 T      0
 6 T      0
 7 T      0
 8 T      0
 9 T      0





*** LEAST SQUARES ITERATIONS***
"""
    return do_test(XML,BUFFER)

def test_loop():
    XML = """
<DICT>

*** LEAST SQUARES ITERATIONS***

<EOL2/>

<LOOP name="part0b">
    <DICT>Fnorm= 
        <FLOAT name="Fnorm"/> xi= 
        <FLOAT name="xi"/> rms= 
        <FLOAT name="rms"/>         
        <OPTIONAL> mu= 
            <FLOAT name="mu"/> size= 
            <FLOAT name="size"/>
        </OPTIONAL>         
        <EOL/>        
    </DICT>AAA 
    
    <EOL/>
    
</LOOP>BBB

</DICT>
"""
    BUFFER = """*** LEAST SQUARES ITERATIONS***

BBB
"""
#    BUFFER = """*** LEAST SQUARES ITERATIONS***
#
#Fnorm= 0.1102E+07 xi=    4.54 rms=    1.83
#AAA
#Fnorm= 0.1102E+07 xi=    4.54 rms=    1.83 mu=  0.1E+02 size=  0.3E-03
#AAA
#BBB
#"""
    return do_test(XML,BUFFER)
    
def test_part0b():
    XML = """
<DICT>

*** LEAST SQUARES ITERATIONS***

<EOL4/>

<LOOP name="part0b">
    <DICT>Fnorm=
        <FLOAT name="Fnorm" format="%11.4E"/> xi=
        <FLOAT name="xi" format="%8.2f"/> rms=
        <FLOAT name="rms" format="%8.2f"/> 
        
        <OPTIONAL> mu=
            <FLOAT name="mu" format="%9.1E"/> size=
            <FLOAT name="size" format="%9.1E"/>
        </OPTIONAL> 
        
        <EOL/>
        
        <LOOP name="inner_list">
            <DICT name="dict_inner">iter=
                <INT name="iter" format="%2d"/> Nfun=
                <INT name="Nfun" format="%2d"/> Jrank=
                <INT name="Jrank" format="%3d"/> scgrad=
                <FLOAT name="scgrad" format="%9.1E"/> scstep=
                <FLOAT name="scstep" format="%9.1E"/> 
            </DICT> 
            
            <EOL/>
        </LOOP>
    </DICT>
</LOOP>

</DICT>
"""
    BUFFER = """*** LEAST SQUARES ITERATIONS***



Fnorm= 0.1102E+07 xi=    4.54 rms=    1.83
iter= 1 Nfun= 2 Jrank=144 scgrad=  0.4E+03 scstep=  0.6E-08
Fnorm= 0.1102E+07 xi=    4.54 rms=    1.83 mu=  0.1E+02 size=  0.3E-03
"""
    return do_test(XML,BUFFER)

def test_part1():
    XML = """
<DICT>

<DICT name="part1">
SVD of dimensionless Fisher matrix:<EOL/>
scaling factor<FLOAT name="sf" format="%9.1E"/><EOL/>
number of the computed nonzero singular value<INT name="nsv" format="%4d"/><EOL/>
number of the computed singular values that are larger than the underflow threshold<INT name="nsvt" format="%4d"/><EOL/>
number of sweeps of Jacobi rotations needed for numerical convergence<INT name="nswee" format="%8d"/><EOL/>
</DICT>

</DICT>
"""
    BUFFER = """SVD of dimensionless Fisher matrix:
scaling factor  0.1E+01
number of the computed nonzero singular value 144
number of the computed singular values that are larger than the underflow threshold 144
number of sweeps of Jacobi rotations needed for numerical convergence      11
"""
    return do_test(XML,BUFFER)

# FOUND ELUSIVE BUG IN RECORING DATA WHILE PARSING!!! USE DEBUG
# ATTENTION!!! VERY IMPORTANT:
# PUT <EOL/> TAG INSIDE(!!!!) DICTIONARY, NOT OUTSIDE!
# WHEN PUTTING OUTSIDE, IT CAN RECORD ADDITIONAL LINE FROM DIFFERENT BLOCK!!!
# THIS IS BECAUSE THE PARSING TRIGGERS ARE CALLED WHEN CONTAINER IS ALL DONE.
# PUTTING MORE THINGS INSIDE CONTAINER (E.G. IN DICT) MAKES IT LESS PROBABLE
# TO FAIL AT THE END OF THE LOOP
def test_part34():
    XML = """
<DICT>

SVD: singular numbers: <EOL/>
<LOOP name="part3">
    <DICT>
        <INT name="id" format="%4d"/> 
        <FLOAT name="val" format="%12.4E"/> 
        <EOL/>
    </DICT> 
</LOOP>

<LOOP name="part4">
    <FLOAT format="%12.4E"/> <OPTIONAL><EOL/></OPTIONAL>
</LOOP>

</DICT>
"""
    BUFFER = """SVD: singular numbers:
   1  0.3396E+13
   2  0.8691E+12
  0.3396E+13  0.8691E+12  0.1147E+12  0.2038E+11  
  0.3768E+09  0.9393E+08  
"""
    return do_test(XML,BUFFER)

def test_fixcol():
    XML = """
<DICT>

THIS IS A HEADER

<EOL/>

<FIXCOL name="myloop">
//HEADER
0 v1 float
1 v2 str
2 v3 float

//DATA
0_________________1__________2________________
<!--
             0.107  -D1      -0.1724582096E-09
             0.104  Cj_5     -0.4401774466E-07
             0.065  Z1112     0.1435569470E-02
-->
</FIXCOL>

</DICT>
"""
    BUFFER = """THIS IS A HEADER
             0.107  -D1      -0.1724582096E-09
             0.104  Cj_5     -0.4401774466E-07
             0.065  Z1112     0.1435569470E-02
"""
    return do_test(XML,BUFFER)

def test_part56():
    XML = """
<DICT>

<DICT name="part5">
conditional number of Fisher matrix<FLOAT name="condfish" format="%12.4E"/><EOL/>
<EOL/>
SVD: right eigenvectors (V)<EOL/>
cumulative contribution of outputted Heff parms is<FLOAT name="cumd" format="%6.2f"/>
</DICT>

<EOL3/>

<LOOP name="part6">
<DICT>
singular number:<FLOAT name="singular_number" format="%12.4E"/><EOL/>
<FIXCOL name="inner">
//HEADER
0 v1 float
1 v2 str
2 v3 float

//DATA
0_________________1__________2________________
<!--
             0.107  -D1      -0.1724582096E-09
             0.104  Cj_5     -0.4401774466E-07
             0.065  Z1112     0.1435569470E-02
-->
</FIXCOL>
</DICT> <EOL/>
</LOOP>

</DICT>
"""
    BUFFER = """conditional number of Fisher matrix  0.9213E+13

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

"""
    return do_test(XML,BUFFER)

def test_part78():
    XML = """
<DICT>

                         **** FIT SUMMARY ****
<EOL2/>

<DICT name="part7">
sse                                  <FLOAT name="sse" format="%10.4E"/> <EOL/>
dimensionless standard deviation           <FLOAT name="chi2" format="%4.2f"/> <EOL/>
RMS(mK)                                    <FLOAT name="rms" format="%4.2f"/> <EOL/>
<EOL/>
 Conditional number of the Jt*J matrix  <FLOAT name="cond" format="%12.4E"/>
</DICT>

<EOL2/>

                                   *** PARAMETERS  ***

    Name          Parameter             Estimate         Error    Sensit.   Est/Err Inflat.  Weight Tags  Gradient    Step
---------- R--M1-M2-M3-D--1--2--3--L--J- ---------------- --------  -------  -------- ------- ------- ----  --------    ----

<EOL/>

<FIXCOL name="part8">
//HEADER
0 name STR
1 R INT
2 M1 INT
3 M2 INT
4 M3 INT
5 D INT
6 A1 INT
7 A2 INT
8 A3 INT
9 L INT
A J INT
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
    BUFFER = """                         **** FIT SUMMARY ****

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
 X11       0  0  0  0  0  2  0  0  0  0  -2.908999749     0.43E-03 0.33E-09   0.7E+04 ******* 0.11E+00    0.13E+06 -0.29E+01
 X12       0  0  0  0  0  1  1  0  0  0  -5.497292670     0.40E-03 0.43E-09   0.1E+05 ******* 0.18E+00    0.44E+06 -0.55E+01
 X13       0  0  0  0  0  1  0  1  0  0  -19.12604455     0.66E-03 0.82E-09   0.3E+05 ******* 0.24E-01   -0.40E+06 -0.19E+02
 X22       0  0  0  0  0  0  2  0  0  0   1.680785128     0.84E-04 0.11E-09   0.2E+05 ******* 0.16E-02   -0.54E+06  0.17E+01
"""
    return do_test(XML,BUFFER)

def test_part910():
    XML = """
<DICT>

                              *** LARGEST PAIR CORRELATIONS ***
<EOL2/>

<DICT name="part9">
correlation_output_threshold   <FLOAT name="corr_out_thresh"/> 
</DICT> 

<EOL2/>

<LOOP name="part10">
<DICT>
    <STR name='par1' format="%-8s"/>       
    <INT name='x1' format="%3d"/>  
    <INT name='x2' format="%3d"/>  
    <INT name='x3' format="%3d"/>  
    <INT name='x4' format="%3d"/>  
    <INT name='x5' format="%3d"/>  
    <INT name='x6' format="%3d"/>  
    <INT name='x7' format="%3d"/>  
    <INT name='x8' format="%3d"/>  
    <INT name='x9' format="%3d"/>  
    <INT name='x10' format="%3d"/>  
    <STR name='par2' format="     %-8s"/>       
    <INT name='y1' format="%3d"/>  
    <INT name='y2' format="%3d"/>  
    <INT name='y3' format="%3d"/>  
    <INT name='y4' format="%3d"/>  
    <INT name='y5' format="%3d"/>  
    <INT name='y6' format="%3d"/>  
    <INT name='y7' format="%3d"/>  
    <INT name='y8' format="%3d"/>  
    <INT name='y9' format="%3d"/>  
    <INT name='y10' format="%3d"/>  
    <FLOAT name="val" format="%9.3f"/>
    <EOL/>
</DICT>
</LOOP>

</DICT>
"""
    BUFFER = """                              *** LARGEST PAIR CORRELATIONS ***

correlation_output_threshold   0.90

X13       0  0  0  0  0  1  0  1  0  0     O3        0  0  0  0  0  0  0  1  0  0   -0.946
Y111      0  0  0  0  0  3  0  0  0  0     X11       0  0  0  0  0  2  0  0  0  0   -0.949
Y123      0  0  0  0  0  1  1  1  0  0     X23       0  0  0  0  0  0  1  1  0  0   -0.908
Y133      0  0  0  0  0  1  0  2  0  0     X33       0  0  0  0  0  0  0  2  0  0   -0.932
Y222      0  0  0  0  0  0  3  0  0  0     O2        0  0  0  0  0  0  1  0  0  0    0.928
Y1ll      0  0  0  0  0  1  0  0  1  0     Y112      0  0  0  0  0  2  1  0  0  0    0.915
Y1ll      0  0  0  0  0  1  0  0  1  0     Y122      0  0  0  0  0  1  2  0  0  0   -0.966
Y2ll      0  0  0  0  0  0  1  0  1  0     Y122      0  0  0  0  0  1  2  0  0  0    0.923
Y2ll      0  0  0  0  0  0  1  0  1  0     Y222      0  0  0  0  0  0  3  0  0  0   -0.939    
"""
    return do_test(XML,BUFFER)

def test_part1112():
    XML = """
<DICT>

                              *** LINE STATISTICS ***
<EOL2/>

<DICT name="part11">
Fmax input    <FLOAT name="Fmax"/> <EOL/>
Pmax input<STR name="Pmax"/> <EOL/>
</DICT>
tag
 ===
O - outlier
I - influental data point
C - point which has large affection on parameters of the model

 ref iso upper lower             Fobs       Fcalc  residual   unc  wht_res      --- upper -- --- lower ---                    Fobs            res.
                                (cm-1)      (cm-1)    (mK)    (mK)              p   j c   n   p   j c    n comment            (MHz)           (KHz)

<EOL/>

<LOOP name="part12">
    <DICT>
        <INT name="tag" format="%1d"/>
        <INT name="ref" format="%4d"/>
        <INT name="iso" format="%4d"/>
        <STR name="upper" format="%6s"/>
        <STR name="lower" format="%6s"/>
        <WORD name="branch" input="PQR" format="%2s"/>
        <STR name="Je" format="%5s"/>
        <FLOAT name="Fobs" format="%12.5f"/>
        <FLOAT name="Fcalc" format="%12.5f"/>
        <FLOAT name="residual" format="%8.2f"/>
        <FLOAT name="unc" format="%8.2f"/>
        <FLOAT name="wht_res" format="%8.2f"/>
        <OPTIONAL>
            <WORD name="flags" input="OIC" format=" %4s"/>
        </OPTIONAL>
        <INT name="p" format="%3d"/>
        <INT name="j" format="%4d"/>
        <INT name="c" format="%2d"/>
        <INT name="n" format="%5d"/>
        <INT name="p_" format="%3d"/>
        <INT name="j_" format="%4d"/>
        <INT name="c_" format="%2d"/>
        <INT name="n_" format="%5d"/>
        <RESTOFLINE name="comment"/>
        <EOL/>
    </DICT> 
</LOOP>

</DICT>
"""
    BUFFER = """                              *** LINE STATISTICS ***

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
0   2   1 00021 10011 P  11e   949.69886   949.69885    0.00    0.00    3.49  I   6  10 1   14  5  11 1    9                  28471255.43       69.86
0   1   1 10011 00001 R  26e  3733.46837  3733.46839   -0.02    0.02   -1.04      5  27 1    9  0  26 1    1                 111926565.89     -720.11
0   2   1 00021 10011 P  43e   919.81851   919.81850    0.01    0.00    7.66  I   6  42 1   14  5  43 1    9                  27575465.19      153.28
0   2   1 00021 10011 P  45e   917.74157   917.74156    0.01    0.00   12.56 OI   6  44 1   14  5  45 1    9                  27513200.16      251.22
0   2   1 00021 10011 R   5e   963.06229   963.06228    0.00    0.00    6.37  I   6   6 1   14  5   5 1    9                  28871880.98      127.38
"""
    return do_test(XML,BUFFER)

def test_part13():
    XML = """
<DICT>

***** BAND STATISTICS *****
 iso          band        ref Nlin  Jm  JM  fm      fM       dfm        dfM       mean       rms      uncert

<EOL/>

<FIXCOL name="part13">
//HEADER
0 iso int
1 v1 int
2 v2 int
3 l2 int
4 v3 int
5 r int
6 v1_ int
7 v2_ int
8 l2_ int
9 v3_ int
A r_ int
B ref int
C Nlin int
D Jmin int
E Jmax int
F Fmin float
G Fmax float
H dFmin float
I dFmax float
J mean float
K rms float
L uncert float

//DATA
0___1__2_3_4_5_6__7_8_9_A_B___C___D___E___F_______G_______H_________I_________J__________K__________L__________
<!--
 iso          band        ref Nlin  Jm  JM  fm      fM       dfm        dfM       mean       rms      uncert
   1  1 0 0 1 1  0 0 0 0 1   1   9   5  27  3698.0  3733.5  1.33E-05  3.67E-05 -2.401E-05  2.631E-05  3.561E-05
   1  0 0 0 2 1  1 0 0 1 1   2  35   5  45   917.7   983.5  6.67E-07  6.67E-07 -7.716E-08  2.781E-06  2.782E-06
-->
</FIXCOL>

</DICT>
"""
    BUFFER = """***** BAND STATISTICS *****
 iso          band        ref Nlin  Jm  JM  fm      fM       dfm        dfM       mean       rms      uncert
   1  0 0 0 8 1  0 0 0 7 1  34  45   0  67  2112.5  2208.2  5.00E-05  5.00E-05  7.814E-06  1.230E-04  1.233E-04
   1  0 0 0 9 1  0 0 0 8 1  34  38   2  61  2110.8  2183.6  6.00E-05  6.00E-05  1.352E-04  2.600E-04  2.931E-04
   1  0 0 010 1  0 0 0 9 1  34  32   3  60  2077.3  2158.4  2.40E-04  2.40E-04  5.362E-05  8.430E-04  8.447E-04
   1  0 0 011 1  0 0 010 1  34  29   2  56  2052.1  2125.9  2.50E-04  2.50E-04 -4.569E-04  1.353E-03  1.428E-03
   1  0 0 012 1  0 0 011 1  34  12   2  26  2057.7  2093.8  4.30E-04  4.30E-04 -3.017E-03  3.102E-03  4.327E-03  
"""
    return do_test(XML,BUFFER)

def test_part14():
    XML = """
<DICT>

***** J STATISTICS *****

iso  J     N    mean_res         rms   rms/max_res   max_res

<EOL2/>

<LOOP name="part14">
    <DICT>
        <INT name="iso" format="%2d"/>
        <INT name="J" format="%4d"/>
        <INT name="N" format="%6d"/>
        <FLOAT name="mean_res" format="%12.2f"/>
        <FLOAT name="rms" format="%12.2f"/>
        <FLOAT name="rms_upon_max_res" format="%12.2f"/>
        <FLOAT name="max_res" format="%12.2f"/>
        <EOL/>
    </DICT>
</LOOP>

</DICT>
"""
    BUFFER = """***** J STATISTICS *****

iso  J     N    mean_res         rms   rms/max_res   max_res

 1   0    25      -78.60     2469.04      -31.41    -4930.28
 1   1   522      248.45     4771.48       19.21    96321.22
 1   2   463       42.30     2163.36       51.15   -11314.44
 1   3   896     -152.31     5021.01      -32.97  -136955.82
 1   4   617       27.13     2192.98       80.84   -15300.82
 1   5  1095       89.92     2258.20       25.11    16395.28
"""
    return do_test(XML,BUFFER)

def test_part15():
    XML = """
<DICT>

***** SOURCE STATISTICS *****

src lines  jm  jM   mean_unc mean_res      rms

<EOL/>

<LOOP name="part15">
    <DICT>
        <INT name="src" format="%3d"/>
        <INT name="lines" format="%6d"/>
        <INT name="jmin" format="%4d"/>
        <INT name="jmax" format="%4d"/>
        <FLOAT name="mean_unc" format="%10.3f"/>
        <FLOAT name="mean_res" format="%10.3f"/>  
        <FLOAT name="rms" format="%10.3f"/>
        <RESTOFLINE name="refs"/>
    </DICT> <EOL/>
</LOOP>

</DICT>
"""
    BUFFER = """***** SOURCE STATISTICS *****

src lines  jm  jM   mean_unc mean_res      rms
  1     9   5  27     0.020    -0.024     0.026 Groh JMS 146 161 (1991)
  2    66   5  45     0.001    -0.000     0.003 Chou JMS 172 233 (1995)
  3    99   1  54     0.000     0.000     0.000 Bradley IEEE QE-22 234(1986)
  4    93   3  45     0.534     0.089     0.232 Siemsen OptComm 22 11 (1977)
  5    95   5  63     0.000     0.000     0.001 Maki JMS 167 211 (1994)
"""
    return do_test(XML,BUFFER)

def test_part16():
    XML = """
<DICT>

***** ISOTOPS *****
 # name symm    mass1       mass2       mass3      lines  rms (mK)v1 v2 v3   j    f_min    f_max    e_max

<EOL/>

<LOOP name="part16">
    <DICT>
        <INT name="i" format="%2d"/>
        <INT name="name" format="%5d"/>
        <INT name="symm" format="%5d"/>
        <FLOAT name="mass1" format="%12.8f"/>
        <FLOAT name="mass2" format="%12.8f"/>  
        <FLOAT name="mass3" format="%12.8f"/>
        <INT name="lines" format="%7d"/>
        <FLOAT name="rms" format="%10.2f"/>
        <INT name="v1" format="%3d"/>
        <INT name="v2" format="%3d"/>
        <INT name="v3" format="%3d"/>
        <INT name="j" format="%4d"/>
        <FLOAT name="f_min" format="%9.1f"/>
        <FLOAT name="f_max" format="%9.1f"/>
        <FLOAT name="e_max" format="%9.1f"/>
    </DICT> <EOL/>
</LOOP>

</DICT>
"""
    BUFFER = """***** ISOTOPS *****
 # name symm    mass1       mass2       mass3      lines  rms (mK)v1 v2 v3   j    f_min    f_max    e_max
 1  626    4  0.00000000  0.00000000  0.00000000  53713      1.83  5 12 12 177    562.1  14075.3  26800.3    
"""
    return do_test(XML,BUFFER)

def test_part17():
    XML = """
<DICT>

<DICT name="part17">
total lines<INT name="lines" format="%8d"/> <EOL2/>

total data:<INT name="data" format="%9d"/> <EOL2/>

energy levels:<INT name="elevels" format="%6d"/> <EOL/>
outliers:<INT name="outliers" format="%11d"/> <EOL/>
influentals:<INT name="influentals" format="%8d"/> <EOL/>
cooks:<INT name="cooks" format="%14d"/> <EOL/>
</DICT>

</DICT>
"""
    BUFFER = """total lines   63549

total data:    53713

energy levels: 10264
outliers:        620
influentals:    4342
cooks:            12
"""
    return do_test(XML,BUFFER)

def test_part18():
    XML = """
<DICT>

 Residual plot
 =============

<EOL3/>

<DICT name="part18">
    <TEXT 
        name="plot" 
        begin="Probability plot for normal distribution" 
        end="Cumulative Probability"
        format="              %s"
    />
</DICT>

</DICT>
"""
    BUFFER = """ Residual plot
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

def test_skipline():
    XML = """
<DICT>

<DICT name="part17">
total lines<INT name="lines" format="%8d"/> <EOL/>

<SKIPLINE/>
<SKIPLINE/>
<SKIPLINE/>

energy levels:<INT name="elevels" format="%6d"/> <EOL/>
outliers:<INT name="outliers" format="%11d"/> <EOL/>
influentals:<INT name="influentals" format="%8d"/> <EOL/>
cooks:<INT name="cooks" format="%14d"/> <EOL/>
</DICT>

</DICT>
"""
    BUFFER = """total lines   63549

total data:    53713

energy levels: 10264
outliers:        620
influentals:    4342
cooks:            12
"""
    return do_test(XML,BUFFER)

def test_skiplines():
    XML = """
<DICT>

<DICT name="part17">
total lines<INT name="lines" format="%8d"/> <EOL/>

<SKIPLINES n="3"/>

energy levels:<INT name="elevels" format="%6d"/> <EOL/>
outliers:<INT name="outliers" format="%11d"/> <EOL/>
influentals:<INT name="influentals" format="%8d"/> <EOL/>
cooks:<INT name="cooks" format="%14d"/> <EOL/>
</DICT>

</DICT>
"""
    BUFFER = """total lines   63549

total data:    53713

energy levels: 10264
outliers:        620
influentals:    4342
cooks:            12
"""
    return do_test(XML,BUFFER)

def test_loop_fix():
    XML = """
<DICT>

<DICT name="part17">

<LOOP name="header" min="5" max="5">
    <RESTOFLINE/><EOL/>
</LOOP>

outliers:<INT name="outliers" format="%11d"/> <EOL/>
influentals:<INT name="influentals" format="%8d"/> <EOL/>
cooks:<INT name="cooks" format="%14d"/> <EOL/>
</DICT>

</DICT>
"""
    BUFFER = """total lines   63549

total data:    53713

energy levels: 10264
outliers:        620
influentals:    4342
cooks:            12
"""
    return do_test(XML,BUFFER)

def test_format_python_percent_omit():
    XML = """
<DICT>

<FLOAT name="value" format="%7.3f"/>

</DICT>
"""
    BUFFER = """123.012
"""
    return do_test(XML,BUFFER)

def test_format_python_percent():
    XML = """
<DICT>

<FLOAT name="value" format="%7.3f" formatter="python_percent"/>

</DICT>
"""
    BUFFER = """123.012
"""
    return do_test(XML,BUFFER)

def test_format_fortranformat_F():
    XML = """
<DICT>

<FLOAT name="value" format="(F7.3)" formatter="fortranformat"/>

</DICT>
"""
    BUFFER = """123.012
"""
    return do_test(XML,BUFFER)

def test_format_fortranformat_E():
    XML = """
<DICT>

<FLOAT name="value" format="(E9.3)" formatter="fortranformat"/>

</DICT>
"""
    BUFFER = """0.023E-10
"""
    return do_test(XML,BUFFER)

def test_format_fortranformat_D():
    XML = """
<DICT>

<FLOAT name="value" format="(D9.3)" formatter="fortranformat"/>

</DICT>
"""
    BUFFER = """0.123D-10
"""
    return do_test(XML,BUFFER)

def test_buffer():
    XML = """
<DICT>

<BUFFER name="a1" nchars="3"/>
<BUFFER name="a2" nchars="4" type="str"/>
<BUFFER name="a3" nchars="5" type="int" format="%5d"/>
<BUFFER name="a4" nchars="7" type="float" format="%7.1E"/>

</DICT>
"""
    BUFFER = """ ABCDE  12341.2E-10
"""
    return do_test(XML,BUFFER)

def test_loop_optional_comments():
    XML = """
<DICT>

<LOOP name="parameters">
    <OPTIONAL>*<RESTOFLINE/><EOL/></OPTIONAL>
    <DICT>
        <INT name="id" format="%3d"/>
        <FLOAT name="value" format="(D24.16)" formatter="fortranformat"/>
        <EOL/>
    </DICT>
</LOOP>

</DICT>
"""
    BUFFER = """ 83  0.2147721405014595D-14
 84 -0.2753089078159071D-15
 85 -0.2597822208698380D-19
*     L-doubling
 86 -0.1531145611211136D-03
 87  0.0000000000000000D+00
 98 -0.1951636311583229D-14
*     Fermi
 99 -0.2660423874167142D+02
100  0.2506913679661035D+00
"""
    return do_test(XML,BUFFER)

def test_spaces_1():
    XML = """
<DICT>

some_word<S/>other_word<S/><INT name="num"/>

</DICT>
"""
    BUFFER = """some_word other_word 123
"""
    return do_test(XML,BUFFER)

def test_spaces_2():
    XML = """
<DICT>

some_word<S/>
other_word<S2/>
<INT name="num1"/><S3/>
<FLOAT name="num2"/><SS/>
<LITERAL name="abc" input="ABC"/>

</DICT>
"""
    BUFFER = """some_word other_word  123   12.0         ABC
"""
    return do_test(XML,BUFFER)

def test_spaces_3():
    XML = """
<DICT>

<LOOP name="details">
<DICT>

<RESTOFLINE name="parname"/><EOL/>
<WORD name="separ" input="-"/><EOL/>
Data type:<S/><RESTOFLINE name="type"/><EOL/>
C-style format specifier:<S/><RESTOFLINE name="cformat"/><EOL/>
Fortran-style format specifier:<S/><RESTOFLINE name="fformat"/><EOL/>
Units:<S/><RESTOFLINE name="units"/><EOL/>
Description:<S/><RESTOFLINE name="description"/><EOL2/>

</DICT>
</LOOP>

</DICT>
"""
    BUFFER = """molec_id
--------
Data type: int
C-style format specifier: %2d
Fortran-style format specifier: I2
Units: [dimensionless]
Description: The HITRAN integer ID for this molecule in all its isotopologue forms

local_iso_id
------------
Data type: int
C-style format specifier: %1d
Fortran-style format specifier: I1
Units: [dimensionless]
Description: Integer ID of a particular Isotopologue, unique only to a given molecule

nu
--
Data type: float
C-style format specifier: %12.6f
Fortran-style format specifier: F12.6
Units: cm-1
Description: Transition wavenumber
"""
    return do_test(XML,BUFFER)

def test_fixcol_asterisc_1():
    XML = """
<DICT>

THIS IS A HEADER<EOL2/>

    Name          Parameter             Estimate         Error    Sensit.   Est/Err Inflat.  Weight Tags  Gradient    Step
           R M1 M2 M3  D  1  2  3  L  J

<EOL/>

<FIXCOL name="parameters">
//HEADER
0 name STR
1 R INT
2 M1 INT
3 M2 INT
4 M3 INT
5 D INT
6 A1 INT
7 A2 INT
8 A3 INT
9 L INT
A J INT
B estimate FLOAT
C error FLOAT
D sensit FLOAT
E est_err FLOAT
F inflat FLOAT *******
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
 Z1112     0  0  0  0  0  3  1  0  0  0  0.1444336305E-02 0.33E-04 0.20E-10   0.4E+02 6.5E-01 0.71E-01   -0.42E+07  0.14E-02
 W11122    0  0  0  0  0  3  2  0  0  0 -0.1701685787E-05 0.43E-05 0.45E-11   0.4E+00 ******* 0.60E-04 T  0.85E+07 -0.17E-05
-->
</FIXCOL>

</DICT>
"""
    BUFFER = """THIS IS A HEADER

    Name          Parameter             Estimate         Error    Sensit.   Est/Err Inflat.  Weight Tags  Gradient    Step
           R M1 M2 M3  D  1  2  3  L  J
 O1        0  0  0  0  0  1  0  0  0  0   1353.674539     0.35E-03 0.42E-09   0.4E+07 ******* 0.55E-01   -0.57E+06  0.14E+04
 Z1112     0  0  0  0  0  3  1  0  0  0  0.1444336305E-02 0.33E-04 0.20E-10   0.4E+02 6.5E-01 0.71E-01   -0.42E+07  0.14E-02
 W11122    0  0  0  0  0  3  2  0  0  0 -0.1701685787E-05 0.43E-05 0.45E-11   0.4E+00 ******* 0.60E-04 T  0.85E+07 -0.17E-05
"""
    return do_test(XML,BUFFER)

def test_fixcol_asterisc_2():
    XML = """
<DICT>

THIS IS A HEADER<EOL2/>

 ref iso upper lower             Fobs       Fcalc  residual   unc  wht_res          upper        lower                        Fobs            res.
                                (cm-1)      (cm-1)    (mK)    (mK)              p   j c   n   p   j c    n comment            (MHz)           (KHz)

<EOL/>

<FIXCOL name="parameters" restofline="comment">
//HEADER
0 tag INT
1 ref INT
2 iso INT
3 upper STR
4 lower STR
5 br STR
6 Jlow INT
7 sym STR
8 Fobs FLOAT
9 Fcalc FLOAT
A unwht_resid_mk FLOAT
B uncertainty FLOAT
C wht_resid_mk FLOAT ********
D flags STR
E p INT
F j INT
G c INT
H n INT
I p_ INT
J j_ INT
K c_ INT
L n_ INT

//DATA
01___2___3_____4_____5_6___78___________9___________A_______B_______C_______D___E__F___G_H____I__J___K_L____
<!--
 ref iso upper lower             Fobs       Fcalc  residual   unc  wht_res          upper        lower                        Fobs            res.
                                (cm-1)      (cm-1)    (mK)    (mK)              p   j c   n   p   j c    n comment            (MHz)           (KHz)
0 170   1 60025 30013 P  37e100995.56165  5995.56621   -4.56    0.00    0.50 OI  18  36 1   66  9  37 1
0   1   1 10011 00001 P   6e  3710.00467  3710.00464    0.03    0.02    1.41      5   5 1    9  0   6 1    1                 111223141.91      777.49
0   1   1 10011 00001 P  12e  3705.00127  3705.00125    0.02    0.02    1.00      5  11 1    9  0  12 1    1                 111073143.81      609.47
-->
</FIXCOL>

</DICT>
"""
    BUFFER = """THIS IS A HEADER

 ref iso upper lower             Fobs       Fcalc  residual   unc  wht_res          upper        lower                        Fobs            res.
                                (cm-1)      (cm-1)    (mK)    (mK)              p   j c   n   p   j c    n comment            (MHz)           (KHz)
0 170   1 60025 30013 P  37e100995.56165  5995.56621   -4.56    0.00    0.50 OI  18  36 1   66  9  37 1   18
0   1   1 10011 00001 P   6e  3710.00467  3710.00464    0.03    0.02    1.41      5   5 1    9  0   6 1    1                 111223141.91      777.49
0   1   1 10011 00001 P  12e  3705.00127  3705.00125    0.02    0.02    1.00      5  11 1    9  0  12 1    1                 111073143.81      609.47
0   1   1 10011 00001 P  18e  3699.77319  3699.77317    0.02    0.01    1.32      5  17 1    9  0  18 1    1                 110916409.81      527.58
0  23   1 03301 02201 P  52e   629.33240   629.33235    0.05    0.36    0.14      3  51 1    2  2  52 1    2                 
0  23   1 03301 02201 P  53f   628.62460   628.62329    1.31    0.30    4.38      3  52 2    2  2  53 2    1 *               
0  23   1 03301 02201 P  54e   627.92270   627.92256    0.14    0.36    0.40      3  53 1    2  2  54 1    2                 
0 170   1 60025 30013 P  27e  6003.57864  6003.55251   26.13    0.00******** OI  18  26 1   66  9  27 1   16                 179982759.80   783316.34
0 170   1 60025 30013 P  29e  6001.97927  6001.95870   20.57    0.00******** OI  18  28 1   66  9  29 1   16                 179934811.74   616721.86
0 170   1 60025 30013 P  31e  6000.37723  6000.36250   14.73    0.0088324.79 OI  18  30 1   66  9  31 1   16                 179886783.80   441623.97
0 170   1 60025 30013 P  33e  5998.77312  5998.76452    8.60    0.0051572.79 OI  18  32 1   66  9  33 1   16                 179838693.90   257863.93
0 170   1 60025 30013 P  37e  5995.56165  5995.56621   -4.56    0.00    0.50 OI  18  36 1   66  9  37 1   17
0 170   1 60025 30013 P  35e  5997.16766  5997.16548    2.17    0.0013040.03  I  18  34 1   66  9  35 1   16                 179790563.28    65200.13
0 170   1 60025 30013 P  37e  5995.56165  5995.56621   -4.56    0.00******** OI  18  36 1   66  9  37 1   20
"""
    return do_test(XML,BUFFER)

def test_fixcol_asterisc_2_simple1():
    XML = """
<DICT>

THIS IS A HEADER<EOL2/>

<FIXCOL name="parameters" restofline="comment">
//HEADER
0 tag INT
1 ref INT

//DATA
01___
<!--
0  23 *               
0  23
0 170                 179982759.80   783316.34
-->
</FIXCOL>

</DICT>
"""
    BUFFER = """THIS IS A HEADER

0 170
0   1    1                 111223141.91      777.49
0   1    1                 111073143.81      609.47
0   1    1                 110916409.81      527.58
0  23    2                 
0  23    1 *               
0  23    2                 
0 171   16                 179982759.80   783316.34
0 172   16                 179934811.74   616721.86
0 173   16                 179886783.80   441623.97
0 174   16                 179838693.90   257863.93
0 175
0 176   16                 179790563.28    65200.13
0 177
"""
    return do_test(XML,BUFFER)

def test_fixcol_asterisc_3():
    XML = """
<DICT>

THIS IS A HEADER<EOL2/>

***** J STATISTICS *****

iso  J     N    mean_res         rms   rms/max_res   max_res<EOL2/>

<FIXCOL name="jstat">
//HEADER
0 iso INT
1 J INT 
2 N INT 
3 mean_res FLOAT ************
4 rms FLOAT ************
5 rms_to_max_res FLOAT
6 max_res FLOAT ************

//DATA
0_1___2_____3___________4___________5___________6___________
<!--
iso  J     N    mean_res         rms   rms/max_res   max_res
 1   0    30     -743.47     4281.70       -5.76   -20333.23
 1  40   817  -141014.20  3988600.56      -28.29************
 1   1   688    -4645.41    67444.20      -14.52 -1572220.49
 1   2   609   653022.69 16118126.51       24.68397761911.59
 1  17  1636    -2742.42   100302.80      -36.57 -2789657.40
-->
</FIXCOL>

</DICT>
"""
    BUFFER = """THIS IS A HEADER

***** J STATISTICS *****

iso  J     N    mean_res         rms   rms/max_res   max_res

 1   0    30     -743.47     4281.70       -5.76   -20333.23
 1  40   817  -141014.20  3988600.56      -28.29************
 1   1   688    -4645.41    67444.20      -14.52 -1572220.49
 1   2   609   653022.69 16118126.51       24.68397761911.59
 1  17  1636    -2742.42   100302.80      -36.57 -2789657.40
 1  18  1020   267588.51  8534321.06       31.89272564196.92
 1  22  1028   212771.91  6804778.84       31.98218177367.81
 1  23  1596   -21084.62   586609.94      -27.82-21662911.95
 1  24   990   191513.09  5984047.54       31.25188281639.11
 1  42   739  -218612.40  5903842.74      -27.01************
 1  45  1118        6.24    18161.19     2909.80  -249502.72
 1  46   626  -416568.94 10407248.92      -24.98************
 1  47  1026     2020.61    53854.98       26.65  1582023.56
 1  48   582  -540608.16 13018191.69      -24.08************
"""
    return do_test(XML,BUFFER)
    
TEST_CASES = [
    test_part0a,
    test_part0b,
    test_part1,
    #test_part34, # fails
    test_part56,
    test_part78,
    test_part910,
    test_part1112,
    test_part13,
    test_part14,
    test_part15,
    test_part16,
    test_part17,
    test_part18,
    test_loop,
    test_fixcol,
    test_skipline,
    test_skiplines,
    test_format_python_percent_omit,
    test_format_python_percent,
    test_format_fortranformat_F,
    test_format_fortranformat_E,
    test_format_fortranformat_D,
    test_buffer,
    #test_loop_optional_comments, # fails
    test_spaces_1,
    test_spaces_2,
    test_spaces_3,
    test_fixcol_asterisc_1,
    test_fixcol_asterisc_2,
    test_fixcol_asterisc_2_simple1,
    test_fixcol_asterisc_3,
]

def get_test_cases(func_names):
    args = func_names
    if not args:
        return TEST_CASES
    test_cases = []
    for arg in args:
        test_cases.append(eval(arg))
    return test_cases

def do_tests(test_cases,testgroup=None,session_name=None): # test all functions    
    
    if testgroup is None:
        filestem,_ = os.path.splitext(__file__)
        testgroup = filestem

    session_uuid = uuid()
    
    for test_fun in test_cases:        
        runtest(test_fun,testgroup,session_name,session_uuid,save=True)
        
if __name__=='__main__':

    parser = argparse.ArgumentParser(description=\
        'Test driver for the FreeParse Python library.')

    parser.add_argument('--session', type=str, default='__not_supplied__',
        help='Session name')

    parser.add_argument('--verbose', dest='verbose',
        action='store_const', const=True, default=False,
        help='Verbose mode')

    parser.add_argument('--breakpoints', dest='breakpoints',
        action='store_const', const=True, default=False,
        help='Turn on breakpoints')

    parser.add_argument('--debug', dest='debug',
        action='store_const', const=True, default=False,
        help='Grammar debugging mode')

    parser.add_argument('--parse-all', dest='parse_all',
        action='store_const', const=True, default=False,
        help='Enabling PARSE_ALL mode')

    parser.add_argument('--cases', nargs='*', type=str, 
        help='List of test cases (functions)')
        
    args = parser.parse_args() 

    VARSPACE['VERBOSE'] = args.verbose
    VARSPACE['DEBUG'] = args.debug
    VARSPACE['BREAKPOINTS'] = args.breakpoints    
        
    VARSPACE['parse_all'] = args.parse_all
    
    if args.parse_all:
        print('ATTENTION: PARSE_ALL MODE ENABLED')
        
    test_cases = get_test_cases(args.cases)
        
    do_tests(test_cases=test_cases,session_name=args.session)
    
