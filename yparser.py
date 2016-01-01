import os
import sys
from pyparsing import *

#TODO
# 1.xpath string doesn't define well
# 2.namespace string doesn't define well
# 3.description doesn't support multi-lines way.


semi,lbrace,rbrace = map(Suppress,";{}")

#double quotation marks
dqm = Suppress(Literal('"'))

def removeColon(token):
	print(token)
	return token[:-1]

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


module_header_stmts = Optional(yang_version_stmt) + OneOrMore((namespace_stmt | prefix_stmt))

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

reference_stmt = Group(Suppress(Keyword("reference")) + dblQContent.setResultsName("reference") + semi)


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

leaf_stmt = Suppress(Keyword("leaf")) + identifier_stmt.setResultsName("name") + lbrace \
              + Suppress(Keyword("type")) + Word(alphas+nums+"-").setResultsName("type_name") + semi \
              + Optional(Suppress(Keyword("mandatory")) + Or("true","false") + semi) \
              + Optional(Suppress(Keyword("default")) + Word(alphas+nums+"-\"") + semi) \
            + rbrace

key_stmt = Suppress(Keyword("key")) + dblQContent.setResultsName("name") + semi

leaf_list_stmt = Suppress(Keyword("leaf-list")) + identifier_stmt.setResultsName("name") + lbrace \
              + Suppress(Keyword("type")) + Word(alphas+nums+"-").setResultsName("type_name") + semi \
              + Optional(Suppress(Keyword("mandatory")) + Or("true","false") + semi) \
              + Optional(Suppress(Keyword("default")) + Word(alphas+nums+"-\"") + semi) \
            + rbrace

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

demo_string = """
module ietf-interfaces {
  prefix if;  
  namespace "urn:ietf:params:xml:ns:yang:ietf-interfaces";
  import ietf-interfaces1 {
      prefix itf1;
  }

  import ietf-yang-types {
       prefix yang;
  }

  organization "ericsson ab";
  contact "james zhang q";

  typedef interface-ref {
       type leafref {
         path "/if:interfaces/if:interface/if:name";
       }
      description "This type is used by data models that need to reference configured interfaces";
     }

  typedef interface-state-ref {
       type leafref {
         path "/if:interfaces-state/if:interface/if:name";
       }
       description "This type is used by data models that need to reference the operationally present interfaces";
     }

}"""


#result = module_mandatory.parseString(demo_string2)

result = yang_parser.parseString(demo_string)

#result = organization_stmt.parseString(demo_string3)
print(result)
print(dir(result))
print("=====>")
print("module name: %s" %(result.module_name))
print("namespace: %s" %(result.namespace))
print("prefix: %s" %(result.prefix))
for imp in result.imports.asList():
  print("name => %s  prefix => %s" %(imp[0], imp[1]))
print("organization: %s" %(result.organization))
print("contact: ", result.contact)

#for t in result.typedefs.asList():
#  print("--->", t)


print(result.asXML())


nested_string = """
list l1 {
  key "abc";
  leaf abc {
    type boolean;
    mandatory true;
  }
  container c1 {
    leaf c1_leaf {
      type boolean;
      default 10;
    }
    list l2 {
      key "bcd";
        leaf bcd {
          type string;
          default "spurs";
        }
      list l3 {
        key "nnn";
        leaf nnn {
          type boolean;
        }
      }
    }
  }
}
"""

leaf_stmt = Suppress("leaf") + Word(alphas+nums+"_-").setResultsName("leaf_name") + lbrace \
              + Suppress("type") + Word(alphas+nums+"-").setResultsName("type_name") + semi \
              + Optional(Suppress("mandatory") + Or("true","false") + semi) \
              + Optional(Suppress("default") + Word(alphas+nums+"-\"") + semi) \
            + rbrace
key_stmt = Suppress("key") + Word(alphas+nums+"\"-").setResultsName("key_name") + semi

list_sexp = Forward()
list_sexp << ((Suppress(("container")) + Word(alphas+nums).setResultsName("container") + lbrace + ZeroOrMore(leaf_stmt).setResultsName("leaves") + Group(ZeroOrMore(list_sexp)) + rbrace) | \
             (Suppress(("list")) + Word(alphas+nums).setResultsName("list") + lbrace + key_stmt + OneOrMore(leaf_stmt).setResultsName("leaves") + Group(ZeroOrMore(list_sexp)) + rbrace))

print(list_sexp.parseString(nested_string).asXML())


if "__main__" == __name__:

  if (len(sys.argv) > 1):
    with open(sys.argv[1]) as yang_file:
      content = yang_file.read()
      result = yang_parser.parseString(content)
      print(result)
