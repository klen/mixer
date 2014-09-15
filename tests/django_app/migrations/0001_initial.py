# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from tests.django_app.models import CustomField
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=20)),
                ('city', models.CharField(unique=True, max_length=20)),
                ('name', models.CharField(max_length=50)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('score', models.IntegerField(default=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('user_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=('auth.user',),
        ),
        migrations.CreateModel(
            name='Door',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('size', models.PositiveIntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Hat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('color', models.CharField(max_length=50, choices=[(b'RD', b'red'), (b'GRN', b'green'), (b'BL', b'blue')])),
                ('brend', models.CharField(default=b'wood', max_length=10)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Hole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=16)),
                ('size', models.SmallIntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField()),
                ('client', models.ForeignKey(to='django_app.Client')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Number',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ColorNumber',
            fields=[
                ('number_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='django_app.Number')),
                ('color', models.CharField(max_length=20)),
            ],
            options={
            },
            bases=('django_app.number',),
        ),
        migrations.CreateModel(
            name='PointA',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PointB',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rabbit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=16)),
                ('username', models.CharField(unique=True, max_length=16)),
                ('active', models.BooleanField(default=True)),
                ('email', models.EmailField(max_length=75)),
                ('text', models.TextField(max_length=512)),
                ('created_at', models.DateField()),
                ('updated_at', models.DateTimeField()),
                ('opened_at', models.TimeField()),
                ('percent', models.FloatField()),
                ('money', models.IntegerField()),
                ('ip', models.IPAddressField()),
                ('ip6', models.GenericIPAddressField(protocol='ipv6')),
                ('picture', models.FileField(upload_to=b'/tmp')),
                ('some_field', models.CommaSeparatedIntegerField(max_length=12)),
                ('funny', models.NullBooleanField()),
                ('slug', models.SlugField()),
                ('speed', models.DecimalField(max_digits=3, decimal_places=1)),
                ('url', models.URLField(default=b'', null=True, blank=True)),
                ('file_path', models.FilePathField()),
                ('object_id', models.PositiveIntegerField()),
                ('error_code', models.PositiveSmallIntegerField()),
                ('custom', CustomField(max_length=24)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Silk',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('color', models.CharField(max_length=20)),
                ('hat', models.ForeignKey(to='django_app.Hat')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Simple',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=20)),
                ('customer', models.ForeignKey(blank=True, to='django_app.Customer', null=True)),
                ('messages', models.ManyToManyField(to='django_app.Message', null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Through',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pointas', models.ForeignKey(to='django_app.PointA')),
                ('pointbs', models.ForeignKey(to='django_app.PointB')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='rabbit',
            name='one2one',
            field=models.OneToOneField(to='django_app.Simple'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pointa',
            name='other',
            field=models.ManyToManyField(to='django_app.PointB', through='django_app.Through'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='number',
            name='doors',
            field=models.ManyToManyField(to='django_app.Door'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='number',
            name='wtf',
            field=models.ManyToManyField(related_name='wtf_rel_+', to='django_app.Number'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='hole',
            name='owner',
            field=models.ForeignKey(to='django_app.Rabbit'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='hat',
            name='owner',
            field=models.ForeignKey(blank=True, to='django_app.Rabbit', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='door',
            name='hole',
            field=models.ForeignKey(to='django_app.Hole'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='door',
            name='owner',
            field=models.ForeignKey(blank=True, to='django_app.Rabbit', null=True),
            preserve_default=True,
        ),
    ]

