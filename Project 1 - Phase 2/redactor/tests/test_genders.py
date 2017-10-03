import redactor
from redactor import redactor
def test_genders():
        text = "He is going to the United States for studies"
        ret  = redactor.redact_gender(text,"test_names.py")
        assert len(ret) == 44
test_genders()
