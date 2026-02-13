from rest_framework import serializers
from .models import Article


class ArticleSerializer(serializers.ModelSerializer):
    owner_email = serializers.ReadOnlyField(source="owner.email")

    class Meta:
        model = Article
        fields = (
            "id",
            "title",
            "content",
            "owner",
            "owner_email",
            "created_at",
            "updated_at"
        )
        read_only_fields = ("owner", "owner_email", "created_at", "updated_at")
