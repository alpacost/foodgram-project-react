from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=30
    )
    slug = models.SlugField(
        verbose_name='Слаг',
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=20
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        unique=True,
        max_length=50,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=10,
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=150,
        db_index=True,
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeCharacteristic'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeCharacteristic',
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
    )
    image = models.ImageField(
        verbose_name='изображение',
        upload_to='recipes/',
    )

    def __str__(self):
        return self.name


class RecipeCharacteristic(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_characteristic',
        verbose_name='Рецепт'
    )
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipe',
        verbose_name='Ингредиент',
        null=True,
    )
    ingredients_quantity = models.PositiveIntegerField(
        verbose_name='Количество ингредиентов',
        null=True,
    )
    tags = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        null=True,
        related_name='tags_recipe'
    )


class ShopList(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='ShopList',
        verbose_name='Пользователь',
    )
    recipes = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ShopList',
        verbose_name='Список покупок',
    )


class Favorite(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='Favorite',
        verbose_name='Пользователь',
    )
    recipes = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='Favorite',
        verbose_name='Ищбранное',
    )
