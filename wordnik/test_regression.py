#!/usr/bin/env python

import helpers
from wordnik import Wordnik
import json, re, unittest
from pprint import pprint

Wordnik._populate_methods()

test_case_output = {}

# id, testsuite, testcase
# (1.1.3)
# [0]
# .size
#     


class TestIntegration(unittest.TestCase):
        def setUp(self):
            self.w        = Wordnik(api_key='9554cd51b3ae7593536040047c20e2ac3ce71b2fd01cf1a27')
            self.tests    = json.load(open('regression.json'))
            self.data     = json.load(open('data.json'))
            self.scriptId = self.tests.get('id')
            self.output   = {}
        
        def test_regression(self):
            self.resources = self.tests.get('resources')
            self.testSuites = self.tests.get('testSuites')
            for suite in self.testSuites:
                suiteName = suite.get('name')
                self.suiteId = suite.get('id')
                cases = suite.get('testCases')
                print "Suite {0} - {1}".format(self.suiteId, suiteName)
                for case in cases:
                    self.runTestCase(case)
            from pprint import pprint
            pprint(self.output)
        
        def runTestCase(self, case):
            caseName = case.get('name')
            self.caseId   = case.get('id')
            print "Running test case {0} -  {1}".format(self.caseId, caseName)
            resource   = self.findResourceById(case.get('resourceId'))
            httpMethod = resource.get('httpMethod')
            path       = resource.get('path')
            methodName  = helpers.normalize(path, httpMethod.lower())
            method_under_test = getattr(self.w, methodName)
            caseInput = case.get('input') or {}
            caseAssertions = case.get('assertions')
            methodInput = {}
            for k, v in caseInput.iteritems():
                k = self.parse_ognl(k)
                v = self.parse_ognl(v)
                if k is None or v is None:
                    return None
                methodInput.update( {str(k): str(v)} )

            # print "testing {0}".format(methodName)
            print method_under_test
            print methodInput
            output = method_under_test(**methodInput)
            self.output["{0}.{1}.{2}".format(self.scriptId, self.suiteId, self.caseId)] = output
        
        def findResourceById(self, n):
            for resource in self.resources:
                if resource.get('id') == n:
                    return resource
        
        def parse_ognl(self, s):
            ## Will find anything between "${" and "}"
            ognl_re = re.compile('\$\{(?P<ognl>.*)\}')
            found = ognl_re.search(s)
            
            ## This doesn't look like an OGNL expression
            if not found:
                return s
            ## start parsing the OGNL...  D-;
            else:
                ## split on periods that don't have numbers next to them, then reverse so we can "pop" off the list
                special_period_re = re.compile
                path = found.groupdict()['ognl'].split(".")
                print path
                path.reverse()
                
                ## do we need to calculate the size?
                if path[0] == "size":
                    doSize = True
                else:
                    doSize = False
                ## regular expression will match something[x]
                list_re = re.compile('(?P<listname>.*)\[(?P<item>.*)\]')
                
                
                obj = path.pop()
                if obj == "data":
                    dataSource = self.data
                    while path:
                        nextElement = path.pop()
                        isList = list_re.search(nextElement)
                        if isList:
                            ## get the list name and element from the regex match
                            listname = isList.groupdict()['listname']
                            item     = int(isList.groupdict()['item'])
                            ## fetch the list and the item in the list
                            l = dataSource.get(listname)
                            dataSource = l[item]
                        else:
                            ## we can just do a "get"
                            dataSource = dataSource.get(nextElement)
                    return dataSource
                            
                elif obj == "output":
                    dataSource = self.output
                    dataLocation = path.pop()
                    print dataLocation
                else:
                    print "got an unknown data source: {0}".format(path)
                
                    
                # print path
                return None

if __name__ == "__main__":
    unittest.main()
            
            
        
        
