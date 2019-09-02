import subprocess
import sys



def bisect(list, badguy):
    # binary search implementation
    script = sys.argv[3]

    index = (int)(list.length / 2)
    commit = list[index]
    respo = subprocess.check_output(['git', 'checkout', commit])
    response = subprocess.check_output(script)

    if list.length == 1:
        if response == 0:
            return badguy
        # elif response == 125:
        #
        else:
            return commit

    if response == 0:
        badguy = bisect(list[:index], badguy)
    # elif response == 125:
    #    print 'error'
    else:
        badguy = commit
        badguy = bisect(list[index:], badguy)

    return badguy

def check_merge(commit):
    branches = subprocess.check_output(['git', 'log', '-1', commit])
    branches = branches.split('\n')[1]
    branches = branches.split(' ')

    if branches[0] == 'Merge:':
        return True, branches
    else:
        return False, branches



def main():
    badcommit = sys.argv[1] # 'master'
    goodcommit = sys.argv[2]


    if (badcommit == None):
        print "missing parameter" # give better err
        return

    if (goodcommit == None):
        print "missing parameter"
        return

    if (sys.argv[3] == None):
        print "missing parameter"
        return

    master_commits = subprocess.check_output(['git', 'rev-list', '--first-parent', badcommit]).split('\n')[:-1]

    list = master_commits.indexof(goodcommit)
    list = master_commits[:list]

    badcommit = bisect(list, badcommit)

# TODO: fare while su risultato della ricerca nei branch finchè il nodo output non è un nodo di merge -> nel caso di merge innestati

    is_merge = False

    is_merge, branches = check_merge(badcommit)

    while(is_merge):
        oldbad = badcommit

        for branch in branches[1:]:
            other_branches = branches
            other_branches = other_branches.remove(branch)
            command_line = ['git', 'rev-list', badcommit, '--not'] + other_branches

            branch = subprocess.check_output(command_line)

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
        else
            # check if the new selected bad commit is a merge node itself
            # if is_merge is False the loop will stop
            is_merge, branches = check_merge(badcommit)

    print "The bug was introduced in this commit: "
    print badcommit




        #repeat process on new branches


    #check if other branches -> merge commit      rev-list
    # git rev-list f4c92ecd85144098653542a164a8e79a39f79ed3^2 --not f4c92ecd85144098653542a164a8e79a39f79ed3^
    #repeat search for each branch merged in the commit
    # TODO: for sha1^i -> not con master -> se no output stoppo


if __name__=='__main__':
    main()
