"""
用户模型
对应数据库 users 表
"""
from tortoise import fields
from tortoise.models import Model


class User(Model):
    """
    用户表模型
    存储用户基本信息和认证凭据
    """

    id = fields.IntField(pk=True, description="用户ID")
    username = fields.CharField(max_length=50, unique=True, description="用户名")
    email = fields.CharField(max_length=100, unique=True, description="邮箱")
    password_hash = fields.CharField(max_length=255, description="密码哈希")
    avatar_url = fields.CharField(max_length=255, null=True, description="头像URL")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "users"
        table_description = "用户基本信息表"

    def __str__(self):
        return f"User(id={self.id}, username={self.username})"

    def __repr__(self):
        return f"<User {self.username}>"
