import subprocess
from sys import argv
from os import devnull

# binary search implementation
def bisect(list, badguy):

    #global sh
    #script = ['python', sh]

    script = argv[3].split(' ')
    index = (int)(len(list) / 2)

    commit = list[index]
    print ("checking the commit: " + str(commit))

    FNULL = open(devnull, 'w') # I don't want to print checkout stdout
    retcode = subprocess.call(['git', 'checkout', commit], stdout=FNULL, stderr=subprocess.STDOUT)

    # the benchmarking script is run and the exit code is stored in response
    response = subprocess.Popen(script, stdout=subprocess.PIPE)
    response.communicate()
    response = response.returncode

    # TODO: check if special code 125 is needed and decide range of error codes
    # by default, 0 exit code means the commit is a good one

    if len(list) == 1:
        print "last check for this branch"
        if response == 0:
            print "good"
            return badguy
        # elif response == 125:
        #
        else:
            print "bad"
            return commit

    if response == 0:
        print "good"
        badguy = bisect(list[:index], badguy)
    # elif response == 125:
    #    print 'error'
    else:
        badguy = commit
        # if the bad commit is the last element of the current list, the research is over
        if (list.index(badguy) == len(list) - 1):
            print "last check for this branch"
            print "bad"
            return badguy
        else:
            print "bad"
            badguy = bisect(list[index+1:], badguy)

    return badguy


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
    badcommit = argv[1] # 'master'
    goodcommit = argv[2]


    # TODO: give better error outputs
    if (badcommit == None):
        print "missing parameter"
        return

    if (goodcommit == None):
        print "missing parameter"
        return

    if (argv[3] == None):
        print "missing parameter"
        return

    master_commits = subprocess.check_output(['git', 'rev-list', '--first-parent', badcommit]).split('\n')[:-1]

    list = master_commits.index(goodcommit)
    list = master_commits[:list]

    badcommit = bisect(list, badcommit)

    print badcommit

    is_merge = False

    # check if the resulted bad commit corresponds to a merge node
    is_merge, branches = check_merge(badcommit)

    while(is_merge):
        oldbad = badcommit

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
            new_commit = bisect(branch, badcommit)

            # the bad commit is in the selected branch, not going to search the other in case of multiple merge
            if new_commit != badcommit:
                # update the overall bad commit to check if it is a new merge node itself
                badcommit = new_commit
                break

        # after searching all the sub-branches of the merge node, the bad commit is still the merge node
        # maybe the bug derives from a conflict in the merged items (easily possible in multiple merges)
        if oldbad == badcommit:
            break
        else:
            # check if the new selected bad commit is a merge node itself
            # if is_merge is False the loop will stop
            is_merge, branches = check_merge(badcommit)

    subprocess.call(['git', 'checkout', 'master'])

    print "---------------------------------------"
    print "---------------------------------------"
    print "The bug was introduced in this commit: "
    print badcommit



if __name__=='__main__':
    main()
