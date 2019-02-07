#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this 
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import print_function
import sys
import platform
import getpass
import time
import argparse
from io import open

parser = argparse.ArgumentParser()
parser.add_argument('statuscodes', help='path/to/Opc.Ua.StatusCodes.csv')
parser.add_argument('outfile', help='outfile w/o extension')
args = parser.parse_args()

rows = []
with open(args.statuscodes, mode="rt") as f:
    lines = f.readlines()
    for l in lines:
        rows.append(tuple(l.strip().split(',')))

fh = open(args.outfile + ".h", "wt", encoding='utf8')
fc = open(args.outfile + ".c", "wt", encoding='utf8')
def printh(string):
    print(string, end=u'\n', file=fh)
def printc(string):
    print(string, end=u'\n', file=fc)

#########################
# Print the header file #
#########################

printh(u'''/*---------------------------------------------------------
 * Autogenerated -- do not modify
 * Generated from %s with script %s
 *-------------------------------------------------------*/

/**
 * .. _statuscodes:
 *
 * StatusCodes
 * -----------
 * StatusCodes are extensively used in the OPC UA protocol and in the open62541
 * API. They are represented by the :ref:`statuscode` data type. The following
 * definitions are autogenerated from the ``Opc.Ua.StatusCodes.csv`` file provided
 * with the OPC UA standard. */

/* These StatusCodes are manually generated. */
#define UA_STATUSCODE_GOOD 0x00
#define UA_STATUSCODE_INFOTYPE_DATAVALUE 0x00000400
#define UA_STATUSCODE_INFOBITS_OVERFLOW 0x00000080
''' % (args.statuscodes, sys.argv[0]))

for row in rows:
    printh(u"#define UA_STATUSCODE_%s %s /* %s */" % (row[0].upper(), row[1], row[2]))

#########################
# Print the source file #
#########################

printc(u'''/**********************************************************
 * Autogenerated -- do not modify
 * Generated from %s with script %s
 *********************************************************/

#include "ua_types.h"''' % (args.statuscodes, sys.argv[0]))

count = 2 + len(rows)

printc(u'''
typedef struct {
    UA_StatusCode code;
    const char *name;
} UA_StatusCodeName;

#ifndef UA_ENABLE_STATUSCODE_DESCRIPTIONS
static const char * emptyStatusCodeName = "";
const char * UA_StatusCode_name(UA_StatusCode code) {
    return emptyStatusCodeName;
}
#else
static const size_t statusCodeDescriptionsSize = %s;
static const UA_StatusCodeName statusCodeDescriptions[%i] = {
    {UA_STATUSCODE_GOOD, \"Good\"},''' % (count, count))

for row in rows:
    printc(u"    {UA_STATUSCODE_%s, \"%s\"}," % (row[0].upper(), row[0]))
printc(u'''    {0xffffffff, "Unknown StatusCode"}
};

const char * UA_StatusCode_name(UA_StatusCode code) {
    for (size_t i = 0; i < statusCodeDescriptionsSize; ++i) {
        if (statusCodeDescriptions[i].code == code)
            return statusCodeDescriptions[i].name;
    }
    return statusCodeDescriptions[statusCodeDescriptionsSize-1].name;
}

#endif''')

fc.close()
fh.close()
