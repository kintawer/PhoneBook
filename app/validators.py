from wtforms.validators import ValidationError


def validate_ru_number(form, number):
    # ex 8 911 940 50 20
    # ex +7 911 940 50 20
    if not number.data:
        return

    if number.data[0] == '+':
        if not number.data[1:].isdigit():
            raise ValidationError('Please enter an integer phone number')
        if len(number.data) != 12:
            raise ValidationError('Please check phone number')
    else:
        if not number.data.isdigit():
            raise ValidationError('Please enter an integer phone number')
        if len(number.data) != 11:
            raise ValidationError('Please check phone number')