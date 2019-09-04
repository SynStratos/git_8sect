import subprocess
import sys
from os import devnull
import parser

args = None


# binary search implementation
def bisect(list, badguy):
    script = args.script.split(' ')
    index = int(len(list) / 2)

    commit = list[index]
    print("checking the commit: " + str(commit))

    fnull = open(devnull, 'w') # I don't want to print checkout stdout
    subprocess.call(['git', 'checkout', commit], stdout=fnull, stderr=fnull)  # subprocess.STDOUT)

    response = subprocess.Popen(script, stdout=subprocess.PIPE)
    response.communicate()
    response = response.returncode

    if response == 0:
        # GOOD
        if len(list) == 1:
            return badguy
        else:
            return bisect(list[:index], badguy)

    else:
       # BAD
        if len(list) == 1 or index == len(list) - 1:
            return commit
        else:
            return bisect(list[index+1:], commit)


# this method will check if the commit is a merge node, returning all the branches involved in the merge
def check_merge(commit):
    branches = subprocess.check_output(['git', 'log', '-1', commit])
    branches = branches.split('\n')[1]
    branches = branches.split(' ')

    if branches[0] == 'Merge:':
        return True, branches[1:]
    else:
        return False, None


# main method
def main():
    bad_commit = args.bad_commit
    good_commit = args.good_commit

    if args.dates:
        master_commits = subprocess.check_output(['git', 'rev-list', '--first-parent', 'master', '--after', good_commit, '--before', bad_commit]).split('\n')[:-1]
        master_commits = master_commits[:-1]  # no sense to pass the good for sure commit
    else:
        master_commits = subprocess.check_output(['git', 'rev-list', '--first-parent', bad_commit]).split('\n')[:-1]
        index = master_commits.index(good_commit)
        master_commits = master_commits[:index]  # the good commit is excluded

    bad_commit = bisect(master_commits, bad_commit)

    is_merge = False

    # check if the resulted bad commit corresponds to a merge node
    is_merge, branches = check_merge(bad_commit)

    while is_merge:
        old_bad = bad_commit

        for branch in branches[1:]:
            # for each parent branch different from master branch [always the first in parent list]
            other_branches = branches
            # I need the list of branches different from the one I am checking for the '--not' argument of 'git rev-list'
            other_branches.remove(branch)
            # get all the commits belonging to the selected branch
            command_line = ['git', 'rev-list', branch, '--not'] + other_branches
            branch = subprocess.check_output(command_line)
            # split and eat the empty line
            branch = branch.split('\n')[:-1]
            # i get all the commits contained in that branch that are not present in the actual master branch and cutting out the merge node
            new_commit = bisect(branch, bad_commit)

            # the bad commit is in the selected branch, not going to search the other in case of multiple merge
            if new_commit != bad_commit:
                # update the overall bad commit to check if it is a new merge node itself
                bad_commit = new_commit
                break

        # after searching all the sub-branches of the merge node, the bad commit is still the merge node
        # maybe the bug derives from a conflict in the merged items (easily possible in multiple merges)
        if old_bad == bad_commit:
            break
        else:
            # check if the new selected bad commit is a merge node itself
            # if is_merge is False the loop will stop
            is_merge, branches = check_merge(bad_commit)

    subprocess.call(['git', 'checkout', 'master'])

    print("---------------------------------------")
    print("---------------------------------------")
    print("The bug was introduced in this commit: ")
    print(bad_commit)


if __name__=='__main__':
    args = parser.parse(sys.argv[1:])

    main()
