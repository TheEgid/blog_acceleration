from blog.models import Post, Tag, Comment
from django.contrib import admin


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):

    readonly_fields = ('published_at',)

    list_display = ('title',
                    'slug',
                    'image',
                    'author',
                    'published_at',
                    )

    raw_id_fields = ('likes', 'author', 'tags',)

    class Meta:
        ordering = ['-published_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):

    readonly_fields = ('published_at',)

    list_display = ('published_at',
                    'author',
                    'text',
                    'post',
                    )

    raw_id_fields = ('author', 'post',)

    class Meta:
        ordering = ['published_at']


@admin.register(Tag)
class CommentAdmin(admin.ModelAdmin):

    list_display = ('title', )

    class Meta:
        ordering = ["title"]