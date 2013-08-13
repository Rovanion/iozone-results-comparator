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
SET2=$(find ./ext2 -name "*.iozone" | sort)
SET3=$(find ./ext3 -name "*.iozone" | sort)

#../old_version/iozone_results_comparator.py --baseline ${BASELINE} --set1 ${SET1} --detail ALL
../src/iozone_results_comparator.py --baseline ${BASELINE} --set1 ${SET1}
#../src/iozone_results_comparator.py --baseline ${BASELINE} --set1 ${SET1} --set2 ${SET2} --set3 ${SET3} --multiset

