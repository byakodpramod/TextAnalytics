import redactor
from redactor import unredactor
def test_entities():
        text = "My friend Sumit is a fan of movies from a long time"
        a,b,c  = unredactor.get_entity(text)
        print(a)
        assert len(a) == 1
