from blog.models import Comment, Post, Tag
from django.db.models import Count
from django.shortcuts import render


def get_related_posts_count(tag):
    return tag.posts.count()


def add_comments_count_to_posts(posts):
    posts_with_comments = Post.objects.filter(
        id__in=[post.id for post in posts]).annotate(
        comments_count=Count('post_comment'))
    ids_and_comments = posts_with_comments.values_list('id', 'comments_count')
    count_for_id = dict(ids_and_comments)
    for post in posts:
        post.comments_count = count_for_id[post.id]
    return posts


def serialize_tags(tags):
    for tag in tags:
        yield {
            'title': tag.title,
            'posts_with_tag': Post.objects.filter(tags=tag).count(),
        }


def serialize_post(posts):
    for post in posts:
        yield {
            "title": post.title,
            "teaser_text": post.text[:200],
            "author": post.author.username,
            "comments_amount": post.comments_count,
            "image_url": post.image.url if post.image else None,
            "published_at": post.published_at,
            "slug": post.slug,
            "tags": list(serialize_tags(post.tags.all())),
            'first_tag_title': post.tags.all()[0].title,
        }


def index(request):

    # posts_with_comments = Post.objects.filter(
    #     id__in=[post.id for post in posts]).annotate(
    #     comments_count=Count('post_comment'))

    # q = Book.objects.annotate(Count('authors', distinct=True),
    #                           Count('chapters', distinct=True))

    # popular_posts = Post.objects.popular().prefetch_related(
    #      'author').prefetch_related('tags').annotate(Count('author', distinct=True), Count('tags', distinct=True))[:5]
    popular_posts = Post.objects.popular().prefetch_related(
        'author').prefetch_related('tags')[:5]

    most_popular_posts = add_comments_count_to_posts(popular_posts)

    fresh_posts = Post.objects.fresh().prefetch_related('author').prefetch_related('tags')[:5]
    most_fresh_posts = add_comments_count_to_posts(fresh_posts)
    most_popular_tags = Tag.objects.popular()[:5]
    context = {
        'most_popular_posts': list(serialize_post(most_popular_posts)),
        'page_posts': list(serialize_post(most_fresh_posts)),
        'popular_tags': list(serialize_tags(most_popular_tags)),
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):

    post = Post.objects.prefetch_related('author').get(slug=slug)

    comments = Comment.objects.prefetch_related('author').filter(post=post)

    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

    likes = post.likes.all()

    related_tags = post.tags.all()

    serialized_post = {
        "title": post.title,
        "text": post.text,
        "author": post.author.username,
        "comments": serialized_comments,
        'likes_amount': likes.count(),
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": list(serialize_tags(related_tags)),
    }

    most_popular_posts = add_comments_count_to_posts(posts=Post.objects.popular()[:5])
    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        'post': serialized_post,
        'popular_tags': list(serialize_tags(most_popular_tags)),
        'most_popular_posts': list(serialize_post(most_popular_posts)),
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title, count_of_tags=20):
    tag = Tag.objects.get(title=tag_title)

    related_posts = tag.posts.all()[:20]
    related_posts = add_comments_count_to_posts(related_posts)

    most_popular_posts = add_comments_count_to_posts(
        posts=Post.objects.popular()[:5])

    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        "tag": tag.title,
        'popular_tags': list(serialize_tags(most_popular_tags)),
        'posts': list(serialize_post(related_posts)),
        'most_popular_posts': list(serialize_post(most_popular_posts)),
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
