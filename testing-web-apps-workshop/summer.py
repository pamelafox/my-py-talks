def sum_scores(scores):
    """ Calculates total score based on list of scores.
    """
    total = 1
    for score in scores:
        total += score
    return total

sum_scores([1, 2, 3, 4, 5])