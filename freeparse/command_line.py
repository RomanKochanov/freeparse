import os
import sys
import json
import pickle
import argparse

# this doesn't seem to increase speed
#import pyparsing
#pyparsing.ParserElement.enablePackrat()
 
from .freeparse import *

def get_filestem(filename):
    stem,ext = os.path.splitext(filename)
    return stem

def main():
    """ Main command line driver"""

    parser = argparse.ArgumentParser(description=\
        'User-friendly text file parser.')

    parser.add_argument('--grammar', type=str, 
        help='XML file defining the grammar (mandatory)')
    #parser.add_argument('xml', metavar='xml',
    #    help='XML format file (mandatory)')    

    parser.add_argument('--diagram', type=str, nargs='?', default='',
        help='Name of the railroad diagram HTML file (optional)')
        
    parser.add_argument('--input', type=str, 
        help='Name of the input file (optional)')

    parser.add_argument('--output', type=str, 
        help='Name of the output file (optional)')

    parser.add_argument('--encoding', type=str, default='utf-8',
        help='Encoding of the input file')

    parser.add_argument('--sniff-encoding', dest='sniff_encoding',
        action='store_const', const=True, default=False,
        help='Detect encoding of the input file (optional)')

    parser.add_argument('--format', type=str, default='json',
        help='Format of the output file (optional): pickle, json')
        
    parser.add_argument('--verbose', dest='verbose',
        action='store_const', const=True, default=False,
        help='Verbose flag (useful for debugging, optional)')
        
    args = parser.parse_args() 
        
    # Create Parsing Tree from the XML file.
    #if not args.grammar:
    #    raise Exception('ERROR: XML filename should be supplied')
    grammar_flag = False
    if args.grammar:
        tree = create_from_file(args.grammar)
        grammar_flag = True
    
    # Set the verbosity level.
    VARSPACE['DEBUG'] = args.verbose

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
        
    # If specified, generate a railroad diagram.
    if args.diagram is not None and args.grammar:

        if not grammar_flag:
            raise Exception('XML grammar not provided')
            
        if args.diagram=='':
            args.diagram = get_filestem(args.grammar) + '.html'

        tree.create_grammar()
        tree.grammar.create_diagram(args.diagram)
        
        print('Diagram was saved to',args.diagram)
        
    if args.input and args.grammar:
        
        if not grammar_flag:
            raise Exception('XML grammar not provided')
        
        tree.parse_file(args.input,encoding=args.encoding)
        data = tree.get_data()
        
        if not args.output:
            stem = get_filestem(args.input)
        
        if args.format=='json':
            outbuf = json.dumps(data,indent=2)
            outfile = args.output if args.output else stem+'.json'
            with open(outfile,'w') as f:
                f.write(outbuf)
        
        elif args.format=='pickle':
            outbuf = pickle.dumps(data)
            outfile = args.output if args.output else stem+'.pickle'
            with open(outfile,'wb') as f:
                f.write(outbuf)
        else:
            raise Exception('unknown format: "%s"'%args.format)
        
        print('Output saved to',outfile)


















