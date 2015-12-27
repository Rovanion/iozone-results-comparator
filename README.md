Iozone Result Comparator
========================

Iozone-results-comparator is a Python 2 application for analysing results of the IOzone Filesystem Benchmark.

It takes two or more sets of Iozone results as the input and compares them using various statistical methods. Primary output is a HTML page with tables and plots. Tab delimited output for further processing is also produced.


Dependencies
------------
Dependencies include scipy and matplotlib. These are installed on Debian/Ubuntu by running:

```bash
sudo apt-get install python-scipy python-matplotlib
```

Installation
------------

To install from source  run the following:

```bash
git clone https://github.com/Rovanion/iozone-result-comparator.git
cd iozone-result-comparator
sudo pip install -r requirements.txt
sudo pip install .

```

If you didn't install the dependencies from your distributions package manager the above lines will install them from pip instead.



Usage
-----

Usage instructions can be found on the wiki pages. There is an [overview](https://github.com/Rovanion/iozone-results-comparator/wiki/Overview) and a [Tutorial](https://github.com/Rovanion/iozone-results-comparator/wiki/Tutorial).
