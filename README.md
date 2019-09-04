## Git 8sect

This is an improved version of the git binary search (bisect) script.
It can work on multiple branch merges and nested merges, trying to visit the least possible amount of nodes.
The command line is almost the same of bisect.

Update: now it is possible to define the bad and good commits whether by Id or by Date.

### Usage
```
script.py [-h] [-d] [-s SCRIPT] bad_commit good_commit
```

### Example
```
$ python ~/script.py 49dd4dd0b76448274e41a3d2a0c761930b6c111e 8c2a21e7638e45c74df8f6da2dd800043a4ca5ee -s 'python /home/Desktop/benchmark.py'
$ python ~/script.py -d 'Mon Sep 2 14:32:03 2019 +0200' 'Mon Sep 2 14:07:41 2019 +0200' -s 'python /home/Desktop/benchmark.py'
```
