import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "创建初始超级用户（用于首次部署）"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            default=os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin"),
            help="超级用户名",
        )
        parser.add_argument(
            "--email",
            default=os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@example.com"),
            help="邮箱",
        )
        parser.add_argument(
            "--password",
            default=os.environ.get("DJANGO_SUPERUSER_PASSWORD"),
            help="密码（建议通过环境变量传入）",
        )

    def handle(self, *args, **options):
        username = options["username"]
        email = options["email"]
        password = options["password"]

        if not password:
            self.stderr.write(
                self.style.ERROR(
                    "请提供密码：--password 或设置 DJANGO_SUPERUSER_PASSWORD 环境变量"
                )
            )
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"用户 {username} 已存在，跳过创建"))
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"超级用户 {username} 创建成功"))
