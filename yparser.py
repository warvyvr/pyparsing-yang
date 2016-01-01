import os
import sys
from pyparsing import *

#TODO
# 1.xpath string doesn't define well
# 2.namespace string doesn't define well


semicolon = Suppress(Literal(";"))
lbrace = Suppress(Literal("{"))
rbrace = Suppress(Literal("}"))

#double quotation marks
dqm = Suppress(Literal('"'))

def removeColon(token):
	print(token)
	return token[:-1]

# maching keyword <value> ; 
def simple_stmt(keyword, matching):
	return Suppress(Literal(keyword)) + matching.setResultsName(keyword) + semicolon

def simple_string_stmt(keyword, matching):
  matching_local = matching.setResultsName(keyword)
  return Suppress(Literal(keyword)) + dqm + matching_local + dqm + semicolon

name_stmt = Word(alphas+"\"-_:"+nums)

# namespace <namespace>;
namespace_stmt = Suppress(Literal("namespace")) + name_stmt.setResultsName("namespace") + semicolon

# prefix <prefix>;
prefix_stmt= Suppress(Literal("prefix")) + name_stmt.setResultsName("prefix")+ semicolon


# import <import_module> { prefix <prefix>; }
import_stmt = Group(Suppress(Literal("import")) + name_stmt.setResultsName("import_module") + lbrace \
                + prefix_stmt + rbrace)

# organization "<organization>";

organization_stmt = Suppress(Literal("organization")) + Word(printables.replace(";","")+" ").setResultsName("organization") + semicolon

yang_version_stmt = Group(Suppress(Literal("yang-version")) + Literal("1").setResultsName("version") + semicolon).setResultsName("yang-version)")

description = Word(printables.replace(";","")+" ").setResultsName("description")
description_stmt = Suppress(Literal("description")) + description + semicolon

contact_stmt = Suppress(Literal("contact")) + Word(printables.replace(";","")+" ").setResultsName("contact") + semicolon

reference_stmt = Group(Suppress(Literal("reference")) + Word(printables.replace(";","")+" ") + semicolon)

module_header_stmts = Optional(yang_version_stmt) + OneOrMore((namespace_stmt | prefix_stmt))

linkage_stmts = ZeroOrMore(import_stmt).setResultsName("imports")

meta_stmts = (organization_stmt | contact_stmt | contact_stmt | reference_stmt) * (0,4)

xpath_stmt = Word(printables.replace(";",""))
path_stmt = Suppress(Literal("path")) + xpath_stmt + semicolon


typedef_name = Word(alphas+nums+"-")
base_type_name = Word(alphas+nums+"-")

typedef_stmt = Group(Suppress(Literal("typedef")) + typedef_name.setResultsName("typedef_name") + lbrace \
                   + Suppress(Literal("type")) + base_type_name.setResultsName("basetype_name") + lbrace \
                     + path_stmt      \
                   + rbrace           \
                   + description_stmt   \
                 + rbrace)

typedef_stmt = typedef_stmt.setResultsName("typedef")

yang_model = Suppress(Literal("module"))  + name_stmt.setResultsName("module_name") + lbrace  \
                + module_header_stmts + linkage_stmts + meta_stmts \
                + ZeroOrMore(typedef_stmt).setResultsName("typedefs") \
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

result = yang_model.parseString(demo_string)

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

for t in result.typedefs.asList():
  print("--->", t)


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
              + Suppress("type") + Word(alphas+nums+"-").setResultsName("type_name") + semicolon \
              + Optional(Suppress("mandatory") + Or("true","false") + semicolon) \
              + Optional(Suppress("default") + Word(alphas+nums+"-\"") + semicolon) \
            + rbrace
key_stmt = Suppress("key") + Word(alphas+nums+"\"-").setResultsName("key_name") + semicolon

list_sexp = Forward()
list_sexp << ((Suppress(("container")) + Word(alphas+nums).setResultsName("container") + lbrace + ZeroOrMore(leaf_stmt).setResultsName("leaves") + Group(ZeroOrMore(list_sexp)) + rbrace) | \
             (Suppress(("list")) + Word(alphas+nums).setResultsName("list") + lbrace + key_stmt + OneOrMore(leaf_stmt).setResultsName("leaves") + Group(ZeroOrMore(list_sexp)) + rbrace))

print(list_sexp.parseString(nested_string).asXML())
