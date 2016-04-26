# **一些常用DJango命令**

## django-admin startproject mysite
创建一个 mysite的project
目录结构如下：
```
mysite/
    manage.py
    mysite/
        __init__.py
        settings.py
        urls.py
        wsgi.py
```
这些文件是：

* 外层的mysite/根目录仅仅是项目的一个容器。它的命名对Django无关紧要；你可以把它重新命名为任何你喜欢的名字。
* manage.py：一个命令行工具，可以使你用多种方式对Django项目进行交互。 你可以在django-admin和manage.py中读到关于manage.py的所有细节。
* 内层的mysite/目录是你的项目的真正的Python包。它是你导入任何东西时将需要使用的Python包的名字（例如 mysite.urls）。
* mysite/__init__.py：一个空文件，它告诉Python这个目录应该被看做一个Python包。 （如果你是一个Python初学者，关于包的更多内容请阅读Python的官方文档）。
* mysite/settings.py：该Django 项目的设置/配置。Django 设置 将告诉你这些设置如何工作。
* mysite/urls.py：该Django项目的URL声明；你的Django站点的“目录”。 你可以在URL 路由器 中阅读到关于URL的更多内容。
* mysite/wsgi.py：用于你的项目的与WSGI兼容的Web服务器入口。

## 设置数据库
编辑mysite/settings.py 的`DATABASES`节点，设置数据库

##  python manage.py runserver 运行服务器

## python manage.py startapp shops  创建一个应用
应用与项目的关系，一个应用封装了一个模块的管理，一个项目是一组应用的集合。

## 编写shops/models.py 文件，增加模型
```
class Shop(models.Model):
    shop_name = models.CharField(max_length=128)
    shop_url = models.CharField(max_length=128)
    admin_phone = models.CharField(max_length=32)
    admin = models.CharField(max_length=64)
    admin_email = models.CharField(max_length=64)

    def __unicode__(self):
        return ','.join([str(self.id), self.admin, self.shop_name, self.shop_url, self.admin_phone])

    class Meta:
        db_table = "qm_shop_info"
```
## mysite/settings.py文件中，加入新增的应用
```
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'shops',
)
```

## python manage.py makemigrations shops  保存模型的改动

## python manage.py sqlmigrate shops 0001 预览本次变更的sql语句

## python manage.py migrate  执行sql语句，创建表及数据迁移

## python manage.py shell 进入Django的shell环境
```
>>> import django
>>> django.setup()

# import the model
>>> from shops.models import Shop
# query all
>>> Shop.objects.all()

# 创建一条记录并保存
>>> s = Shop(shop_name='jack liang's shop')
>>> s.save()

# 查询id=1 的记录
>>> s = Shop.objects.get(id=1)
# 查询主键等于1的记录
>>> s = Shop.objects.get(pk=1)

# 删除记录
>>> s.delete()
```
