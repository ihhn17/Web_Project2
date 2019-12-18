from django.db import models
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:ProductListByCategory', args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', verbose_name="Category", on_delete=models.PROTECT)
    name = models.CharField(max_length=200, db_index=True, verbose_name="Name")
    slug = models.SlugField(max_length=200, db_index=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d/', blank=True, verbose_name="Product image")
    description = models.TextField(blank=True, verbose_name="description")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price")
    stock = models.PositiveIntegerField(verbose_name="In stock")
    available = models.BooleanField(default=True, verbose_name="Available")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        index_together = [
            ['id', 'slug']
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
          return reverse('shop:ProductDetail', args=[self.id, self.slug])

class Comment(models.Model):
    product = models.ForeignKey(Product, related_name="comments", verbose_name="product", on_delete=models.CASCADE)
    username = models.CharField(max_length=50, db_index=True, verbose_name="username")
    text = models.TextField(blank=False, verbose_name="text")

    class Meta:
        ordering = ['username']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

    def __str__(self):
        return "%s: %s" % (self.username, self.text)
