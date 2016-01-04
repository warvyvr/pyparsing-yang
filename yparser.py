import os
import sys
from pyparsing import *


semi,lbrace,rbrace = map(Suppress,";{}")

#########################################################################
#  common statements definition
#########################################################################

identifier_stmt = Word(alphas+nums+"_-.")

date_stmt = Word(nums+"-")
name_stmt = Word(alphas+"\"-_:"+nums)

dblQContent =  dblQuotedString.setParseAction(removeQuotes)

description_stmt = Suppress(Keyword("description")) + QuotedString('"',multiline=True).setResultsName("description") + semi

revision_date_stmt = Suppress(Keyword("revision-date")) + Word(nums+"@:/ ").setResultsName("revision-date") \
                      + semi

xpath_stmt = dblQContent.setResultsName("xpath")

path_stmt = Suppress(Keyword("path")) + xpath_stmt + semi

#########################################################################
#  module header statements definition
#########################################################################
yang_version_stmt = Group(Suppress(Keyword("yang-version")) + Literal("1").setResultsName("version") \
                    + semi).setResultsName("yang-version)")

namespace_stmt = Suppress(Keyword("namespace")) + name_stmt.setResultsName("namespace") + semi

prefix_stmt= Suppress(Keyword("prefix")) + name_stmt.setResultsName("prefix")+ semi


module_header_stmts = Optional(yang_version_stmt) + OneOrMore(namespace_stmt | prefix_stmt)

#########################################################################
#  linkage statements definition
#########################################################################
import_stmt = Group(Suppress(Keyword("import")) + name_stmt.setResultsName("import_module") + lbrace \
                + prefix_stmt + Optional(revision_date_stmt) + rbrace).setResultsName("import")

include_stmt = Group(Suppress(Keyword("include")) + name_stmt.setResultsName("include_module") + lbrace \
                + prefix_stmt + Optional(revision_date_stmt) + rbrace).setResultsName("include")


linkage_stmts = ZeroOrMore(import_stmt | include_stmt).setResultsName("imports")

#########################################################################
#  meta statements definition
#########################################################################
organization_stmt = Suppress(Keyword("organization")) \
                      + dblQContent.setResultsName("organization") + semi

contact_stmt = Suppress(Keyword("contact")) + dblQContent.setResultsName("contact") + semi

reference_stmt = Suppress(Keyword("reference")) + dblQContent.setResultsName("reference") + semi


meta_stmts = (organization_stmt | contact_stmt | description_stmt | reference_stmt) * (0,4)

#########################################################################
#  revision statements definition
#########################################################################
revision_stmts = Suppress(Keyword("revision")) + date_stmt.setResultsName("revision") \
                  + lbrace \
                    + description_stmt \
                    + reference_stmt \
                  + rbrace


#########################################################################
#  body statements definition
#########################################################################

typedef_name = Word(alphas+nums+"-")

base_type_name = Word(alphas+nums+"-")

typedef_stmt = Group(Suppress(Keyword("typedef")) + typedef_name.setResultsName("typedef_name") + lbrace \
                   + Suppress(Keyword("type")) + base_type_name.setResultsName("basetype_name") + lbrace \
                     + path_stmt          \
                   + rbrace               \
                   + description_stmt     \
                 + rbrace)

typedef_stmt = typedef_stmt.setResultsName("typedef")

#def leaf_convert_to_dict(tokens):
#  print("--->",tokens)
#  return tokens

when_stmt = Suppress(Keyword("when")) + dblQContent \
              + (semi | (lbrace + (reference_stmt|description_stmt)*(1,2) + rbrace))

# an additional paser function to conform range string rule as RFC 6020
numerical_restriction_stmt = Suppress(Keyword("range")) + dblQContent.setResultsName("range") + semi

type_body_stmt = numerical_restriction_stmt 

type_stmt = Suppress(Keyword("type")) + identifier_stmt.setResultsName("type_name") \
              + (semi | (lbrace + type_body_stmt + rbrace))

if_feature_stmt = Suppress(Keyword("if-feature")) + identifier_stmt + semi

# if-feature may occur many times for leaf, we use OneOrMore to allow this, but it doesn't block the 
# singleton item check by default (e.g. when_stmt, type_stmt,...)
leaf_stmt = Group(Suppress(Keyword("leaf")) + identifier_stmt.setResultsName("name") + lbrace \
              + OneOrMore(when_stmt | type_stmt | if_feature_stmt) \
              + Optional(Suppress(Keyword("mandatory")) + Or("true","false") + semi) \
              + Optional(Suppress(Keyword("default")) + Word(alphas+nums+"-\"") + semi) \
            + rbrace).setResultsName("leaf")

key_stmt = Suppress(Keyword("key")) + dblQContent.setResultsName("name") + semi


leaf_list_stmt = Group(Suppress(Keyword("leaf-list")) + identifier_stmt.setResultsName("name") + lbrace \
              + Suppress(Keyword("type")) + Word(alphas+nums+"-").setResultsName("type_name") + semi \
              + Optional(Suppress(Keyword("mandatory")) + Or("true","false") + semi) \
              + Optional(Suppress(Keyword("default")) + Word(alphas+nums+"-\"") + semi) \
            + rbrace).setResultsName("leaf-list")

list_sexp = Forward()

list_stmt = Suppress(Keyword("list")) + identifier_stmt.setResultsName("name") + lbrace \
                + key_stmt \
                + OneOrMore(leaf_stmt | leaf_list_stmt | list_sexp) \
              + rbrace

container_stmt = Suppress(Keyword("container")) + identifier_stmt.setResultsName("name") + lbrace \
                    + ZeroOrMore(leaf_stmt | leaf_list_stmt | list_sexp) \
                  + rbrace

list_sexp << (Group(list_stmt).setResultsName("list") | Group(container_stmt).setResultsName("container"))

data_def_stmt = list_sexp | leaf_stmt | leaf_list_stmt


body_stmts = ZeroOrMore(typedef_stmt | data_def_stmt)

#########################################################################
#  yang parer definition
#########################################################################

yang_parser = Suppress(Keyword("module"))  + name_stmt.setResultsName("module_name") + lbrace  \
                  + module_header_stmts \
                  + linkage_stmts \
                  + meta_stmts \
                  + Optional(revision_stmts) \
                  + body_stmts \
                + rbrace

def parse_yang_file(file_name):
  with open(file_name) as yang_file:
    content = yang_file.read()
    return yang_parser.parseString(content)


if "__main__" == __name__:
  if (len(sys.argv) > 1):
    print(open(sys.argv[1]).read())
    print("")
    print(parse_yang_file(sys.argv[1]))
