from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=30,
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=20,
        unique=True
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=150,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=30,
    )

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe_name = models.ForeignKey(
        "Recipe",
        on_delete=models.CASCADE,
        related_name='recipe_ingredient',
        verbose_name='Название рецепта'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipe',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество ингредиентов',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe_name', 'ingredient'],
                name='unique ingredients')
        ]


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        db_index=True,
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
    )
    image = models.ImageField(
        verbose_name='изображение',
        upload_to='recipes/',
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class ShopList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ShopList',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ShopList',
        verbose_name='Список покупок',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique shopping list')
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='Favorite',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='Favorite',
        verbose_name='Ищбранное',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique favorite')
        ]
