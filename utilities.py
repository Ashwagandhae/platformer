def intTuple(tuuple):
    returnList = []
    for i in range(len(tuuple)):
        returnList.append(int(tuuple[i]))
    return tuple(returnList)


def colorShade(color, shade):
    return (
        max(0, min(255, color[0] + shade)),
        max(0, min(255, color[1] + shade)),
        max(0, min(255, color[2] + shade)),
    )
