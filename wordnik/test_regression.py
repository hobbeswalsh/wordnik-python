#!/usr/bin/env python

import helpers
from wordnik import Wordnik
import json, unittest
from pprint import pprint

Wordnik._populate_methods()
w = Wordnik(api_key='9554cd51b3ae7593536040047c20e2ac3ce71b2fd01cf1a27')
j = json.load(open('regression.json'))
data = json.load(open('data.json'))

id = j.get('id')
resources = j.get('resources')
testSuites = j.get('testSuites')

def findResourceById(n):
    for resource in resources:
        if resource.get('id') == n:
            return resource

def runTestCase(case):
    caseName = case.get('name')
    caseId   = case.get('id')
    print "Running test case {0} -  {1}".format(caseId, caseName)
    resource = findResourceById(case.get('resourceId'))
    httpMethod = resource.get('httpMethod')
    path       = resource.get('path')
    methodName  = helpers.normalize(path, httpMethod.lower())
    method_under_test = getattr(w, methodName)
    caseInput = case.get('input') or {}
    caseAssertions = case.get('assertions')
    methodInput = {}
    for k, v in caseInput.iteritems():
        if "${" in k or "${" in v:
            return None
        methodInput.update( {str(k): str(v)} )
    
    print "testing {0}".format(methodName)
    
    print method_under_test(**methodInput)

for suite in testSuites:
    suiteName = suite.get('name')
    suiteId = suite.get('id')
    cases = suite.get('testCases')
    print "Suite {0} - {1}".format(suiteId, suiteName)
    for case in cases:
        runTestCase(case)
    


# class TestHelperFunctions(unittest.TestCase):