from rest_framework import viewsets, status
from rest_framework.response import Response

from users.authentication import JWTAuthentication
from users.permissions import CustomPermission
from users.decorators import login_required
from users.models import BusinessElement, AccessRoleRule
from .models import Article
from .serializers import ArticleSerializer


def can_read_article(request, obj=None):
    user = request.user
    roles = user.roles.all()
    element = BusinessElement.objects.get(name="Article")
    rules = AccessRoleRule.objects.filter(role__in=roles, element=element)

    if rules.filter(read_all_permission=True).exists():
        return True

    if obj and any(rule.read_permission and obj.owner_id == user.id for rule in rules):
        return True

    return False


def can_create_article(request, *args, **kwargs):
    user = request.user
    roles = user.roles.all()
    element = BusinessElement.objects.get(name="Article")
    rules = AccessRoleRule.objects.filter(role__in=roles, element=element)
    return any(rule.create_permission for rule in rules)


def can_update_article(request, obj=None):
    user = request.user
    roles = user.roles.all()
    element = BusinessElement.objects.get(name="Article")
    rules = AccessRoleRule.objects.filter(role__in=roles, element=element)

    if rules.filter(update_all_permission=True).exists():
        return True

    if obj and any(rule.update_permission and obj.owner_id == user.id for rule in rules):
        return True

    return False


def can_delete_article(request, obj=None):
    user = request.user
    roles = user.roles.all()
    element = BusinessElement.objects.get(name="Article")
    rules = AccessRoleRule.objects.filter(role__in=roles, element=element)

    if rules.filter(delete_all_permission=True).exists():
        return True

    if obj and any(rule.delete_permission and obj.owner_id == user.id for rule in rules):
        return True

    return False


class ArticleViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]

    # список статей с учетом ролей
    @login_required()
    def list(self, request):
        user = request.user
        roles = user.roles.all()
        element = BusinessElement.objects.get(name="Article")
        rules = AccessRoleRule.objects.filter(role__in=roles, element=element)

        if rules.filter(read_all_permission=True).exists():
            queryset = Article.objects.all()
        else:
            # только свои статьи
            queryset = Article.objects.filter(owner=user)

        serializer = ArticleSerializer(queryset, many=True)
        return Response(serializer.data)

    # получить одну статью
    @login_required(permission_check=can_read_article)
    def retrieve(self, request, pk=None):
        try:
            article = Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            return Response({"detail": "Статья не найдена"}, status=status.HTTP_404_NOT_FOUND)

        # проверка прав
        allowed = can_read_article(request, obj=article)
        if not allowed:
            return Response({"detail": "Недостаточно прав"}, status=status.HTTP_403_FORBIDDEN)

        serializer = ArticleSerializer(article)
        return Response(serializer.data)

    # создать статью
    @login_required(permission_check=can_create_article)
    def create(self, request):
        serializer = ArticleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # обновить статью
    @login_required(permission_check=can_update_article)
    def update(self, request, pk=None):
        try:
            article = Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            return Response({"detail": "Статья не найдена"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ArticleSerializer(article, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    # удалить статью
    @login_required(permission_check=can_delete_article)
    def destroy(self, request, pk=None):
        try:
            article = Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            return Response({"detail": "Статья не найдена"}, status=status.HTTP_404_NOT_FOUND)

        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
