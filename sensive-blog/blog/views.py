from blog.models import Comment, Post, Tag
from django.db.models import Count
from django.shortcuts import render


def get_related_posts_count(tag):
    return tag.posts.count()


def serialize_comments(comments):
    for comment in comments:
        yield {
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        }


def add_comments_count(posts):
    posts_with_comments = Post.objects.filter(
        id__in=[post.id for post in posts]).annotate(
        comments_count=Count('post_comment'))
    ids_and_comments = posts_with_comments.values_list('id', 'comments_count')
    count_for_id = dict(ids_and_comments)
    for post in posts:
        post.comments_count = count_for_id[post.id]
    return posts


def add_tags_count(tags):
    tags_with = Tag.objects.filter(
        id__in=[tag.id for tag in tags]).annotate(tags_count=Count('posts'))
    ids_and_tags = tags_with.values_list('id', 'tags_count')
    count_for_id = dict(ids_and_tags)
    for tag in tags:
        tag.tags_count = count_for_id[tag.id]
    return tags


def serialize_tags(tags):
    for tag in tags:
        yield {
            'title': tag.title,
            'posts_with_tag': tag.tags_count
        }


def serialize_posts(posts):
    for post in posts:
        post_tags = list(post.tags.all())
        yield {
            "title": post.title,
            "teaser_text": post.text[:200],
            "author": post.author.username,
            "comments_amount": post.comments_count,
            "image_url": post.image.url if post.image else None,
            "published_at": post.published_at,
            "slug": post.slug,
            "tags": post_tags,
            'first_tag_title': post_tags[0].title,
        }


def serialize_post(post, comments):
    return {
        "title": post.title,
        "text": post.text,
        "author": post.author.username,
        "comments": list(serialize_comments(comments)),
        'likes_amount': post.likes.all().count(),
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": list(post.tags.all()),
    }


def index(request):
    popular_posts = Post.objects.popular()[:5].\
        prefetch_related('author').prefetch_related('tags')
    most_popular_posts = add_comments_count(popular_posts)
    fresh_posts = Post.objects.fresh()[:5].\
        prefetch_related('author').prefetch_related('tags')
    most_fresh_posts = add_comments_count(fresh_posts)

    most_popular_tags = Tag.objects.prefetch_related('post').popular()[:5]
    most_popular_tags = add_tags_count(most_popular_tags)
    context = {
        'most_popular_posts': list(serialize_posts(most_popular_posts)),
        'page_posts': list(serialize_posts(most_fresh_posts)),
        'popular_tags': list(serialize_tags(most_popular_tags)),
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = Post.objects.prefetch_related('author').get(slug=slug)
    comments = Comment.objects.prefetch_related('author').filter(post=post)
    serialized_post = serialize_post(post, comments)
    most_popular_posts = add_comments_count(posts=Post.objects.popular()[:5])
    most_popular_tags = Tag.objects.popular()[:5]
    most_popular_tags = add_tags_count(most_popular_tags)
    context = {
        'post': serialized_post,
        'popular_tags': list(serialize_tags(most_popular_tags)),
        'most_popular_posts': list(serialize_posts(most_popular_posts)),
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)
    related_posts = tag.posts.all()[:20]

    popular_posts = Post.objects.popular()[:5].\
        prefetch_related('author').prefetch_related('tags')

    most_popular_posts = serialize_posts(add_comments_count(popular_posts))

    most_popular_tags = Tag.objects.popular()[:5]
    most_popular_tags = add_tags_count(most_popular_tags)

    context = {
        "tag": tag.title,
        'popular_tags': list(serialize_tags(most_popular_tags)),
        'posts': list(related_posts),
        'most_popular_posts': list(most_popular_posts),
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
