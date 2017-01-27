types = ["short", "int", "long", "float", "double", "char", "void", "bool", "FILE"]
containers = ["enum", "struct", "union", "typedef"]
modifiers = [ "const", "volatile", "extern", "static", "register", "signed", "unsigned"]
flow = [ "if", "else",
         "goto",
         "case", "default",
         "continue", "break", ]
loops = ["for", "do", "while" "switch", ]
keywords = types + containers + modifiers + flow + loops + [ "return", "sizeof" ]


prefix_operations = ["-","+","*","&","~","!","++","--"]
postfix_operations = ["++", "--"]
selection_operations = [".","->"] # Left-to-Right
multiplication_operations = ["*","/","%"] # Left-to-Right
addition_operations = ["+","-"] # Left-to-Right
bitshift_operations = ["<<",">>"] # Left-to-Right
relation_operations = ["<","<=",">",">="] # Left-to-Right
equality_operations = ["==","!="] # Left-to-Right
bitwise_operations = ["&", "^", "|"] # Left-to-Right
logical_operations = ["&&","||"]
ternary_operations = ["?",":"]
# Ternary () ? () : ()
assignment_operations = ["=", # Right-to-Left
                        "+=","-=",
                        "/=","*=","%="
                        "<<=",">>=",
                     "&=","^=","|=",
                    ]
binary_operations = multiplication_operations + \
                    addition_operations + \
                    bitshift_operations + \
                    relation_operations + \
                    equality_operations + \
                    bitwise_operations  + \
                    logical_operations  + \
                    assignment_operations + selection_operations

operators = prefix_operations +  binary_operations + ternary_operations
reserved = keywords + operators

def is_keyword(token):
    return token in keywords

def is_reserved(token):
    return token in reserved
