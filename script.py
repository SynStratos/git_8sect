import subprocess
import sys

sh = sys.argv[3]

def bisect(list, badguy):
    # binary search implementation
    global sh
    script = ['python', sh]

    index = (int)(len(list) / 2)

    commit = list[index]
    print ("checking the commit: " + str(commit))

    response = subprocess.Popen(['git', 'checkout', commit], stdout=subprocess.PIPE)
    response = response.communicate()[0]
    response = subprocess.Popen(script, stdout=subprocess.PIPE)
    response.communicate()[0]
    response = response.returncode

    # TODO: check if special code 125 is needed and decide range of error codes
    # by default, 0 exit code means the commit is a good one



    if len(list) == 1:
        if response == 0:
            print "last check for this branch is good"
            return badguy
        # elif response == 125:
        #
        else:
            print "last check for this branch is bad"
            return commit

    if response == 0:
        print "good"
        badguy = bisect(list[:index], badguy)
    # elif response == 125:
    #    print 'error'
    else:
        print "bad"
        badguy = commit
        if (list.index(badguy) == len(list) - 1):
            print "last check for this branch is bad"
            return badguy
        else:
            badguy = bisect(list[index+1:], badguy)

    return badguy

# this method will check if the commit is a merge node, returning all the branches it is contained
def check_merge(commit):
    branches = subprocess.check_output(['git', 'log', '-1', commit])
    branches = branches.split('\n')[1]
    branches = branches.split(' ')

    if branches[0] == 'Merge:':
        return True, branches[1:]
    else:
        return False, None



def main():
    badcommit = sys.argv[1] # 'master'
    goodcommit = sys.argv[2]


    # TODO: give better error outputs
    if (badcommit == None):
        print "missing parameter"
        return

    if (goodcommit == None):
        print "missing parameter"
        return

    if (sys.argv[3] == None):
        print "missing parameter"
        return

    master_commits = subprocess.check_output(['git', 'rev-list', '--first-parent', badcommit]).split('\n')[:-1]

    list = master_commits.index(goodcommit)
    list = master_commits[:list]

    badcommit = bisect(list, badcommit)

    print badcommit

    is_merge = False

    is_merge, branches = check_merge(badcommit)

    while(is_merge):
        oldbad = badcommit

        for branch in branches[1:]:
            # for each parent branch different from master branch [always the first in parent list]
            other_branches = branches
            # I need the list of branches different from the one I am checking for the '--not' argument of 'git rev-list'
            other_branches.remove(branch)
            command_line = ['git', 'rev-list', badcommit, '--not'] + other_branches

            branch = subprocess.check_output(command_line)
            branch = branch.split('\n')[1:]
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
    print "The bug was introduced in this commit: "
    print badcommit



if __name__=='__main__':
    main()
