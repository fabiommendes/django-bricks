def flatten(seq, seqtypes=(list, tuple)):
    """
    Flatten a sequence of sequences.

    Returns:
        A flattened list.
    """

    result = []
    tasks = [iter(seq)]
    while tasks:
        try:
            elem = next(tasks[-1])
            if isinstance(elem, seqtypes):
                tasks.append(iter(elem))
            else:
                result.append(elem)
        except StopIteration:
            tasks.pop()
    return result