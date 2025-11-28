from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0017_sync_migrations'),  # 依赖于最新的迁移文件
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='website',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name='categories',
                to='records.website',
                verbose_name='数据来源网站'
            ),
        ),
    ]
