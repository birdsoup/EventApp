from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def hash_password(input):
    """Bcrypt hash an input.

    Args:
        input - the input to hash

    Returns:
        The bcrypt hash of the input.
    """
    return bcrypt.generate_password_hash(input)


def validate(hash, input):
    """Validate an input to a known good bcrypt hash.

    Args:
        hash - the known good bcrypt hash
        input - the input to validate

    Returns:
        True if input validates correctly to hash, false otherwise.
    """
    return bcrypt.check_password_hash(hash, input)
