import os
import sys
import json
import pickle
import argparse

from time import time
from copy import deepcopy
from difflib import Differ

# this doesn't seem to increase speed
#import pyparsing
#pyparsing.ParserElement.enablePackrat()
 
from .freeparse import *

def get_filestem(filename):
    stem,ext = os.path.splitext(filename)
    return stem

def save_data(data,args,filestem=None):

    if not filestem:
        if not args.output:
            filestem = get_filestem(args.input)
        else:
            filestem,_ = os.path.splitext(args.output)
        
    if args.format=='json':
        outbuf = json.dumps(data,indent=2)
        outfile = filestem+'.json'
        with open(outfile,'w') as f:
            f.write(outbuf)
        
    elif args.format=='pickle':
        outbuf = pickle.dumps(data)
        outfile = filestem+'.pickle'
        with open(outfile,'wb') as f:
            f.write(outbuf)
    else:
        raise Exception('unknown format: "%s"'%args.format)
        
    return outfile

def compare_buffers(buf2,buf1,outfile=None):
    buf1_lines = buf1.split('\n')
    buf2_lines = buf2.split('\n')
    d = Differ()
    difference = list(d.compare(buf1_lines, buf2_lines))
    difference = '\n'.join(difference)
    #print (difference)
    if not outfile:
        outfile = 'compare_buffers.diff'
    with open(outfile,'w') as f:
        f.write(difference)
    
def compare_data(data2,data1,outfile=None):
    """ Simple yet informative comparison: 
        use only higher-level detalization """
    if type(data1)==type(data2)==list:
        result = []
        minln = min(len(data1),len(data2))
        maxln = max(len(data1),len(data2))
        for i in range(minln):
            result.append(data1[i]==data2[i])
        result += [False]*(maxln-minln)        
    elif type(data1)==type(data2)==dict:
        keys1 = list(data1.keys())
        keys2 = list(data2.keys())
        result = {}
        for key in keys2:
            #print('===================')
            #print('key',key)
            compare = data1.get(key)==data2.get(key)
            #print('data1.get(key)',data1.get(key))
            #print('data2.get(key)',data2.get(key))
            #print('compare',compare)
            #print('===================')
            result[key] = compare
        for key in keys1:
            if key in keys2: continue
            result[key] = False
    elif type(data1)!=type(data2):
        raise Exception('types are not same: <%s> and <%s>'%(
            type(data1),type(data2)))
    else:
        raise Exception('unknown data type <> for data1 and data2'%(
            type(data1)))
    if not outfile:
        outfile = 'compare_data.diff'
    with open(outfile,'w') as f:
        f.write(json.dumps(result,indent=2))

def main():
    """ Main command line driver"""

    parser = argparse.ArgumentParser(description=\
        'User-friendly text file parser.')

    parser.add_argument('--grammar', type=str, 
        help='XML file defining the grammar')
    #parser.add_argument('xml', metavar='xml',
    #    help='XML format file (mandatory)')    

    parser.add_argument('--diagram', type=str, nargs='?', default='',
        help='Name of the railroad diagram HTML file')
        
    parser.add_argument('--input', type=str, 
        help='Name of the input file')

    parser.add_argument('--output', type=str, 
        help='Name of the output file')

    parser.add_argument('--encoding', type=str, default='utf-8',
        help='Encoding of the input file')

    parser.add_argument('--sniff-encoding', dest='sniff_encoding',
        action='store_const', const=True, default=False,
        help='Detect encoding of the input file')

    parser.add_argument('--format', type=str, default='json',
        help='Format of the output file: pickle, json')

    parser.add_argument('--generate', dest='generate',
        action='store_const', const=True, default=False,
        help='Generate raw text file using XML and data structure')
        
    parser.add_argument('--verbose', dest='verbose',
        action='store_const', const=True, default=False,
        help='Verbose flag (useful for debugging)')

    parser.add_argument('--breakpoints', dest='breakpoints',
        action='store_const', const=True, default=False,
        help='Turn on breakpoints (useful for debugging)')
        
    parser.add_argument('--debug', dest='debug',
        action='store_const', const=True, default=False,
        help='Turn on grammar debug (ATTENTION: very space-demanding!!!)')

    parser.add_argument('--test-grammar', dest='test_grammar',
        action='store_const', const=True, default=False,
        help='Grammar testing mode (parse->generate->compare)')

    parser.add_argument('--difflib', dest='difflib',
        action='store_const', const=True, default=False,
        help='Comparing buffers using difflib (can be slow)')
        
    args = parser.parse_args() 
        
    # Create Parsing Tree from the XML file.
    #if not args.grammar:
    #    raise Exception('ERROR: XML filename should be supplied')
    grammar_flag = False
    if args.grammar:
        tree = create_from_file(args.grammar)
        grammar_flag = True
    
    # Set the verbosity level.
    VARSPACE['VERBOSE'] = args.verbose

    # Set the breakpoints.
    VARSPACE['BREAKPOINTS'] = args.breakpoints

    # Set the debug mode.
    VARSPACE['DEBUG'] = args.debug

    #print('args.diagram>>>',args.diagram,type(args.diagram))

    if args.sniff_encoding:
        
        if not args.input:
            raise Exception('no input file name specified')
        
        from bs4 import UnicodeDammit

        with open(args.input,'rb') as f:
            binbuf = f.read()

        print('detecting input file encoding...')

        dammit = UnicodeDammit(binbuf)
        #print(dammit.unicode_markup) # print data

        print(dammit.original_encoding)
        
        args.encoding = dammit.original_encoding
        
    # If specified, generate a railroad diagram.
    #if args.diagram is not None and args.grammar:
    if args.grammar:

        if not grammar_flag:
            raise Exception('XML grammar not provided')
            
        if args.diagram=='':
            args.diagram = get_filestem(args.grammar) + '.html'

        tree.create_grammar()
        tree.grammar.create_diagram(args.diagram)
        
        print('Diagram was saved to',args.diagram)
        
    if not args.generate and not args.test_grammar: 
        # get data structure from raw file and XML format
        
        # freeparse --grammar test.xml --input test.json --format json --output test.json
        
        if args.input and args.grammar:
            
            if not grammar_flag:
                raise Exception('XML grammar not provided')
        
            tree.parse_file(args.input,encoding=args.encoding)
            data = tree.get_data()
        
            outfile = save_data(data,args)
            print('Output saved to',outfile)
            
    elif args.input and args.grammar and not args.test_grammar: 
        # get raw file from data structure and XML format

            # freeparse --grammar test.xml --input test.json --format json --generate --output test.raw

            if not grammar_flag:
                raise Exception('XML grammar not provided')

            if args.format=='json':
                with open(args.input,'r') as f:
                    data = json.load(f)
        
            elif args.format=='pickle':
                with open(args.input,'rb') as f:
                    data = pickle.load(f)
            else:
                raise Exception('unknown format: "%s"'%args.format)

            if not args.output:
                outfile,_ = os.path.splitext(args.input)
            else:
                outfile = args.output
                
            buf = tree.generate(data)
            with open(outfile,'w') as f:
                f.write(buf)

            print('Output saved to',outfile)
            
    elif args.test_grammar:
        # grammar testing mode
        
        t = time()
        
        # Open input file.
        with open(args.input,encoding=args.encoding) as f:
            rawbuf = f.read()

        # 1st stage (a): parse initial file and get data.
        #tree.parse_file(args.input,encoding=args.encoding)
        tree.parse_string(rawbuf)
        
        data = deepcopy(tree.get_data())

        outfile_data = save_data(data,args)
        print('\n1st stage parsed data structure saved to',outfile_data)

        # 2nd stage (a): generate and save a new "raw" file.
        rawbuf2 = tree.generate(data)
        filestem,_ = os.path.splitext(outfile_data)
        outfile_buf = filestem + '.stage2' + '.rawbuf2'
        with open(outfile_buf,'w') as f:
            f.write(rawbuf2)
        print('2nd stage generated "raw" file saved to',outfile_buf)
        
        # 2nd stage (b): parse generated "raw" file and get new data structure.
        tree.parse_string(rawbuf2)
        data2 = deepcopy(tree.get_data())

        outfile_data2 = save_data(data2,args,filestem+'.stage2')
        print('2st stage parsed data structure saved to',outfile_data2)
        
        # 3rd stage (a): compare "raw" buffers.
        if args.difflib:
            outfile_bufferdiff = filestem+'.buffers_diff'
            compare_buffers(rawbuf2,rawbuf,outfile_bufferdiff)
            print('3rd stage buffer2-buffer diff comparison saved to',outfile_bufferdiff)
        
        # 4th stage (a): compare data structures
        outfile_datadiff = filestem+'.data_diff'
        compare_data(data2,data,outfile_datadiff)
        print('4th stage data2-data diff comparison saved to',outfile_datadiff)
        
        # 5th stage (a): higher-level comparison
        compare = data2==data
        if compare: 
            print('\nSUCCESS: DATA SIMILARITY TEST PASSED\n')
        else:
            print('\nERROR: DATA SIMILARITY TEST NOT PASSED\n')
        
        # Print elapsed time.
        print('Elapsed time: %f sec.'%(time()-t))








