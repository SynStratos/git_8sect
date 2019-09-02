## Git 8sect

This is an improved version of the git binary search (bisect) script.
It can work on multiple branch merges and nested merges, trying to visit the least possible amount of nodes.
The command line is almost the same of bisect.

Run in your git repository folder:
```
python <path-to-this-script>/script.py <bad-commit-sha1> <good-commit-sha1> '<benchmarking-shell-script>'
```

### Example
```
python ~/script.py 49dd4dd0b76448274e41a3d2a0c761930b6c111e 8c2a21e7638e45c74df8f6da2dd800043a4ca5ee 'python /home/Desktop/benchmark.py'
```
