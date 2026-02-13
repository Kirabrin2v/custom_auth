from article.models import Article
from users.models import User, Role, BusinessElement, AccessRoleRule


admin_role, _ = Role.objects.get_or_create(name="admin")
moderator_role, _ = Role.objects.get_or_create(name="moderator")
user_role, _ = Role.objects.get_or_create(name="user")

article_element, _ = BusinessElement.objects.get_or_create(name="Article")

admin = User.objects.create(email="admin@example.com", first_name="Admin", last_name="Admin")
admin.set_password("admin123")
admin.roles.add(admin_role)

moderator = User.objects.create(email="moderator@example.com", first_name="Moder", last_name="Moder")
moderator.set_password("moder123")
moderator.roles.add(moderator_role)

user = User.objects.create(email="user@example.com", first_name="User", last_name="User")
user.set_password("user123")
user.roles.add(user_role)

article1 = Article.objects.create(
    title="Статья администратора",
    content="Контент админа",
    author=admin
)
article2 = Article.objects.create(
    title="Статья модератора",
    content="Контент модератора",
    author=moderator
)
article3 = Article.objects.create(
    title="Статья пользователя",
    content="Контент пользователя",
    author=user
)

# Admin может всё
AccessRoleRule.objects.create(role=admin_role, element=article_element,
                              read_permission=True, read_all_permission=True,
                              create_permission=True, update_permission=True,
                              update_all_permission=True,
                              delete_permission=True, delete_all_permission=True)

# Moderator: читать все, удалять все
AccessRoleRule.objects.create(role=moderator_role, element=article_element,
                              read_permission=True, read_all_permission=True,
                              create_permission=True, update_permission=True,
                              delete_permission=True, delete_all_permission=True)

# User: только свои
AccessRoleRule.objects.create(role=user_role, element=article_element,
                              read_permission=True, create_permission=True,
                              update_permission=True, delete_permission=True)

print("Тестовые данные созданы")
