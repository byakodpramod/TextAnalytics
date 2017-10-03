import redactor
from redactor import redactor
def test_addresses():
        text = "My friend stay at 1003 E Brooks St, Apt A Norman, OK 73071"
        ret  = redactor.redact_name_loc(text,"--places","test_names.py")
        assert len(ret) == 58
test_addresses()
