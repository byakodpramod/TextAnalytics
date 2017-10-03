import redactor
from redactor import redactor
def test_places():
        text = "My friend is coming from Dallas today to meet me."
        ret  = redactor.redact_name_loc(text,"--places","test_names.py")
        assert len(ret) == 49
test_places()
