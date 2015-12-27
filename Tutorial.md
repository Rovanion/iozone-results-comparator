# Iozone runs #

You will need to create iozone result files first. We recommend to perform 5 runs to create one set of data.

## Baseline set of iozone data ##
```
iozone -U /mnt/test -a -f /mnt/test/iozone -n 4k -g 4096m > baseline_1.iozone
iozone -U /mnt/test -a -f /mnt/test/iozone -n 4k -g 4096m > baseline_2.iozone
iozone -U /mnt/test -a -f /mnt/test/iozone -n 4k -g 4096m > baseline_3.iozone
iozone -U /mnt/test -a -f /mnt/test/iozone -n 4k -g 4096m > baseline_4.iozone
iozone -U /mnt/test -a -f /mnt/test/iozone -n 4k -g 4096m > baseline_5.iozone
```

## Target set of iozone data ##
```
iozone -U /mnt/test -a -f /mnt/test_1/iozone -n 4k -g 4096m > target_1.iozone
iozone -U /mnt/test -a -f /mnt/test_1/iozone -n 4k -g 4096m > target_2.iozone
iozone -U /mnt/test -a -f /mnt/test_1/iozone -n 4k -g 4096m > target_3.iozone
iozone -U /mnt/test -a -f /mnt/test_1/iozone -n 4k -g 4096m > target_4.iozone
iozone -U /mnt/test -a -f /mnt/test_1/iozone -n 4k -g 4096m > target_5.iozone
```

Target set of iozone result files can be produced for example
  * on another version of Linux kernel
  * on another physical device with the same file-system as for baseline
  * on the same physical device with the different file-system as for baseline. It can include for example encryption layer (LUKS).

# Analyses with help of `iozone_results_comparator.py` #

The typical usage is
  1. run `iozone_results_comparator.py` in the **default mode**
    * Check summary graph
    * Check default results for all operations or interesting operations based on the overall summary graph
  1. comparison of more than two data sets using the **multiset mode** plots


```
BASELINE=$(find ./ -name "baseline*.iozone" | sort)
SET1=$(find ./ -name "target*.iozone" | sort)

#Default analyses mode (overview)
~/GIT/iozone-results-comparator/src/iozone_results_comparator.py --baseline ${BASELINE} --set1 ${SET1} 
```

Please note you need matplotlib in version 1.2 or higher in order to get the tool working properly.

### Checking default analyses mode results ###
Open results in your preferred HTML browser `firefox html_out/index.html`
Check the Summary graph ![http://wiki.iozone-results-comparator.googlecode.com/git/summary.png](http://wiki.iozone-results-comparator.googlecode.com/git/summary.png) on the top of the page.

You will note that results in the baseline and target set differs significantly for the _record rewrite_ operation. Let's click on the  Record rewrite link in the header of the table located below the summary plot, which brings us to the Record rewrite section. There are four graphs:

#### Throughput as a function of the file size ####
In this plot there are data aggregated over all block sizes.  You can see that performance starts to be different for file sizes bigger than 512kB. Median, first and third quartile values are displayed when mouse pointer is placed over the plot.  ![http://wiki.iozone-results-comparator.googlecode.com/git/record_rewrite_FS.png](http://wiki.iozone-results-comparator.googlecode.com/git/record_rewrite_FS.png)

#### Throughput as a function of the block size ####
Data are aggregated over all file sizes. You can see that performance differs from block size bigger than 8kB. ![http://wiki.iozone-results-comparator.googlecode.com/git/record_rewrite_BS.png](http://wiki.iozone-results-comparator.googlecode.com/git/record_rewrite_BS.png)

#### Linear regression plot ####
In this plot each point represents throughput for one file size and one block size. X coordinate represents arithmetic average of the throughput in the _baseline data set_ for the one particular file and block size. Y coordinate represents arithmetic average of the throughput in the _target data set_ for the same file and block size. You can see that almost all points are above line Y=X which means that performance in the _target data set_ is greater than performance in the _baseline data set_. There are however few red points where performance in _target data set_ is slightly worse than in the _baseline data set_. ![http://wiki.iozone-results-comparator.googlecode.com/git/record_rewrite_linear_regression.png](http://wiki.iozone-results-comparator.googlecode.com/git/record_rewrite_linear_regression.png)

#### Percentual difference plot ####
File size values are displayed on the X axis and Block size values on the Y axis while the percentual difference of Baseline and Set1 is displayed in form of a circles. Bigger the difference, bigger the circle. Color of the circle represents category as shown in the legend box. Below example actually belongs to different operation to demonstrate it's function in better way. Set1 is more than 30% faster for file sizes around 2<sup>12</sup> bytes, but Baseline is from 15% to 30% faster for files having 2<sup>20</sup> bytes in size and also faster for files smaller than 64 bytes.
![http://wiki.iozone-results-comparator.googlecode.com/git/percentual_difference.png](http://wiki.iozone-results-comparator.googlecode.com/git/percentual_difference.png)

#### Tabbed delimited files for the further analyses ####
`iozone_results_comparator` will create also directory called `tsv_out` with text files containing iozone result values delimited by Tab key. These can be used for the further analyses for example in the GNU R language or in the open office.

### Checking the multiset mode results ###
The multiset mode is enabled by using the `--multiset` option and providing more than two sets for comaprision.
```
BASELINE=$(find ./ext4 -name "*.iozone" | sort)
SET1=$(find ./xfs -name "*.iozone" | sort)
SET2=$(find ./ext2 -name "*.iozone" | sort)
SET3=$(find ./ext3 -name "*.iozone" | sort)

~/GIT/iozone-results-comparator/src/iozone_results_comparator.py --baseline ${BASELINE} --set1 ${SET1} --set2 ${SET2} --set3 ${SET3} --multiset
```

Let's check results in the HTML browser:
```
firefox html_out/index.html &
```
You can see throughput as a function of the file size and throughput as a function of the block size plots for every operation; every plot containing values for all the data sets as shown in the bellow examples. The plot showing throughput as a function of file size demonstrates significant performance drop for Set2 on 4G file size. If such drop needs to be analysed in more detail, users are encouraged to use the normal mode to compare the investigated data set against selected baseline.
![http://wiki.iozone-results-comparator.googlecode.com/git/multiset_FS.png](http://wiki.iozone-results-comparator.googlecode.com/git/multiset_FS.png)
![http://wiki.iozone-results-comparator.googlecode.com/git/multiset_BS.png](http://wiki.iozone-results-comparator.googlecode.com/git/multiset_BS.png)