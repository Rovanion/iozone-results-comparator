# Introduction #

We deal with performance testing using [iozone](http://www.iozone.org/). The task is to compare iozone results on different development versions of Linux kernel. It has turned out to be a complex task. To compare the data properly one has to
  * perform several (recommended 5) runs on each Linux kernel version
  * use statistical tests to find if results differ at given confidence level

To do this task we have written a tool which will parse iozone result files and create plots along with statistical tests to compare the data. The script will also create tab delimited data files which can be used to further analyses data using R language or Open Office (or MS Excel)

# Features #

  * it can analyze and compare sets of run. You can for example compare **baseline set** of iozone results (1 or more iozone runs) against **target set** of iozone results (1 or more iozone runs to statistically filter out some randomness in the iozone results)

  * it will produce graphs showing the results visually and present the statistical results in the HTML

  * in the **multiset mode** it will compare a throughput of more than two data sets. Throughput of all the data sets is presented as a function of file and block size for every operation.  ![http://wiki.iozone-results-comparator.googlecode.com/git/multiset_FS.png](http://wiki.iozone-results-comparator.googlecode.com/git/multiset_FS.png)

  * in the **default analyses mode** it will aggregate data by _filesize_ and _blocksize_ and will produce corresponding graphs along with statistics.  Student's t-test is used for evaluation of set difference at 90% confidence level, but because we are aggregating different data (and throughput for small and big file/block sizes vary significantly) it's results can be disputed. Therefore we compute number of other statistics available for such aggregates like geometric mean, median, first quartile, third quartile and confidence intervals.

  * in the **default analyses mode** it will produce a linear regression graph where each data point represents one comparison of baseline against target data. The X coordinate represents throughput in the baseline set for the given filesize and blocksize. The Y coordinate represents throughput in the target set for the same filesize and blocksize. When baseline and target throughput are the same, point will be on the line y=x. For performance regression the point lies below line y=x, for performance improvement above line y=x. Linear regression is done to determine the best fit y=k\*x. For k<1 there is performance drop. This kind of graph is an extremely useful tool to compare two data sets. Ideally, all points are on one line y=k\*x. In practice you can see the spread along the line y=k\*x and you can immediately see any strange values. It completes also comparison of geometrical means. iozone will measure far more values for small FS and BS than for big FS and BS. Geometrical mean (as well as median) computation can mask out the results for big FS and BS because of far more values for the small FS and BS. Linear fit is different. Values with big throughput are more significant than tiny values of the throughput. ![http://wiki.iozone-results-comparator.googlecode.com/git/record_rewrite_linear_regression.png](http://wiki.iozone-results-comparator.googlecode.com/git/record_rewrite_linear_regression.png) <br>Notice that throughput in the target set is significantly better than in the  baseline set for the most of the measured values (black points) with few exceptions (red points).</li></ul>

<ul><li>overall summary graph along with different statistics is presented as well. The graph is a <a href='http://en.wikipedia.org/wiki/Box_plot'>box-and-whisker plot</a> where<br>
<ul><li>boxes represent first quartile, median, third quartile over the all results for a given operation<br>
</li><li>whiskers represent min and max throughput values over the all results for a given operation <img src='http://wiki.iozone-results-comparator.googlecode.com/git/summary.png' /></li></ul></li></ul>

<ul><li>The percentual difference plot is also generated in the <b>default mode</b>. It is extremely handy for discovering anomalies which occur for a specific file and block size combination or for cases when Baseline is faster than Set1 under some conditions while Set1 is faster than Baseline under different conditions. The percentual  difference plot may give a good overview on which these conditions are.<br>
<img src='http://wiki.iozone-results-comparator.googlecode.com/git/percentual_difference.png' /></li></ul>

<ul><li>in the <b>default analyses mode</b> a tab delimitted file is produced with all aggregated raw data. This file can be read either into<br>
<ul><li>open office <code>oocalc &lt;filename&gt;</code>
</li><li>GNU statical language R, <code>read.delim("&lt;filename&gt;",comment.char = "#")</code> for the further processing.</li></ul></li></ul>

<ul><li>We have very carefully confirmed that computed statistical data are correct. We have used GNU R, Open Office and Wolfram's Mathematica (via <a href='http://www.wolframalpha.com/'>Wolfram Alpha Search Engine</a>) to verify the results</li></ul>

<h1>Further plans #
  * All the planned features were implemented in the current version of the tool. If you happen to have a feature or bugfix request, you're welcome to contact us.