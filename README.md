## Git 8sect

This is an improved version of the git binary search (bisect) script.
It can work on multiple branch merges and nested merges, trying to visit the least possible amount of nodes.
The command line is almost the same of bisect.

Run in your git repository folder:
```
python [path-to-this-script]/script.py [bad-commit-sha1] [good-commit-sha1] [path-to-the-benchmarking-script]
```

