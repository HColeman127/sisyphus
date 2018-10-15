def get_value(arr):
    return arr[0]*1 + arr[1]*2 + arr[2]*5 + arr[3]*10 + arr[4]*20 + arr[5]*50 + arr[6]*100 + arr[7]*200


def next_perm(arr):
    # find the last index with a nonzero value
    last_index = len(arr) - 1

    if arr[last_index] > 0:
        return False
    else:
        while arr[last_index] == 0 and last_index > 0:
            last_index -= 1

        arr[last_index] -= 1
        arr[last_index+1] += 1

        if get_value(arr) > 200:
            temp = arr[last_index]+1
            arr[last_index] = 0
            arr[last_index + 1] = 0

            while arr[last_index] == 0:
                last_index -= 1

                if last_index < 0:
                    return False

            arr[last_index] -= 1
            arr[last_index+1] = temp+1

    return True

# will manually account for one 2 pound coin
total = 1
for i in range(1, 200):
    ps = [0, 0, 0, 0, 0, 0, 0, 0]
    ps[0] = i

    # Permute Distribution ------------
    changed = True
    while changed:
        if get_value(ps) == 200:
            total += 1
        # Try to Permute Distribution---------------------------
        changed = next_perm(ps)
    print(i, total)
