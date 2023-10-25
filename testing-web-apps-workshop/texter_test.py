# test leet()

def test_leet():
    assert texter.leet('hello') == 'h3llo'

# test clapify()

def test_clapify():
    assert texter.clapify('hello') == 'h👏e👏l👏l👏o'

# test emojify()

def test_emojify():
    assert texter.emojify('happy cake day') == '😊 🎂 day'

# test shortener()

def test_shortener():
    assert texter.shortener('hello') == 'hll'

# test exclamify()

def test_exclamify():
    random.seed(0)
    assert texter.exclamify('hello') == '᥄ hello ‼︎'
