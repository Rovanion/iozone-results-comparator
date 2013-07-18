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
#       VERSION:  1.1
#       CREATED:  02/18/2011 11:36:03 PM CET
#      REVISION:  ---
#===============================================================================

BASELINE=$(find ./ext4 -name "*.iozone" | sort)
SET1=$(find ./xfs -name "*.iozone" | sort)

#read -ra BASELINE_ARRAY <<< ${BASELINE}
#read -ra SET1_ARRAY <<< ${SET1}

cp ../src_new_version/stylesheet.css .

#../src/iozone_results_comparator.py --baseline ${BASELINE} --set1 ${SET1} --detail ALL
../src_new_version/iozone_results_comparator.py --baseline ${BASELINE} --set1 ${SET1}

rm -f stylesheet.css

