import redactor
from redactor import redactor
def test_dates():
        text = "Today is Monday 13th March"
        ret  = redactor.redact_gender(text,"test_names.py")
        assert len(ret) == 26
test_dates()
