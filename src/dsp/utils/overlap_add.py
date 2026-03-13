def overlap_add(output, segment, position):

    seg_len = len(segment)

    end = position + seg_len

    if end > len(output):
        return False

    output[position:end] += segment

    return True