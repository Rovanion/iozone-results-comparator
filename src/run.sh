#!/bin/bash
#===============================================================================
#
#          FILE:  run.sh
# 
#         USAGE:  ./run.sh 
#
#   DESCRIPTION:
#
#       OPTIONS:  ---
#  REQUIREMENTS:  ---
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR:  Jiri Hladky (JH), hladky.jiri@gmail.com
#       COMPANY:
#       VERSION:  1.0
#       CREATED:  02/18/2011 11:36:03 PM CET
#      REVISION:  ---
#===============================================================================

BASELINE=$(find ../data/JOBID_31835_RECIPEID_63041_RECIPETESTID_704021/ -name iozone_incache_default.iozone | grep Run | sort)
SET1=$(find ../data/JOBID_31835_RECIPEID_63041_RECIPETESTID_704023/ -name iozone_incache_default.iozone | grep Run | sort)

./iozone_results_comparator.py --baseline ${BASELINE} --set1 ${SET1} --html
