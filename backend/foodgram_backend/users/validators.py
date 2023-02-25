from django.core.validators import RegexValidator

AlphanumericValidator = RegexValidator(
    r'^[0-9a-zA-Z]*$', 'Разрешены только латинские буквы и цифры')
