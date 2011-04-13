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

class OGNLObject(object):
    regex = re.compile('\$\{(.*)\}')
    
    def __init__(self, data=dict()):
        self.data    = data
    
    def get(self, item):
        if self.data is None:
            return None
        else:
            return self.data.get(item)
    
    def setData(self, data):
        self.data = data
    
    def parseOgnl(self, expr):
        found = self.regex.findall(expr)
        if found == []:
            return expr
        else:
            components = found[0].split(".")
            print components
    

class TestIntegration(unittest.TestCase):
        def setUp(self):
            self.id      = 1
            self.w       = Wordnik(api_key='9554cd51b3ae7593536040047c20e2ac3ce71b2fd01cf1a27')
            self.results = OGNLObject()
            self.tests   = OGNLObject(data=json.load(open('regression.json')))
            self.data    = OGNLObject(data=json.load(open('data.json')))
            self.output  = {"data": {}}
            self.output['data'].update( {self.id: {}})
        
        def test_regression(self):
            self.resources = self.tests.get('resources')
            self.testSuites = self.tests.get('testSuites')
            for suite in self.testSuites:
                suiteName = suite.get('name')
                suiteId = suite.get('id')
                self.output['data'][self.id].update({ suiteId: {}})
                cases = suite.get('testCases')
                print "Suite {0} - {1}".format(suiteId, suiteName)
                for case in cases:
                    self.runTestCase(case)
        
        def runTestCase(self, case):
            caseName = case.get('name')
            caseId   = case.get('id')
            print "Running test case {0} -  {1}".format(caseId, caseName)
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

            print "testing {0}".format(methodName)

            output = method_under_test(**methodInput)
        
        def findResourceById(self, n):
            for resource in self.resources:
                if resource.get('id') == n:
                    return resource
        
        def parse_ognl(self, s):
            ognl_re = re.compile('\$\{(.*)\}')
            found = ognl_re.findall(s)
            if found == []:
                return s
            else:
                path = found[0].split(".")
                obj = path[0]
                if obj == "data":
                    dataSource = self.data
                elif obj == "output":
                    dataSource = self.output
                else:
                    print "got an unknown data source: {0}".format(path)
                
                    
                print path
                return None

if __name__ == "__main__":
    unittest.main()
            
            
        
        
