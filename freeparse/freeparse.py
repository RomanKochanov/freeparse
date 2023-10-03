import io
import re
import json
import pyparsing as pp

from copy import deepcopy
from functools import reduce

from pyparsing import (LineEnd, Literal, Empty, Word, 
    printables, ZeroOrMore, Optional, Group, restOfLine, 
    Regex, Combine, LineStart)

import pyparsing.common as ppc

import xml.etree.ElementTree as ET

EOL = LineEnd()
EMPTY = Empty()

VARSPACE = {
    'DEBUG': False
}

def _print(*args):
    if VARSPACE['DEBUG']: print(*args)

class Buffer:
    
    def __init__(self):
        raise NotImplementedError
    
    def insert(self,key,value):
        raise NotImplementedError
    
    def flush_data(self):
        raise NotImplementedError
        
    def relocate_buffer(self,key,external_buffer):
        external_data = external_buffer.flush_data()
        self.insert(key,external_data)
                
    def pretty_print(self,margin=0):
        s0 = json.dumps(self.__buffer__,indent=2)
        lines = s0.split('\n')
        s1 = '\n'.join([' '*margin+line for line in lines])
        print(s1)

class BufferDict(Buffer):
    
    def __init__(self):
        self.__buffer__ = {}
    
    def insert(self,key,value):
        self.__buffer__[key] = value

    def flush_data(self):
        external_data = {}
        for key in self.__buffer__:
            external_data[key] = self.__buffer__[key]
        self.__buffer__.clear()
        return external_data        

class BufferList(Buffer):
    
    def __init__(self):
        self.__buffer__ = []
    
    def insert(self,key,value):
        self.__buffer__.append(value)

    def flush_data(self):
        external_data = []
        for val in self.__buffer__:
            external_data.append(val)
        self.__buffer__.clear()
        return external_data        

class BufferStub(Buffer):
    
    def __init__(self):
        self.__buffer__ = None
    
    def insert(self,key,value):
        raise NotImplementedError

    def flush_data():
        raise NotImplementedError

def sum_grammars(*grammars):
    gg = []
    for g in grammars:
        if g: gg.append(g)
    grammar = reduce(lambda x,y: x+y,gg) if gg else None
    return grammar

class ParsingTree:
    
    """
    Abstract class for all the subclasses. 
    GetGrammar method must be redefined by subcasses.
    """
    
    @classmethod
    def get_buffer(cls):
        raise NotImplementedError
    
    @classmethod
    def create_tree(cls,xmlroot,parent=None):

        cls_ = DISPATCHER[xmlroot.tag]
        obj = cls_(xmlroot,parent)

        if issubclass(obj.__class__,ParsingTreeContainer):
            new_parent = obj
        else:
            new_parent = parent

        for el in xmlroot:
            child_obj = cls.create_tree(el,new_parent)
            obj.__children__.append(child_obj)
            
        return obj
                
    def __init__(self,xmlroot,parent=None):
        """
        "parent" must have the defined "push" method
        which adds the parsed values to internal storage 
        (list, dict etc...)
        The push method is activated by child every time the 
        parse action trigger is activated.
        """        
        self.__grammar__ = None
        self.__parent__ = parent # !!! parent must be container!!!
        #self.__buffer__ = Buffer()
        self.__buffer__ = self.__class__.get_buffer()
        self.__xmlroot__ = xmlroot  
        self.__tag__ = xmlroot.tag  
        self.__text__ = xmlroot.text
        self.__tail__ = xmlroot.tail    
        self.__varname__ = xmlroot.get('name')
        self.__children__ = [] # each child is a tag
        
    def collect_grammar_from_children(self): 
        """
        Collect grammar from text, children, and tail.
        """
        
        _print('collect_grammar_from_children>>>self.__tag__',self.__tag__)
        
        # initialize grammar list
        gg = []
        
        # append text grammar, if present
        if self.__text__ is not None:
            text = self.__text__.strip()
            if text: gg.append(text)
            
            _print('collect_grammar_from_children>>>gg|0',gg)
            
        # append child grammars, if present
        for el in self.__children__:
            gg.append(el.getGrammar())
            
        _print('collect_grammar_from_children>>>gg|1',gg)
        
        grammar_body = reduce(lambda x,y:x+y,gg) if gg else None
        
        _print('collect_grammar_from_children>>>grammar_body',grammar_body)
    
        # append tail grammar, if present
        if self.__tail__ is not None:
            grammar_tail = self.__tail__.strip()
        else:
            grammar_tail = None
            
        _print('collect_grammar_from_children>>>grammar_tail',grammar_tail)
                        
        return grammar_body,grammar_tail
        
    def print_tree(self,level=0,show_buffer=False):
        print('\n'+("=="*level),self.__tag__,self.__varname__)
        if show_buffer:
            self.__buffer__.pretty_print(margin=2*level)
        for child in self.__children__:
            child.print_tree(level=level+1,show_buffer=show_buffer)
                        
    def insert_to_buffer(self,key,value):
        self.__buffer__.insert(key,value)       
        
    def get_data(self):
        return self.__buffer__.__buffer__
    
    @property
    def grammar(self):
        if not self.__grammar__:
            self.__grammar__ = self.getGrammar()
        return self.__grammar__
        
    def create_grammar(self):
        self.__grammar__ = self.getGrammar()
        
    def parse_string(self,buf):
        self.grammar.parse_string(buf)
        
    def parse_file(self,fileobj,encoding='utf-8'):
        enc = encoding
        if type(fileobj) is str:
            with open(fileobj,encoding=enc) as f:
                buf = f.read()
        else:
            enc_ = fileobj.encoding
            assert enc_==enc,'%s <> %s'%(enc_,enc)
            buf = fileobj.read()
        self.parse_string(buf)
                
    def getGrammar(self):
        raise NotImplementedError

    def init_grammar(self):
        raise NotImplementedError

    def post_process(self):
        raise NotImplementedError
        
class ParsingTreeValue(ParsingTree):    
    """
    Abstract class for the "leaves" such as float, int, str etc...
    """    
    
    @classmethod
    def get_buffer(cls):
        return BufferStub()
            
    def post_process(self,grammar):
        return grammar
    
    def getGrammar(self):
        
        grammar = self.init_grammar()
        type_ = self.get_type()
        
        # add type conversion
        grammar.setParseAction(lambda tokens: type_(tokens[0]))
        
        # attach the trigger             
        def insert_to_parent(self,value):            
            parent = self.__parent__
            key = self.__varname__            
            _print('============================')
            _print('insert_to_parent>>>self.__tag__',self.__tag__)
            _print('insert_to_parent>>>parent.__tag__',parent.__tag__)
            _print('insert_to_parent>>>parent.__varname__',parent.__varname__)
            _print('insert_to_parent>>>key',key)
            _print('insert_to_parent>>>value',value)
            _print('============================')
            parent.insert_to_buffer(key,value)
            
        grammar.addParseAction(lambda tokens: insert_to_parent(self,tokens[0]))
        
        # take care of the tail text (if present)
        if self.__tail__ is not None:
            tail = self.__tail__.strip()
            if tail:
                grammar += tail

        _print('ParsingTreeValue.getGrammar>>>grammar',grammar)
        
        #grammar = Group(grammar) # !!! without this regex and text do not work.
        # ??? is it necessary to assign a group to each value???
        
        grammar = self.post_process(grammar)
        
        return grammar
        
class TreeFLOAT(ParsingTreeValue):
    
    def init_grammar(self):
        return ppc.number()
    
    def get_type(self):
        return float
    
class TreeINT(ParsingTreeValue):

    def init_grammar(self):
        return ppc.number()
    
    def get_type(self):
        return int

class TreeSTR(ParsingTreeValue):

    def init_grammar(self):
        return Word(printables)
    
    def get_type(self):
        return str

class TreeLITERAL(ParsingTreeValue):

    def init_grammar(self):
        inp = self.__xmlroot__.get('input')
        if not inp: raise Exception('LITERAL tag must '
                'have "input" parameter specified')
        return Literal(inp)
    
    def get_type(self):
        return str

class TreeWORD(ParsingTreeValue):

    def init_grammar(self):
        inp = self.__xmlroot__.get('input')
        #if not inp: inp = printables
        if not inp: inp = pyparsing_unicode.printables
        return Word(inp)
    
    def get_type(self):
        return str

class TreeRESTOFLINE(ParsingTreeValue):
    
    def init_grammar(self):
        return restOfLine()
    
    def get_type(self):
        return str

class TreeREGEX(ParsingTreeValue):

    def init_grammar(self):
        inp = self.__xmlroot__.get('input')
        if not inp: 
            raise Exception('regex is empty')
        return Regex(inp)
    
    def get_type(self):
        return str
        
    def post_process(self,grammar):
        return Group(grammar)

class TreeTEXT(ParsingTreeValue):

    def init_grammar(self):
        begin = self.__xmlroot__.get('begin')
        end = self.__xmlroot__.get('end')
        if not (begin and end): 
            raise Exception('text should have both "begin" and "end" fields')
        return Regex(begin+'[\s\S]*'+end)
    
    def get_type(self):
        return str

    def post_process(self,grammar):
        return Group(grammar)

class ParsingTreeContainer(ParsingTree):
    """
    Abstract class for container tags (list, loop, dict).
    """    

    def getGrammar(self):
                
        grammar_body,grammar_tail = self.collect_grammar_from_children()        
        
        grammar = self.process(grammar_body,grammar_tail)

        # attach a trigger to group, if parent is not None
        if self.__parent__ is not None:                    
            
            def move_to_parent(self):
                parent = self.__parent__ 
                key = self.__varname__
                buf = self.__buffer__
                _print('============================')
                _print('move_to_parent>>>self.__tag__',self.__tag__)
                _print('move_to_parent>>>parent.__tag__',parent.__tag__)
                _print('move_to_parent>>>parent.__varname__',parent.__varname__)
                _print('move_to_parent>>>key',key)
                _print('move_to_parent>>>buf',buf.__buffer__)
                _print('============================')
                parent.__buffer__.relocate_buffer(key,buf)
            
            grammar.setParseAction(lambda tokens: move_to_parent(self))
                
        _print('ParsingTreeContainer.getGrammar>>>self.__tag__',self.__tag__)
        _print('ParsingTreeContainer.getGrammar>>>self.__varname__',self.__varname__)
        if self.__parent__:
            _print('ParsingTreeContainer.getGrammar>>>self.__parent__.__tag__',self.__parent__.__tag__)
        _print('ParsingTreeContainer.getGrammar>>>grammar',grammar)

        return grammar

class TreeDICT(ParsingTreeContainer):
    """ Dictionary """
    
    @classmethod
    def get_buffer(cls):
        return BufferDict()

    def process(self,grammar_body,grammar_tail):
        return sum_grammars(grammar_body,grammar_tail)

class TreeLIST(ParsingTreeContainer):
    """ Static list """

    @classmethod
    def get_buffer(cls):
        return BufferList()

    def process(self,grammar_body,grammar_tail):
        return sum_grammars(grammar_body,grammar_tail)
    
class TreeLOOP(ParsingTreeContainer):
    """ Dynamic list, zero or more repetitions """

    @classmethod
    def get_buffer(cls):
        return BufferList()

    def process(self,grammar_body,grammar_tail):
        grammar_body = ZeroOrMore(grammar_body)
        return sum_grammars(grammar_body,grammar_tail)

class TreeFIXCOL(ParsingTree): # TODO: Make it a child ParsingTreeCollection (needs some refactoring!)
    """
    Class for parsing fixed-width fields using Jeanny markup.
    This class by default produces a single dictionary item.
    To obtain a list if items to convert to Jeanny3 collection,
    use the enclosing LOOP tag.
    """    

    @classmethod
    def get_buffer(cls):
        return BufferList()

    def getGrammar(self):
                        
        grammar_body,grammar_tail = self.collect_grammar_fixcol()  # the only difference with ParsingTreeCollection is this line      
        
        grammar = self.process(grammar_body,grammar_tail)

        # attach a trigger to group, if parent is not None
        if self.__parent__ is not None:                    
            
            def move_to_parent(self):
                parent = self.__parent__ 
                key = self.__varname__
                buf = self.__buffer__
                _print('============================')
                _print('move_to_parent>>>self.__tag__',self.__tag__)
                _print('move_to_parent>>>parent.__tag__',parent.__tag__)
                _print('move_to_parent>>>parent.__varname__',parent.__varname__)
                _print('move_to_parent>>>key',key)
                _print('move_to_parent>>>buf',buf.__buffer__)
                _print('============================')
                parent.__buffer__.relocate_buffer(key,buf)
            
            grammar.setParseAction(lambda tokens: move_to_parent(self))
                
        _print('ParsingTreeFIXCOL.getGrammar>>>self.__tag__',self.__tag__)
        _print('ParsingTreeFIXCOL.getGrammar>>>self.__varname__',self.__varname__)
        if self.__parent__:
            _print('ParsingTreeFIXCOL.getGrammar>>>self.__parent__.__tag__',self.__parent__.__tag__)
        _print('ParsingTreeFIXCOL.getGrammar>>>grammar',grammar)

        return grammar
        
    def collect_grammar_fixcol(self):
        """
        Create a grammar from the specially formatted column-fixed Jeanny3 markup.
        The markup has the following format (types can be omitted):
        
        //HEADER
        0 Column0 Type0
        1 Column1 Type1
        ...
        N ColumnN TypeN
        
        //DATA
        0___1___2____.....N______
        
        In the data buffer, comments are marked with hashtag (#) and ignored.
        """
        TYPES = {'float':float,'int':int,'str':str}        
                
        # initialization
        f = io.StringIO(self.__text__)
        buf = self.__buffer__
                
        def trigger_factory(buf,types):
            def add_to_buffer(tokens):         
                dct = tokens.as_dict()
                item = {key:types[key](dct[key]) for key in dct}
                buf.insert(None,item)
            return add_to_buffer
    
        # Search for //HEADER section.    
        for line in f:
            if '//HEADER' in line: break
    
        # Scan //HEADER section.     
        HEAD = {}        
        for line in f:
            line = line.strip()
            if not line: continue
            if line[0]=='#': continue
            if '//DATA' in line: break
            vals = [_ for _ in line.split() if _]
            token = vals[0]
            if token in HEAD:
                raise Exception('ERROR: duplicate key was found: %s'%vals[0])
            vtype = TYPES[vals[2].lower()] if len(vals)>2 else str           
            HEAD[token] = {}
            HEAD[token]['token'] = token
            HEAD[token]['name'] = vals[1]
            HEAD[token]['type'] = vtype # vtype
                        
        # Get tokenized mark-up.
        for line in f:
            widths = line.rstrip(); break # readline doesn't work because of the "Mixing iteration and read methods"
        matches = re.finditer('([^_]+_*)',widths)
        tokens = []; names = []
        for match in matches:
            i_start = match.start()
            i_end = match.end()
            token = re.sub('_','',widths[i_start:i_end])
            if token not in HEAD: continue                
            tokens.append(token)
            names.append(HEAD[token]['name'])
            HEAD[token]['i_start'] = i_start
            HEAD[token]['i_end'] = i_end
        #markup = re.findall('([^_]+_*)',widths) # doesn't give indexes
        
        # create a list of grammars and attach triggers
        regex = ''
        types = {}
        for token in HEAD:      
            type_ = HEAD[token]['type']
            key = HEAD[token]['name']
            i_start = HEAD[token]['i_start']
            i_end = HEAD[token]['i_end']
            length = i_end-i_start
            regex += '(?P<%s>.{%d})'%(key,length)
            types[key] = type_
            _print('======================================')
            _print('collect_grammar_fixcol>>>loop>>token',token)
            _print('collect_grammar_fixcol>>>loop>>key',key)
            _print('collect_grammar_fixcol>>>loop>>type_',type_)
            _print('collect_grammar_fixcol>>>loop>>i_start',i_start)
            _print('collect_grammar_fixcol>>>loop>>i_end',i_end)
            _print('collect_grammar_fixcol>>>loop>>length',length)            
            _print('======================================')
        
        #regex = '^' + regex + '$'
        #regex = '^' + regex
        _print('collect_grammar_fixcol>>>loop>>regex',regex)
            
        add_to_buffer = trigger_factory(buf,types) # produce with factory (proper closures!!)
            
        # make a single grammar for body
        grammar_body = Regex(regex)
        grammar_body.setParseAction(add_to_buffer)
        _print('collect_grammar_fixcol>>>grammar_body',grammar_body)
        
        # combine grammar body to weed out extra spaces
        #grammar_body = Combine(grammar_body) 
        #_print('collect_grammar_fixcol>>>Combine(grammar_body)',grammar_body)
        
        #grammar_body = LineStart() + grammar_body + LineEnd()
        #grammar_body = LineEnd() + grammar_body
        
        #grammar_body = grammar_body.leaveWhitespace() # THIS IS NECESSARY!!!

        #grammar_body = ZeroOrMore(LineEnd()+grammar_body).leaveWhitespace()
        grammar_body = ZeroOrMore(EOL+grammar_body).leaveWhitespace()

        # create a tail grammar, if present
        if self.__tail__ is not None:
            grammar_tail = self.__tail__.strip()
        else:
            grammar_tail = None
            
        _print('collect_grammar>>>grammar_tail',grammar_tail)
                        
        return grammar_body,grammar_tail        

    def process(self,grammar_body,grammar_tail):
        return sum_grammars(grammar_body,grammar_tail)

class ParsingTreeAux(ParsingTree):
    """
    Abstract class for non-container tags (optional, eol etc...).
    """    

    @classmethod
    def get_buffer(cls):
        return BufferStub()

    def getGrammar(self):                
        grammar_body,grammar_tail = self.collect_grammar_from_children()
        grammar = self.process(grammar_body,grammar_tail)
        _print('ParsingTreeAux.getGrammar>>>grammar',grammar)
        return grammar

class TreeOPTIONAL(ParsingTreeAux):
    
    def process(self,grammar_body,grammar_tail):
        grammar_body = Optional(grammar_body)
        return sum_grammars(grammar_body,grammar_tail)

class TreeEOL(ParsingTreeAux):

    def process(self,grammar_body,grammar_tail):
        grammar = sum_grammars(grammar_body,grammar_tail)
        if grammar:
            return EOL+grammar
        else:
            return EOL

class TreeLEAVEWHITESPACE(ParsingTreeAux): 
    
    def process(self,grammar_body,grammar_tail):
        grammar_body = grammar_body.leaveWhitespace()
        return sum_grammars(grammar_body,grammar_tail)

class TreeCOMBINE(ParsingTreeAux): 
    
    def process(self,grammar_body,grammar_tail):
        grammar_body = Combine(grammar_body)
        return sum_grammars(grammar_body,grammar_tail)

class TreeGROUP(ParsingTreeAux): 
    
    def process(self,grammar_body,grammar_tail):
        grammar_body = Group(grammar_body)
        return sum_grammars(grammar_body,grammar_tail)

DISPATCHER = {
    'FLOAT': TreeFLOAT,
    'INT': TreeINT,
    'STR': TreeSTR,
    'DICT': TreeDICT,
    'LIST': TreeLIST,
    'LOOP': TreeLOOP,
    'OPTIONAL': TreeOPTIONAL,
    'EOL': TreeEOL,
    'LINEEND': TreeEOL,
    'LITERAL': TreeLITERAL,
    'WORD':TreeWORD,
    'RESTOFLINE': TreeRESTOFLINE,
    'REGEX': TreeREGEX,
    'TEXT': TreeTEXT,
    'FIXCOL': TreeFIXCOL,
    'LEAVEWHITESPACE': TreeLEAVEWHITESPACE,
    'COMBINE': TreeCOMBINE,
    'GROUP': TreeGROUP,
}

# MAIN INTERFACE FUNCTIONS

def create_from_xml_node(xmlroot):
    """
    Create parsing tree from the XML tree node object.
    """
    return ParsingTree.create_tree(xmlroot)

def create_from_xml_tree(xmltree): # main function
    """
    Create parsing tree from the XML tree object.
    """
    xmlroot = xmltree.getroot()
    return create_from_xml_node(xmlroot)

def create_from_file(fileobj):
    """
    Create parsing tree from the plain XML text.
    Fileobj can be both filename and object similar to TextIOWrapper.
    """
    xmltree = ET.parse(fileobj)
    return create_from_xml_tree(xmltree)
                
def create_from_text(textbuf):
    """
    Create parsing tree from the plain XML text.
    """
    with io.StringIO(textbuf) as f:
        return create_from_file(f)

def get_data(parsingtree):
    """
    Wrapper function for the get_data() method of ParsingTree child class. 
    """    
    return parsingtree.get_data()
