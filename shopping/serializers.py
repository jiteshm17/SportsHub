from .models import Product, Category
from rest_framework import serializers


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField(method_name='get_category')

    class Meta:
        model = Product
        fields = ['pk', 'prod_name', 'description', 'cost', 'brand', 'category', 'stock', 'weight']

    def get_category(self, obj):
        return obj.category.cat_name


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['cat_name']
