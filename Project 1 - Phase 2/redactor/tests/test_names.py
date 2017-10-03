import redactor
from redactor import redactor
def test_names():
        text = "Pramod has enrolled to text anlytics course under Dr.Grant from today in the afternoon"
        ret  = redactor.redact_name_loc(text,"--names","test_names.py")
        assert len(ret) == 86
test_names()
