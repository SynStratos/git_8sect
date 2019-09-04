import subprocess
import sys
from os import devnull
import parser


# binary search implementation
def bisect(commit_list, script):
    index = int(len(commit_list) / 2)  # needed for py3
    commit = commit_list[index]
    print("checking the commit: " + str(commit))

    fnull = open(devnull, 'w') # I don't want to print checkout stdout
    subprocess.call(['git', 'checkout', commit], stdout=fnull, stderr=fnull)  # subprocess.STDOUT)

    response = None

    if len(commit_list) == 1:
        return commit_list[0]

    # the benchmarking script is run and the exit code is stored in response
    response = subprocess.Popen(script, stdout=subprocess.PIPE)
    response.communicate()
    response = response.returncode

    # TODO: check if special code 125 is needed and decide range of error codes
    # by default, 0 exit code means the commit is a good one

    if response == 0:
        return bisect(commit_list[:index], script)
    else:
       return bisect(commit_list[index:], script)


# this method will check if the commit is a merge node, returning all the branches involved in the merge
def check_merge(commit):
    commit_log = subprocess.check_output(['git', 'log', '-1', commit])
    commit_log = commit_log.split('\n')[1]
    commit_log = commit_log.split(' ')

    # check if the line contains the header "Merge:"
    if commit_log[0] == 'Merge:':
        # the content of the line will be the list of parent commits (2+)
        return True, commit_log[1:]
    else:
        return False, None


# main method
def main():
    args = parser.parse(sys.argv[1:])
    bad_commit = args.bad_commit
    good_commit = args.good_commit

    if args.dates:
        master_commits = subprocess.check_output(['git', 'rev-list', '--first-parent', 'master', '--after', good_commit, '--before', bad_commit]).split('\n')[:-1]
        master_commits = master_commits[:-1]  # no sense to pass the good for sure commit
    elif args.timestamps:
        master_commits = subprocess.check_output(
            ['git', 'rev-list', '--first-parent', 'master', '--max-age', good_commit, '--min-age', bad_commit]).split(
            '\n')[:-1]
        master_commits = master_commits[:-1]  # no sense to pass the good for sure commit
    elif args.commits:
        master_commits = subprocess.check_output(['git', 'rev-list', '--first-parent', bad_commit]).split('\n')[:-1]
        index = master_commits.index(good_commit)
        master_commits = master_commits[:index]  # the good commit is excluded

    bad_commit = bisect(master_commits, bad_commit)

    # check if the resulted bad commit corresponds to a merge node
    is_merge, parents = check_merge(bad_commit)

    while is_merge:
        old_bad_commit = bad_commit

        for parent_commit in parents[1:]:
            # for each parent commit not in master branch [always the first in parent list]
            other_parents = parents
            # list of parents different from the one I am checking for the '--not' argument of 'git rev-list'
            other_parents.remove(parent_commit)
            # get all the commits belonging to the selected branch
            command_line = ['git', 'rev-list', bad_commit, '--not'] + other_parents
            branch_commits = subprocess.check_output(command_line)
            # split and eat the empty line
            branch_commits = branch_commits.split('\n')[:-1]
            # i get all the commits contained in that branch that are not present in the actual master branch
            # and cutting out the merge node
            new_bad_commit = bisect(branch_commits, bad_commit)

            # the bad commit is in the selected branch, not going to search the other in case of multiple merge
            if new_bad_commit != bad_commit:
                # update the overall bad commit to check if it is a new merge node itself
                bad_commit = new_bad_commit
                break

        # after searching all the sub-branches of the merge node, the bad commit is still the merge node
        # maybe the bug derives from a conflict in the merged items (easily possible in multiple merges)
        if old_bad_commit == bad_commit:
            break
        else:
            # check if the new selected bad commit is a merge node itself
            # if is_merge is False the loop will stop
            is_merge, parents = check_merge(bad_commit)

    subprocess.call(['git', 'checkout', 'master'])

    print("---------------------------------------")
    print("---------------------------------------")
    print("The bug was introduced in this commit: ")
    print(bad_commit)


if __name__ == '__main__':
    main()
