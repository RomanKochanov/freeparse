import io
import re
import json
#import cPyparsing as pp
import pyparsing

from copy import deepcopy

from functools import reduce
from itertools import cycle

#from cPyparsing import (LineEnd, Literal, Empty, Word, 
#    printables, ZeroOrMore, Optional, Group, restOfLine, 
#    Regex, Combine, LineStart, ParserElement, OneOrMore,
#    White, StringEnd)

#import pyparsing.common as pyparsing_common
#from cPyparsing import pyparsing_common

import xml.etree.ElementTree as ET

#ParserElement.enablePackrat() # enable caching

#SOL = LineStart()
#EOL = LineEnd()
#EMPTY = Empty()
#WHITE = White() # not only space, but tab + other whitespace symbols
#WHITESPACE = Literal(' ').leaveWhitespace() # only whitespace
#EOF = StringEnd()

VARSPACE = {
    'VERBOSE': False,
    'BREAKPOINTS': False,
    'DEBUG': False,
}

# Set default whitespace characters.
#ParserElement.set_default_whitespace_chars(' \t')
##ParserElement.setDefaultWhitespaceChars(' \t')
#ParserElement.set_default_whitespace_chars(' \t\n') # default

def _print(*args):
    if VARSPACE['VERBOSE']: print(*args)

class GenerationError(Exception):
    "Raised when the raw file generation has been failed"
    pass

# Custom converting to float
def convert_to_float(tokens):
    """ intended to be used in pyparsing_common_ only """
    val = tokens[0]
    # DAMN YOU FORTRAN!!!
    try:
        return float(val)
        #return pyparsing_common.convert_to_float(val)
    except ValueError: # this can happen when float number contains D-exponent
        val = val.lower().replace('d','e')
        #return pyparsing_common.convert_to_float(val)
        return float(val)

# Custom pyparsing_common class to parse Fortran-generated floats (D-exponents)
#class pyparsing_common_(pyparsing_common):    
#    sci_real = (
#        Regex(r"[+-]?(?:\d+(?:[eEdD][+-]?\d+)|(?:\d+\.\d*|\.\d+)(?:[eEdD][+-]?\d+)?)")
#        .setName("real number with scientific notation")
#        .setParseAction(convert_to_float)
#    )

#ppc = pyparsing_common # default set of parsers
##ppc = pyparsing_common_ # custom set of parsers

class Parser:
    
    """ 
    Interface for two similar parsing libraries:
           ->  pyparsing (default)
           ->  cPyparsing (compiled version of pyparsing)
    """
    
    def __init__(self,parser_module):
                
        self.LineEnd = parser_module.LineEnd
        self.Literal = parser_module.Literal
        self.Empty = parser_module.Empty
        self.Word = parser_module.Word
        self.printables = parser_module.printables
        self.ZeroOrMore = parser_module.ZeroOrMore
        self.Optional = parser_module.Optional
        self.Group = parser_module.Group
        self.restOfLine = parser_module.restOfLine
        self.Regex = parser_module.Regex
        self.Combine = parser_module.Combine
        self.LineStart = parser_module.LineStart
        self.ParserElement = parser_module.ParserElement
        self.OneOrMore = parser_module.OneOrMore
        self.White = parser_module.White
        self.StringEnd = parser_module.StringEnd
        
        self.SOL = self.LineStart()
        self.EOL = self.LineEnd()
        self.EMPTY = self.Empty()
        self.WHITE = self.White() # not only space, but tab + other whitespace symbols
        self.WHITESPACE = self.Literal(' ').leaveWhitespace() # only whitespace
        self.EOF = self.StringEnd()
        
        parser_module.ParserElement.setDefaultWhitespaceChars(' \t')
        
        class pyparsing_common_(parser_module.pyparsing_common):    
            sci_real = (
                self.Regex(r"[+-]?(?:\d+(?:[eEdD][+-]?\d+)|(?:\d+\.\d*|\.\d+)(?:[eEdD][+-]?\d+)?)")
                    .setName("real number with scientific notation")
                    .setParseAction(convert_to_float)
            )
            
        self.ppc = pyparsing_common_ # custom set of parsers
        
        self.pp = parser_module

try:
    import cPyparsing
    VARSPACE['PARSER'] = Parser(cPyparsing)
except ImportError:
    print('FreeParse: could not import cPyparsing')
    VARSPACE['PARSER'] = Parser(pyparsing)

V = VARSPACE
print('FreeParse: using %s as a core parser module (on import)'%V['PARSER'].pp.__name__)

# FORMAT PROCESSORS FOR GENERATION OF VALUE-BASED TAGS
class Formatter:
    
    @classmethod
    def create(self,tree):
        
        #assert isinstance(tree,ParsingTreeValue)
        if not isinstance(tree,ParsingTreeValue):
            return None
        
        fmt = tree.__xmlroot__.get('format')
        if fmt:
            #buf = fmt%data
            formatter_name = tree.__xmlroot__.get('formatter')
            if not formatter_name: formatter_name = 'python_percent'
        else:
            formatter_name = 'python_str'
        
        return DISPATCHER_FORMATTERS[formatter_name](tree)
        
    def __init__(self,tree):
        raise NotImplementedError
    
    def write(cls,fmt,data):
        raise NotImplementedError

class Formatter_PYTHON_STR(Formatter):

    def __init__(self,tree):
        self.__tree__ = tree

    def write(self,data):
        return self.__tree__.to_str(data)

class Formatter_PYTHON_PERCENT(Formatter):
    
    def __init__(self,tree):
        self.__tree__ = tree
        self.__fmt__ = tree.__xmlroot__.get('format')

    def write(self,data):
        return self.__fmt__%data

class Formatter_FORTRANFORMAT(Formatter):

    def __init__(self,tree):
        import fortranformat as ff
        self.__tree__ = tree
        self.__fmt__ = tree.__xmlroot__.get('format')
        self.__writer__ = ff.FortranRecordWriter(self.__fmt__)

    def write(self,data):
        return self.__writer__.write([data])

# DATA ITERATOR
class DataIterator():
    
    def __init__(self,data):
        self.__data__ = data
        self.__datatype__ = type(data)
        self.__vars__ = {}
        self.__vars__['isempty'] = False        
        if self.__datatype__ in {list,tuple}:
            self.__vars__['index'] = 0
            if len(data)==0: self.__vars__['isempty'] = True
        elif self.__datatype__ in {dict}:
            self.__vars__['allkeys'] = set(data.keys())
            self.__vars__['usedkeys'] = set()
            #self.__index__ = None
            if len(data)==0: self.__vars__['isempty'] = True
        
    def next(self,key=None):
        if self.__datatype__ in {list,tuple}:
            self.__vars__['index'] += 1
            if self.__vars__['index']>=len(self.__data__):
                self.__vars__['isempty'] = True
                _print('DataIterator.next>>>EMPTY LIST!')
            return self.__data__[self.__vars__['index']-1]
        elif self.__datatype__ in {dict}:
            self.__vars__['usedkeys'].add(key)
            if not self.__vars__['allkeys'] - self.__vars__['usedkeys']:
                self.__vars__['isempty'] = True
                _print('DataIterator.next>>>EMPTY DICT!')
            return self.__data__[key]
        else:
            raise Exception('unknown type for DataIterator: "%s"'%self.__datatype__)
            
    def is_empty(self):
        return self.__vars__['isempty']
        
    def copy(self):
        obj = DataIterator(self.__data__)
        obj.__vars__ = deepcopy(self.__vars__)
        return obj
        
    def getall(self):
        return self.__data__
        
    def __repr__(self):
        return 'DataIterator(type=%s,index=%s)'%(self.__datatype__,self.__vars__.get('index'))

class Buffer:
    
    def __init__(self):
        raise NotImplementedError
    
    def insert(self,key,value):
        raise NotImplementedError
    
    def flush_data(self):
        raise NotImplementedError
        
    def clear(self):
        buf = self.__buffer__
        if type(buf) in {list,dict}:
            buf.clear()
        elif type(buf) is type(None):
            pass
        else:
            raise Exception('Buffer.clear: Unknown buffer type "%s"'%type(buf))
        
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

def process_text(txt): # for initialize tag
    if not txt: return txt
    if txt[0]=='\n': return txt[1:]
    return txt

def process_tail(txt): # for initialize tag
    if not txt: return txt
    if txt[0]=='\n': return txt[1:]
    return txt

def remove_leading_eol(txt): # for generate_ method of ParsingTree
    if not txt: return txt
    if txt[0]=='\n': return txt[1:]
    return txt

def process_text_(txt): # for generate_ method of ParsingTree
    if not txt: return txt
    lines = txt.split('\n')
    lines = [line.lstrip() for line in lines]
    txt = '\n'.join(lines)
    return txt

def strip_new_lines(txt): 
    """ Remove heading and trailing new lines,
        remove spaces on trailing and heading empty lines,
        keep all spaces on lines with text.
        IT'S NOT THE SAME AS .STRIP('\n') !!!
    """

    #if not txt: return txt
    if not txt or not txt.strip(): return ''

    def fifnol(txt,forward=True):
        """ Find first non-empty line either from beginning 
            or from end, return index """
        i,step = (0,1) if forward else (-1,-1)
        ieol = i
        while -len(txt)<=i<len(txt) and txt[i] in {' ','\n'}:
            if txt[i]=='\n': ieol = i
            i += step
        i = ieol + step if txt[ieol]=='\n' else ieol
        return i
    
    istart = fifnol(txt,forward=True)
    iend = fifnol(txt,forward=False)
    
    if iend==-1:
        result = txt[istart:]
    else:
        result = txt[istart:iend+1]
    
    return result

def split_list(lst,separator):
    from itertools import groupby
    chunks = [list(g) for k,g in groupby(lst, key=lambda x: x != separator) if k]
    return chunks

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

        cls_ = DISPATCHER_TAGS[xmlroot.tag]
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
        #self.__text__ = process_text(xmlroot.text)
        #self.__tail__ = process_tail(xmlroot.tail)
        self.__text__ = strip_new_lines(xmlroot.text)
        self.__tail__ = strip_new_lines(xmlroot.tail)
        self.__varname__ = xmlroot.get('name')
        self.__children__ = [] # each child is a tag
        self.__formatter__ = Formatter.create(self)
        
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
        
        gg = [g for g in gg if g] # get rid of empty grammars     
        grammar_body = reduce(lambda x,y:x+y,gg) if gg else None
        
        _print('collect_grammar_from_children>>>grammar_body',grammar_body)
    
        # append tail grammar, if present
        if self.__tail__ is not None:
            grammar_tail = self.__tail__.strip()
        else:
            grammar_tail = None
            
        _print('collect_grammar_from_children>>>grammar_tail',grammar_tail)
                        
        return grammar_body,grammar_tail
        
    def generate(self,data):
        dataiter = DataIterator(data)
        buf = self.generate_(dataiter)
        return buf
        #print('GENERATE:')
        #print(buf)
        #buf = [s for s in buf if s]
        #buf = split_list(buf,'\n')
        #lines = [' '.join(b) for b in buf]
        #return '\n'.join(lines)
    
    def generate_(self,dataiter):
        """
        Tries to generate a "raw" file from data structure using stored format.
        This is needed to have a full cycle "parse->analyze->substitute->generate".
        """
        
        _print('breakpoint ParsingTree.generate_>>>BEGIN:')
        if VARSPACE['BREAKPOINTS']: breakpoint()
        
        _print('-------------------------- generate_ --------------------------')
        _print('ParsingTree.generate_>>>self.__tag__',self.__tag__)
        _print('ParsingTree.generate_>>>self.__varname__',self.__varname__)
        _print('ParsingTree.generate_>>>dataiter',dataiter)
        _print('ParsingTree.generate_>>>dataiter.getall()',dataiter.getall())
        _print('---------------------------------------------------------------')
        
        buf = ''
        #buf = []
        
        #if self.__text__: buf += self.__text__
        #if self.__text__: _print('ParsingTree.generate_>>>self.__text__',self.__text__)
        
        # generate buffer for vale-type tags
        try:
            
            _print('breakpoint ParsingTree.generate_>>>try>>>1:')
            if VARSPACE['BREAKPOINTS']: breakpoint()
            
            selfbuf = self.genval(dataiter) # -> if tag=FLOAT, STR, INT etc...
            _print('ParsingTree.generate_>>>selfbuf',selfbuf)
            buf += selfbuf
            #buf.append(selfbuf)
        except GenerationError:
            
            _print('breakpoint ParsingTree.generate_>>>except>>>1:')
            if VARSPACE['BREAKPOINTS']: breakpoint()
            
            self.handle_generation_error()
            
        while self.__children__ and not dataiter.is_empty():
            
            _print('breakpoint ParsingTree.generate_>>>while>>>1:')
            if VARSPACE['BREAKPOINTS']: breakpoint()

            #if dataiter.is_empty(): break
            
            if self.__text__: 
                #text = remove_leading_eol(self.__text__)
                #text = process_text_(text)
                #buf += text
                #buf.append(text)
                buf += self.__text__
            
            if self.__text__: _print('ParsingTree.generate_>>>while>>>self.__text__',self.__text__)
                                                            
            for el in self.__children__:
                
                _print('breakpoint ParsingTree.generate_>>>while>>>for>>>1:')
                if VARSPACE['BREAKPOINTS']: breakpoint()
                
                _print('ParsingTree.generate_>>>while>>>for>>el.__tag__',el.__tag__)
                _print('ParsingTree.generate_>>>while>>>for>>el.__varname__',el.__varname__)
                _print('ParsingTree.generate_>>>while>>>for>>dataiter',dataiter)
                _print('ParsingTree.generate_>>>while>>>for>>dataiter.getall()',dataiter.getall())
                
                dataiter_child = el.dataiter_next(dataiter)
                                        
                _print('ParsingTree.generate_>>>while>>>for>>dataiter_child.getall()',dataiter_child.getall())
                #if not dataiter_child: continue
                try:
                    
                    _print('breakpoint ParsingTree.generate_>>>while>>>for>>>try>>>1:')
                    if VARSPACE['BREAKPOINTS']: breakpoint()
                    
                    #elbuf = el.generate_(dataiter_child.copy()) #????
                    elbuf = el.generate_(dataiter_child) #????
                    _print('ParsingTree.generate_>>>while>>>for>>try>>dataiter',dataiter)
                    _print('ParsingTree.generate_>>>while>>>for>>try>>elbuf',elbuf)
                    buf += elbuf
                    #if dataiter.is_empty(): break
                except (GenerationError, KeyError):
                    # do something if failed to generate from children (important for "optional" tag)
                    _print('breakpoint ParsingTree.generate_>>>while>>>for>>>except>>>1:')
                    if VARSPACE['BREAKPOINTS']: breakpoint()
                    el.handle_generation_error()

                if el.__tail__: 
                    #tail = process_text_(el.__tail__)
                    #buf += tail
                    #buf.append(tail)
                    buf += el.__tail__
                if el.__tail__: _print('ParsingTree.generate_>>>while>>>for>>>el.__tail__',el.__tail__)
                    
            if self.__stop_criteria__(dataiter): break # stopping criteria for each tag
        
        #if self.__tail__: 
        #    tail = process_text_(self.__tail__)
        #    #buf += tail
        #    buf.append(tail)
        #    #buf += self.__tail__
        #if self.__tail__: _print('ParsingTree.generate_>>>self.__tail__',self.__tail__)
        
        _print('breakpoint ParsingTree.generate_>>>END:')
        if VARSPACE['BREAKPOINTS']: breakpoint()
        
        return buf
        
    def __stop_criteria__(self,dataiter):
        return True
        
    def dataiter_next(self,dataiter):
        obj = dataiter.next(self.__varname__)
        _print('%s.dataiter_next>>>tag'%self.__class__.__name__,self.__tag__)
        _print('%s.dataiter_next>>>dataiter(before)'%self.__class__.__name__,dataiter)
        dataiter_child = DataIterator(obj)
        _print('%s.dataiter_child.getall()>>>dataiter(after)'%self.__class__.__name__,dataiter_child.getall())
        _print('%s.dataiter_next>>>dataiter(after)'%self.__class__.__name__,dataiter)
        return dataiter_child
                
    def print_tree(self,level=0,show_buffer=False):
        print('\n'+("=="*level),self.__tag__,self.__varname__)
        if show_buffer:
            self.__buffer__.pretty_print(margin=2*level)
        for child in self.__children__:
            child.print_tree(level=level+1,show_buffer=show_buffer)
                        
    def insert_to_buffer(self,key,value):
        self.__buffer__.insert(key,value)
        
    def clear_buffer(self):
        """ recursively clear the buffer """
        self.__buffer__.clear()
        for el in self.__children__:
            el.clear_buffer()
        
    def get_data(self):
        return self.__buffer__.__buffer__
    
    @property
    def grammar(self):
        if not self.__grammar__:
            self.__grammar__ = self.getGrammar()
        return self.__grammar__
        
    def create_grammar(self):
        self.__grammar__ = self.getGrammar()
        
    def parse_string(self,buf,parse_all=False):
        self.clear_buffer()
        #self.grammar.parse_string(buf,parse_all=parse_all)
        self.grammar.parseString(buf)
        
    def parse_file(self,fileobj,encoding='utf-8',parse_all=False):
        enc = encoding
        if type(fileobj) is str:
            with open(fileobj,encoding=enc) as f:
                buf = f.read()
        else:
            enc_ = fileobj.encoding
            assert enc_==enc,'%s <> %s'%(enc_,enc)
            buf = fileobj.read()
        self.parse_string(buf,parse_all=parse_all)
                
    def getGrammar(self):
        raise NotImplementedError

    def init_grammar(self):
        raise NotImplementedError

    def post_process(self):
        raise NotImplementedError
        
    #def get_data_generator(self,data):
    #    raise NotImplementedError
    
    def handle_generation_error(self):
        _print('%s.handle_generation_error'%self.__class__.__name__)
        raise GenerationError
        
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
        grammar.addParseAction(lambda tokens: type_(tokens[0]))
        
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
        
        if VARSPACE['DEBUG'] and grammar: grammar.set_debug()
        
        return grammar
        
    #def generate(self,data):
    #    _print('ParsingTreeValue.generate>>>tag',self.__tag__)
    #    _print('ParsingTreeValue.generate>>>data',data)
    #    # Do a common type comparison check.
    #    self_type = self.get_type()
    #    data_type = type(data)
    #    _print('ParsingTreeValue.generate>>>data_type',data_type)
    #    if self_type!=data_type:
    #        raise GenerationError('%s <> %s for %s'%(self_type,data_type,self.__tag__))
    #    # Do a type-specific check.
    #    self.check_data(data) 
    #    buf = str(data)
    #    _print('ParsingTreeValue.generate>>>buf=data',buf)
    #    if self.__tail__: 
    #        buf += process_tail(self.__tail__)
    #    _print('ParsingTreeValue.generate>>>buf=data+tail',buf)
    #    return buf
    
    def genval(self,dataiter):
        data = dataiter.getall()
        _print('%s.genval>>>tag'%self.__class__.__name__,self.__tag__)
        _print('%s.genval>>>data'%self.__class__.__name__,data)
        self_type = self.get_type()
        data_type = type(data)
        _print('%s.genval>>>data_type'%self.__class__.__name__,data_type)
        if self_type!=data_type:
            raise GenerationError('%s <> %s for %s'%(self_type,data_type,self.__tag__))
        # Do a type-specific check.
        self.check_data(data)
        buf = self.__formatter__.write(data)
        _print('%s.genval>>>buf'%self.__class__.__name__,buf)
        return buf
        
    def to_str(self,data):
        return str(data)
        
    def check_data(self,data):
        pass
        
class TreeFLOAT(ParsingTreeValue):
    
    def init_grammar(self):
        #return ppc.number()
        return V['PARSER'].ppc.sci_real()
    
    def get_type(self):
        return float
            
class TreeINT(ParsingTreeValue):

    def init_grammar(self):
        #return ppc.number()
        return V['PARSER'].ppc.signed_integer()
    
    def get_type(self):
        return int

class TreeNUMBER(ParsingTreeValue):
    
    TYPES = {
        'int': int,
        'float': float,
    }

    def init_grammar(self):
        return V['PARSER'].ppc.number()
    
    def get_type(self):
        typ = self.__xmlroot__.get('type')
        if typ: return self.__class__.TYPES[typ.lower()]
        return float

class TreeFORTRAN(TreeNUMBER):
    
    """ Fortran-formatted numbers, e.g. 1.e-10, 1.2-307 etc... """
    
    def init_grammar(self):
        return V['PARSER'].Regex('[+-]?(?:\.|\d+\.?)\d*([de][+-]?\d+)?(_[a-z\d]+)?')
        
    def get_type(self): # TODO!!!
        raise NotImplementedError
    
class TreeBUFFER(ParsingTreeValue):
    
    TYPES = {
        'int': int,
        'float': float,
        'str': str,
    }

    def init_grammar(self):
        nchars = self.__xmlroot__.get('nchars')
        if not nchars: raise Exception('BUFFER tag requires "nchars"'
            ' parameter to be supplied')
        nchars = int(nchars)
        return V['PARSER'].Regex('.{%d}'%nchars).leaveWhitespace()
    
    def get_type(self):
        typ = self.__xmlroot__.get('type')
        if typ: return self.__class__.TYPES[typ.lower()]
        return str

class TreeSTR(ParsingTreeValue):

    def init_grammar(self):
        return V['PARSER'].Word(V['PARSER'].printables)
    
    def get_type(self):
        return str

class TreeLITERAL(ParsingTreeValue):

    def init_grammar(self):
        inp = self.__xmlroot__.get('input')
        if not inp: raise Exception('LITERAL tag must '
                'have "input" parameter specified')
        return V['PARSER'].Literal(inp)
    
    def get_type(self):
        return str

    def check_data(self,data):
        inp = self.__xmlroot__.get('input')
        if inp != data:
            raise GenerationError('"%s" <> "%s" for %s'%(inp,data,self.__tag__))

class TreeWORD(ParsingTreeValue):

    def init_grammar(self):
        inp = self.__xmlroot__.get('input')
        #if not inp: inp = printables
        #if not inp: inp = pyparsing_unicode.printables
        #if not inp: inp = pp.unicode.printables
        if not inp: inp = V['PARSER'].pp.unicode.printables
        return V['PARSER'].Word(inp)
    
    def get_type(self):
        return str

    def check_data(self,data):
        inp = self.__xmlroot__.get('input')
        if not set(data).issubset(inp):
            raise GenerationError('"%s" is not a word of "%s" for %s'%(data,inp,self.__tag__))

class TreeRESTOFLINE(ParsingTreeValue):
    
    def init_grammar(self):
        return V['PARSER'].restOfLine()
    
    def get_type(self):
        return str
     
    #def to_str(self,data): # rest of line takes extra space when generated back to string buffer
    #    if data and data[0]==' ':
    #        return data[1:]
    #    return data

class TreeREGEX(ParsingTreeValue):

    def init_grammar(self):
        regex = self.__xmlroot__.get('input')
        if not regex: 
            raise Exception('regex is empty')
        return V['PARSER'].Regex(regex)
    
    def get_type(self):
        return str
        
    def post_process(self,grammar):
        return V['PARSER'].Group(grammar)

    def check_data(self,data):
        regex = self.__xmlroot__.get('input')
        if not re.match(regex,data):
            raise GenerationError('regex(%s) for %s not matched: "%s"'%(regex,self.__tag__,data))

class TreeTEXT(ParsingTreeValue):

    def init_grammar(self):
        begin = self.__xmlroot__.get('begin')
        end = self.__xmlroot__.get('end')
        if not (begin and end): 
            raise Exception('text should have both "begin" and "end" fields')
        regex = begin+'[\s\S]*'+end
        return V['PARSER'].Regex(regex)
    
    def get_type(self):
        return str

    def post_process(self,grammar):
        return V['PARSER'].Group(grammar)

    def check_data(self,data):        
        begin = self.__xmlroot__.get('begin')
        end = self.__xmlroot__.get('end')
        if not (begin and end): 
            raise Exception('text should have both "begin" and "end" fields')
        regex = begin+'[\s\S]*'+end        
        if not re.match(regex,data):
            raise GenerationError('regex(%s) for %s not matched: "%s"'%(regex,self.__tag__,data))

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
            
            grammar = V['PARSER'].Group(grammar) # without this nested structures work badly
            
            grammar.setParseAction(lambda tokens: move_to_parent(self))
                
        _print('ParsingTreeContainer.getGrammar>>>self.__tag__',self.__tag__)
        _print('ParsingTreeContainer.getGrammar>>>self.__varname__',self.__varname__)
        if self.__parent__:
            _print('ParsingTreeContainer.getGrammar>>>self.__parent__.__tag__',self.__parent__.__tag__)
        _print('ParsingTreeContainer.getGrammar>>>grammar',grammar)

        if VARSPACE['DEBUG'] and grammar: grammar.set_debug()

        return grammar

    def genval(self,dataiter):
        data = dataiter.getall()
        _print('%s.genval>>>tag'%self.__class__.__name__,self.__tag__)
        #_print('%s.genval>>>data'%self.__class__.__name__,data)
        self_type = self.get_type()
        data_type = type(data)
        _print('%s.genval>>>data_type'%self.__class__.__name__,data_type)
        if self_type!=data_type:
            raise GenerationError('%s <> %s for %s'%(self_type,data_type,self.__tag__))
        buf = ''
        return buf
        
class TreeDICT(ParsingTreeContainer):
    """ Dictionary """
    
    @classmethod
    def get_buffer(cls):
        return BufferDict()

    def process(self,grammar_body,grammar_tail):
        return sum_grammars(grammar_body,grammar_tail)

    def get_type(self):
        return dict
        
    #def get_data_generator(self,data):
    #    for el in self.__children__:
    #        key = el.__xmlroot__.get('name')
    #        _print('TreeDICT.get_data_generator>>>el.__tag__',el.__tag__)
    #        _print('TreeDICT.get_data_generator>>>key',key) 
    #        #if key not in data: continue
    #        #data_next = data[key]
    #        data_next = data.get(key)
    #        _print('TreeDICT.get_data_generator>>>data_next',data_next) 
    #        _print('TreeDICT.get_data_generator>>>data_next==None',data_next==None) 
    #        yield el,data_next

class TreeLIST(ParsingTreeContainer):
    """ Static list """

    @classmethod
    def get_buffer(cls):
        return BufferList()

    def process(self,grammar_body,grammar_tail):
        return sum_grammars(grammar_body,grammar_tail)
        
    def get_data_generator(self,data):
        raise NotImplementedError    

    def get_type(self):
        return list

    #def get_data_generator(self,data):
    #    for el,datum in zip(self.__children__,data):    
    #        _print('TreeLIST.get_data_generator>>>el.__tag__',el.__tag__)
    #        _print('TreeLIST.get_data_generator>>>datum',datum)
    #        yield el,datum
    
class TreeLOOP(ParsingTreeContainer):
    """ Dynamic list, zero or more repetitions """

    @classmethod
    def get_buffer(cls):
        return BufferList()

    #def process(self,grammar_body,grammar_tail):
    #    grammar_body = ZeroOrMore(grammar_body)
    #    return sum_grammars(grammar_body,grammar_tail)
    def process(self,grammar_body,grammar_tail):
        miniter = self.__xmlroot__.get('min')
        if not miniter: 
            miniter = ...
        else:
            miniter = int(miniter)
        maxiter = self.__xmlroot__.get('max')
        if not maxiter: 
            maxiter = ...
        else:
            maxiter = int(maxiter)
        grammar_body = grammar_body[miniter,maxiter]
        return sum_grammars(grammar_body,grammar_tail)

    def get_type(self):
        return list
        
    def __stop_criteria__(self,dataiter): # exclusive stopping criteria for loop
        if dataiter.is_empty(): return True
        return False
        
    #def get_data_generator(self,data):        
    #    for el,datum in zip(cycle(self.__children__),data):
    #        _print('TreeLOOP.get_data_generator>>>el._tag__',el.__tag__)
    #        _print('TreeLOOP.get_data_generator>>>datum',datum)
    #        yield el,datum

class ffloat(float): 
    """
    Fortran-type float dealing with peculiarities of the Fortran
    formatting, i.e. "ghost" exponent: "1.426-100"
    """
    
    def __new__(self,value):
        try:
            return float.__new__(self,value)
        except ValueError:
            value = value.strip()
            regex = '^([+-]?\d*\.?\d*)([+-]\d+)$'
            a,b = re.search(regex,value).groups()
            value = float(a)*10**int(b)
            return float.__new__(self,value)
    
    def __init__(self,value):
        float.__init__(value)
        
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

        if VARSPACE['DEBUG'] and grammar: grammar.set_debug()

        return grammar

    def collect_grammar_fixcol(self): 
        
        ###TODO: add a "comment" and "stop" regexes to parameters; comments must be also saved to list as strings
        
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
        TYPES = {'float':float,'int':int,'str':str,'ffloat':ffloat}        
                
        # initialization
        f = io.StringIO(self.__text__)
        buf = self.__buffer__
                
        def trigger_factory(buf,head,restofline):
            def add_to_buffer(tokens): 
                line = tokens[0]        
                item = {}
                for token in head: 
                    head_ = head[token]
                    name = head_['name']
                    type_ = head_['type']
                    i_start = head_['i_start']
                    i_end = head_['i_end']
                    s = line[i_start:i_end]
                    try:
                        val = type_(s)
                    except ValueError as e:
                        mask = head_['mask']
                        if mask is None or s.strip()!=mask:
                            raise(e)
                        else:
                            val = mask
                    item[name] = val
                if restofline is not None:
                    item[restofline] = line[i_end:]
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
            # process masks
            try:
                mask = vals[3]                
            except IndexError:
                mask = None
            HEAD[token]['mask'] = mask                        
            
        # Get tokenized mark-up.
        for line in f:
            widths = line.rstrip(); break # readline doesn't work because of the "Mixing iteration and read methods"
        #matches = re.finditer('([^_]+_*)',widths) # fails when no underscore between columns tokens
        matches = re.finditer('([^_]_*)',widths)
        tokens = []; names = []; line_length = 0
        for match in matches:
            i_start = match.start()
            i_end = match.end()
            token = re.sub('_','',widths[i_start:i_end])
            if token not in HEAD: continue                
            tokens.append(token)
            names.append(HEAD[token]['name'])
            HEAD[token]['i_start'] = i_start
            HEAD[token]['i_end'] = i_end
            line_length += i_end-i_start
        #markup = re.findall('([^_]+_*)',widths) # doesn't give indexes
        
        # create a simpler regular expression
        regex = '.{%d,}'%line_length
        
        #regex = '^' + regex + '$'
        #regex = '^' + regex
        _print('collect_grammar_fixcol>>>loop>>regex',regex)

        restofline = self.__xmlroot__.get('restofline')
            
        add_to_buffer = trigger_factory(buf,HEAD,restofline) # produce with factory (proper closures!!)        
        
        # make a single grammar for body
        grammar_body = V['PARSER'].Regex(regex)

        grammar_body.setParseAction(add_to_buffer)

        _print('collect_grammar_fixcol>>>grammar_body',grammar_body)
        
        if VARSPACE['DEBUG'] and grammar_body: grammar_body.set_debug()
        
        # combine grammar body to weed out extra spaces
        #grammar_body = Combine(grammar_body) 
        #_print('collect_grammar_fixcol>>>Combine(grammar_body)',grammar_body)
        
        #grammar_body = LineStart() + grammar_body + LineEnd()
        #grammar_body = LineEnd() + grammar_body
        
        #grammar_body = grammar_body.leaveWhitespace() # THIS IS NECESSARY!!!

        #grammar_body = ZeroOrMore(LineEnd()+grammar_body).leaveWhitespace()
        
        #grammar_body = ZeroOrMore(EOL+grammar_body).leaveWhitespace() # WORKS, BUT NOT WITH LEADING EOLS
        #grammar_body = ZeroOrMore(EOL) + ZeroOrMore(grammar_body+EOL).leaveWhitespace() # WORKS FOR EOL-UNAWARE PARSING
        
        grammar_body = V['PARSER'].ZeroOrMore(grammar_body+V['PARSER'].EOL).leaveWhitespace() # WORKS FOR EOL-AWARE PARSING
                
        # create a tail grammar, if present
        if self.__tail__ is not None:
            grammar_tail = self.__tail__.strip()
        else:
            grammar_tail = None
            
        _print('collect_grammar>>>grammar_tail',grammar_tail)
        
        # save for using in generate
        self.__types__ = TYPES
        self.__head__ = HEAD
                        
        if VARSPACE['DEBUG'] and grammar_body: grammar_body.set_debug()
                        
        return grammar_body,grammar_tail 

    def process(self,grammar_body,grammar_tail):
        return sum_grammars(grammar_body,grammar_tail)
        
    #def generate(self,data):
    def genval(self,dataiter):
        
        data = dataiter.getall()
        
        TYPES = self.__types__
        HEAD = self.__head__
        
        rol_name = self.__xmlroot__.get('restofline')
        
        #FORMATS = {str:'%%%ds',int:'%%%dd',float:'%%%de'}
        
        tokens = HEAD.keys()
        names = [HEAD[t]['name'] for t in tokens]
        
        buf = ''
        for item in data:
            vals = [item[name] for name in names]
            line = ''
            line_length = 0
            for val,token in zip(vals,tokens):
                name = HEAD[token]['name']
                i_start = HEAD[token]['i_start']
                i_end = HEAD[token]['i_end']
                #type_ = TYPES[name]
                length = i_end-i_start
                b = '%%%ds'%length%str(val)
                assert len(b)==length, 'len("%s")=%d!=%d'%(b,len(b),length)
                buf += b
            # append comment if any:
            if rol_name is not None:
                buf += item[rol_name]
            buf += '\n'
            
        if self.__tail__:
            #tail = process_tail(self.__tail__)
            _print('TreeFIXCOL.generate>>>process_tail(self.__tail__)',tail,type(tail))
            buf += tail
            
        return buf

class TreeFIXCOL2(TreeFIXCOL): # TODO: Make it a child ParsingTreeCollection (needs some refactoring!)
    
    """ OLD LEGACY VERSION, WILL BE DELETED """

    def collect_grammar_fixcol(self): 
        
        ###TODO: add a "comment" and "stop" regexes to parameters; comments must be also saved to list as strings
        
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
                
        def trigger_factory(buf,types,masks):
            def add_to_buffer(tokens):         
                dct = tokens.as_dict()                
                #item = {key:types[key](dct[key]) for key in dct} # without exception handling
                item = {}
                for key in dct: # with exception handling
                    try:
                        val = types[key](dct[key])
                    except ValueError as e:
                        mask = masks[key]
                        if mask is None or dct[key].strip()!=mask:
                            raise(e)
                        else:
                            val = mask
                    item[key] = val
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
            # process masks
            try:
                mask = vals[3]                
            except IndexError:
                mask = None
            HEAD[token]['mask'] = mask                        
            
        # Get tokenized mark-up.
        for line in f:
            widths = line.rstrip(); break # readline doesn't work because of the "Mixing iteration and read methods"
        #matches = re.finditer('([^_]+_*)',widths) # fails when no underscore between columns tokens
        matches = re.finditer('([^_]_*)',widths)
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
        masks = {}
        for token in HEAD:      
            type_ = HEAD[token]['type']
            key = HEAD[token]['name']
            #print(token,'>>>',HEAD[token])
            i_start = HEAD[token]['i_start']
            i_end = HEAD[token]['i_end']
            length = i_end-i_start
            regex += '(?P<%s>.{%d})'%(key,length)
            types[key] = type_
            masks[key] = HEAD[token]['mask']
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

        rol_name = self.__xmlroot__.get('restofline')
            
        if rol_name is not None:
            types[rol_name] = str
            
        add_to_buffer = trigger_factory(buf,types,masks) # produce with factory (proper closures!!)        
        
        # make a single grammar for body
        grammar_body = V['PARSER'].Regex(regex)

        if rol_name is None: # ignore rest of line
            grammar_body = grammar_body.setParseAction(add_to_buffer) + V['PARSER'].restOfLine()
        else:
            grammar_body = (grammar_body + V['PARSER'].restOfLine(rol_name)).setParseAction(add_to_buffer)

        _print('collect_grammar_fixcol>>>grammar_body',grammar_body)
        
        if VARSPACE['DEBUG'] and grammar_body: grammar_body.set_debug()
        
        # combine grammar body to weed out extra spaces
        #grammar_body = Combine(grammar_body) 
        #_print('collect_grammar_fixcol>>>Combine(grammar_body)',grammar_body)
        
        #grammar_body = LineStart() + grammar_body + LineEnd()
        #grammar_body = LineEnd() + grammar_body
        
        #grammar_body = grammar_body.leaveWhitespace() # THIS IS NECESSARY!!!

        #grammar_body = ZeroOrMore(LineEnd()+grammar_body).leaveWhitespace()
        
        #grammar_body = ZeroOrMore(EOL+grammar_body).leaveWhitespace() # WORKS, BUT NOT WITH LEADING EOLS
        #grammar_body = ZeroOrMore(EOL) + ZeroOrMore(grammar_body+EOL).leaveWhitespace() # WORKS FOR EOL-UNAWARE PARSING
        
        grammar_body = V['PARSER'].ZeroOrMore(grammar_body+V['PARSER'].EOL).leaveWhitespace() # WORKS FOR EOL-AWARE PARSING
                
        # create a tail grammar, if present
        if self.__tail__ is not None:
            grammar_tail = self.__tail__.strip()
        else:
            grammar_tail = None
            
        _print('collect_grammar>>>grammar_tail',grammar_tail)
        
        # save for using in generate
        self.__types__ = TYPES
        self.__head__ = HEAD
                        
        if VARSPACE['DEBUG'] and grammar_body: grammar_body.set_debug()
                        
        return grammar_body,grammar_tail     

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
        
        if VARSPACE['DEBUG'] and grammar: grammar.set_debug()
        
        return grammar
        
    def genval(self,dataiter):
        _print('%s.genval>>>tag'%self.__class__.__name__,self.__tag__)
        buf = ''
        return buf
        
    def dataiter_next(self,dataiter):
        #_print('%s.dataiter_next>>>tag'%self.__class__.__name__,self.__tag__,'(SKIPPING)')
        _print('%s.dataiter_next>>>tag'%self.__class__.__name__,self.__tag__,'(UNCHANGED)')
        #return None
        return dataiter        

class TreeOPTIONAL(ParsingTreeAux):
    
    def process(self,grammar_body,grammar_tail):
        grammar_body = V['PARSER'].Optional(grammar_body)
        return sum_grammars(grammar_body,grammar_tail)
        
    def handle_generation_error(self):
        _print('TreeOPTIONAL.handle_generation_error')
        pass

class TreeSOL(ParsingTreeAux):

    def process(self,grammar_body,grammar_tail):
        grammar = sum_grammars(grammar_body,grammar_tail)
        g = V['PARSER'].SOL
        if grammar: g += grammar
        return g

class TreeEOF(ParsingTreeAux):

    def process(self,grammar_body,grammar_tail):
        grammar = sum_grammars(grammar_body,grammar_tail)
        g = V['PARSER'].EOF
        if grammar: g += grammar
        return g

class TreeWhitespace(ParsingTreeAux): # TODO: Similar to TreeEOL. Refactor to a common parent class?

    __nspaces__ = 1

    def process(self,grammar_body,grammar_tail):
        grammar = sum_grammars(grammar_body,grammar_tail)
        g = V['PARSER'].WHITESPACE*self.__nspaces__
        if grammar: g += grammar
        return g
    
    def genval(self,dataiter):
        _print('%s.genval>>>tag'%self.__class__.__name__,self.__tag__)
        buf = ' '*self.__nspaces__
        return buf

class TreeWhitespace2(TreeWhitespace):
    __nspaces__ = 2
class TreeWhitespace3(TreeWhitespace):
    __nspaces__ = 3
class TreeWhitespace4(TreeWhitespace):
    __nspaces__ = 4
class TreeWhitespace5(TreeWhitespace):
    __nspaces__ = 5
class TreeWhitespace6(TreeWhitespace):
    __nspaces__ = 6
class TreeWhitespace7(TreeWhitespace):
    __nspaces__ = 7
class TreeWhitespace8(TreeWhitespace):
    __nspaces__ = 8
class TreeWhitespace9(TreeWhitespace):
    __nspaces__ = 9

class TreeWhitespaces(ParsingTreeAux):
    
    def process(self,grammar_body,grammar_tail):
        grammar = sum_grammars(grammar_body,grammar_tail)
        nspaces = self.__xmlroot__.get('n')
        #if not nspaces: raise Exception('Invalid use of n in SS')
        if nspaces:
            nspaces = int(nspaces)
            g = V['PARSER'].WHITESPACE*nspaces
        else:
            g = V['PARSER'].OneOrMore(V['PARSER'].WHITESPACE)
        if grammar: g += grammar
        return g

    def genval(self,dataiter):
        _print('%s.genval>>>tag'%self.__class__.__name__,self.__tag__)
        nspaces = self.__xmlroot__.get('n')
        #if not nspaces: raise Exception('Invalid use of n in SS')
        if nspaces:
            nspaces = int(nspaces)
            buf = ' '*nspaces
        else:
            buf = ' '
        return buf

class TreeEOL_OLD(ParsingTreeAux):

    #def process(self,grammar_body,grammar_tail):
    #    grammar = sum_grammars(grammar_body,grammar_tail)
    #    if grammar:
    #        return EOL+grammar
    #    else:
    #        return EOL
    
    def process(self,grammar_body,grammar_tail):
        grammar = sum_grammars(grammar_body,grammar_tail)
        return grammar

    #def generate(self,data):
    #    # Do a common type comparison check.
    #    buf = '\n'
    #    tail = process_tail(self.__tail__) if self.__tail__ else ''
    #    buf += tail
    #    _print('TreeEOL.generate>>>tail',tail)
    #    return buf
    
    def genval(self,dataiter):
        _print('%s.genval>>>tag'%self.__class__.__name__,self.__tag__)
        buf = '\n'
        return buf

class TreeEOL(ParsingTreeAux):

    __neols__ = 1

    def process(self,grammar_body,grammar_tail):
        grammar = sum_grammars(grammar_body,grammar_tail)
        g = V['PARSER'].EOL*self.__neols__
        if grammar: g += grammar
        return g
    
    def genval(self,dataiter):
        _print('%s.genval>>>tag'%self.__class__.__name__,self.__tag__)
        buf = '\n'*self.__neols__
        return buf

class TreeEOL2(TreeEOL):
    __neols__ = 2
class TreeEOL3(TreeEOL):
    __neols__ = 3
class TreeEOL4(TreeEOL):
    __neols__ = 4
class TreeEOL5(TreeEOL):
    __neols__ = 5
class TreeEOL6(TreeEOL):
    __neols__ = 6
class TreeEOL7(TreeEOL):
    __neols__ = 7
class TreeEOL8(TreeEOL):
    __neols__ = 8
class TreeEOL9(TreeEOL):
    __neols__ = 9

class TreeEOLS(ParsingTreeAux):
    
    def process(self,grammar_body,grammar_tail):
        grammar = sum_grammars(grammar_body,grammar_tail)
        neols = self.__xmlroot__.get('n')
        #if not neols: raise Exception('Invalid use of n in EOLS')
        if neols:
            neols = int(neols)
            g = V['PARSER'].EOL*neols
        else:
            g = V['PARSER'].OneOrMore(V['PARSER'].EOL)
        if grammar: g += grammar
        return g

    def genval(self,dataiter):
        _print('%s.genval>>>tag'%self.__class__.__name__,self.__tag__)
        neols = self.__xmlroot__.get('n')
        #if not neols: raise Exception('Invalid use of n in EOLS')
        if neols:
            neols = int(neols)
            buf = '\n'*neols
        else:
            buf = '\n'
        return buf

class TreeSKIPLINE(ParsingTreeAux):
    
    def process(self,grammar_body,grammar_tail):
        grammar = sum_grammars(grammar_body,grammar_tail)
        #g = SOL+restOfLine+EOL # this should be right???
        g = V['PARSER'].restOfLine+V['PARSER'].EOL
        if grammar: g += grammar
        return g

    def genval(self,dataiter):
        _print('%s.genval>>>tag'%self.__class__.__name__,self.__tag__)
        buf = '\n'
        return buf

class TreeSKIPLINES(ParsingTreeAux):
    
    def process(self,grammar_body,grammar_tail):
        grammar = sum_grammars(grammar_body,grammar_tail)
        nlines = self.__xmlroot__.get('n')
        if not nlines: raise Exception('n empty in SKIPLINES')
        nlines = int(nlines)
        #g = SOL+restOfLine+EOL # this should be right???
        g = V['PARSER'].restOfLine+V['PARSER'].EOL
        g *= nlines
        if grammar: g += grammar
        return g

    def genval(self,dataiter):
        _print('%s.genval>>>tag'%self.__class__.__name__,self.__tag__)
        nlines = self.__xmlroot__.get('n')
        if not nlines: raise Exception('n empty in SKIPLINES')
        nlines = int(nlines)
        buf = '\n'*nlines
        return buf
    
class TreeLEAVEWHITESPACE(ParsingTreeAux): 
    
    def process(self,grammar_body,grammar_tail):
        grammar_body = grammar_body.leaveWhitespace()
        return sum_grammars(grammar_body,grammar_tail)

class TreeCOMBINE(ParsingTreeAux): 
    
    def process(self,grammar_body,grammar_tail):
        grammar_body = V['PARSER'].Combine(grammar_body)
        return sum_grammars(grammar_body,grammar_tail)

class TreeGROUP(ParsingTreeAux): 
    
    def process(self,grammar_body,grammar_tail):
        grammar_body = V['PARSER'].Group(grammar_body)
        return sum_grammars(grammar_body,grammar_tail)

DISPATCHER_TAGS = {
    'FLOAT': TreeFLOAT,
    'INT': TreeINT,
    'NUMBER': TreeNUMBER,
    'FORTRAN': TreeFORTRAN,
    'STR': TreeSTR,
    'BUFFER': TreeBUFFER,
    'DICT': TreeDICT,
    'LIST': TreeLIST,
    'LOOP': TreeLOOP,
    'OPTIONAL': TreeOPTIONAL,
    'S': TreeWhitespace,
    'S2': TreeWhitespace2,
    'S3': TreeWhitespace3,
    'S4': TreeWhitespace4,
    'S5': TreeWhitespace5,
    'S6': TreeWhitespace6,
    'S7': TreeWhitespace7,
    'S8': TreeWhitespace8,
    'S9': TreeWhitespace9,
    'SS': TreeWhitespaces,
    'EOL': TreeEOL,
    'EOL2': TreeEOL2,
    'EOL3': TreeEOL3,
    'EOL4': TreeEOL4,
    'EOL5': TreeEOL5,
    'EOL6': TreeEOL6,
    'EOL7': TreeEOL7,
    'EOL8': TreeEOL8,
    'EOL9': TreeEOL9,
    'EOLS': TreeEOLS,
    'LINEEND': TreeEOL,
    'SOL': TreeSOL,
    'LINESTART': TreeSOL,
    'EOF': TreeEOF,
    'SKIPLINE': TreeSKIPLINE,
    'SKIPLINES': TreeSKIPLINES,
    'LITERAL': TreeLITERAL,
    'WORD':TreeWORD,
    'RESTOFLINE': TreeRESTOFLINE,
    'REGEX': TreeREGEX,
    'TEXT': TreeTEXT,
    'FIXCOL': TreeFIXCOL,
    'FIXCOL2': TreeFIXCOL2, # legacy (slow)
    'LEAVEWHITESPACE': TreeLEAVEWHITESPACE,
    'COMBINE': TreeCOMBINE,
    'GROUP': TreeGROUP,
}

DISPATCHER_FORMATTERS = {
    'python_str': Formatter_PYTHON_STR,
    'python_percent': Formatter_PYTHON_PERCENT,
    'fortranformat': Formatter_FORTRANFORMAT,
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
