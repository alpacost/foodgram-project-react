from django.core.validators import RegexValidator

AlphanumericValidator = RegexValidator(
    r'^[0-9a-zA-Z\W]*$', 'Разрешены только латинские буквы и цифры')
