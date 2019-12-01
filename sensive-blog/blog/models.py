from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count
from django.db.models.query import Prefetch
from django.urls import reverse


class PostQuerySet(models.QuerySet):

    def get_posts(self):
        return Post.objects

    def fresh(self):
        posts = self.get_posts()
        fresh_posts = posts.order_by('-published_at')
        return fresh_posts

    def popular(self):
        posts = self.get_posts()
        popular_posts = posts.annotate(num_posts=Count('likes')).\
            order_by('-num_posts')
        return popular_posts

    def prefetch_with_tags(self):
        return self.prefetch_related('author'). \
            prefetch_related(Prefetch('tags',
                                      queryset=Tag.objects.annotate(
                                          num_posts_with_tags=Count('posts'))))

    def prefetch_comments_count(self):
        _posts = Post.objects.\
            filter(id__in=Post.objects.values('id')).\
            annotate(comments_count=Count('post_comment'))
        ids_and_comments = _posts.values_list('id', 'comments_count')
        count_for_id = dict(ids_and_comments)
        for post in self:
            post.comments_count = count_for_id[post.id]
        return self


class Post(models.Model):

    objects = PostQuerySet.as_manager()
    title = models.CharField("Заголовок", max_length=200)
    text = models.TextField("Текст")
    slug = models.SlugField("Название в виде url", max_length=200)
    image = models.ImageField("Картинка")
    published_at = models.DateTimeField("Дата и время публикации")

    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор", limit_choices_to={'is_staff': True})
    likes = models.ManyToManyField(User, related_name="liked_posts", verbose_name="Кто лайкнул", blank=True)
    tags = models.ManyToManyField("Tag", related_name="posts", verbose_name="Теги")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args={'slug': self.slug})

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'пост'
        verbose_name_plural = 'посты'


class TagQuerySet(models.QuerySet):

    def popular(self):
        popular_tags = Tag.objects.prefetch_related('posts').annotate(
            num_tags=Count('posts')).order_by('-num_tags')
        return popular_tags

    def prefetch_tags_count(self):
        _tags = Tag.objects.prefetch_related('posts').\
            filter(id__in=Tag.objects.values('id')). \
            annotate(tags_count=Count('posts'))
        ids_and_tags = _tags.values_list('id', 'tags_count')
        count_for_id = dict(ids_and_tags)
        for tag in self:
            tag.tags_count = count_for_id[tag.id]
        return self


class Tag(models.Model):

    objects = TagQuerySet.as_manager()
    title = models.CharField("Тег", max_length=20, unique=True)

    def __str__(self):
        return self.title

    def clean(self):
        self.title = self.title.lower()

    def get_absolute_url(self):
        return reverse('tag_filter', args={'tag_title': self.slug})

    class Meta:
        ordering = ["title"]
        verbose_name = 'тег'
        verbose_name_plural = 'теги'


class Comment(models.Model):

    post = models.ForeignKey("Post", on_delete=models.CASCADE,
                             verbose_name="Пост, к которому написан",
                             related_name="post_comment")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name="Автор")
    text = models.TextField("Текст комментария")
    published_at = models.DateTimeField("Дата и время публикации")

    def __str__(self):
        return f"{self.author.username} under {self.post.title}"

    class Meta:
        ordering = ['published_at']
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
