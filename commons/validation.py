import re

def is_containing_email(email):

    """Check if the email is a valid format."""

    # Regular expression for validating an Email

    regex = r'[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'

    # If the string matches the regex, it is a valid email

    if re.search(regex, email):
        return True
    
    else:
        return False