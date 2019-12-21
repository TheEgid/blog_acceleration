from blog.models import Post, Tag
from django.shortcuts import render


def get_most_popular_posts():
    return Post.objects.popular()[:5].\
        prefetch_with_tags().prefetch_comments_count()


def get_most_popular_tags():
    return Tag.objects.popular()[:5].\
        prefetch_tags_count().order_by('-tags_count')


def get_most_fresh_posts():
    return Post.objects.fresh()[:5].\
        prefetch_with_tags().prefetch_comments_count()


def serialize_comments(comments):
    for comment in comments:
        yield {
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        }


def serialize_tags(tags):
    for tag in tags:
        yield {
            'title': tag.title,
            'posts_with_tag': tag.tags_count
        }


def serialize_posts(posts):
    for post in posts:
        #post_tags = post.tags.all()
        #print(post_tags)
        yield {
            "title": post.title,
            "teaser_text": post.text[:200],
            "author": post.author.username,
            "comments_amount": post.comments_count,
            "image_url": post.image.url if post.image else None,
            "published_at": post.published_at,
            "slug": post.slug,
            "tags": post.tags.all(),
            'first_tag_title': post.tags.first().title,
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
        "tags": post.tags.all()
    }


def index(request):
    most_popular_posts = get_most_popular_posts()
    most_fresh_posts = get_most_fresh_posts()
    most_popular_tags = get_most_popular_tags()

    context = {
        'most_popular_posts': list(serialize_posts(most_popular_posts.prefetch_related('author'))),
        'page_posts': list(serialize_posts(most_fresh_posts.prefetch_related('author'))),
        'popular_tags': list(serialize_tags(most_popular_tags)),
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = Post.objects.get(slug=slug)
    comments = post.post_comments.prefetch_related('author')
    serialized_post = serialize_post(post, comments)

    most_popular_posts = get_most_popular_posts()
    most_popular_tags = get_most_popular_tags()

    context = {
        'post': serialized_post,
        'popular_tags': list(serialize_tags(most_popular_tags)),
        'most_popular_posts': list(serialize_posts(most_popular_posts.
                                                   prefetch_related('author'))),
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)

    related_posts = tag.posts.all()[:20].\
        prefetch_related('author').prefetch_with_tags()

    most_popular_posts = get_most_popular_posts()
    most_popular_tags = get_most_popular_tags()

    context = {
        "tag": tag.title,
        'popular_tags': list(serialize_tags(most_popular_tags)),
        'posts': list(related_posts.prefetch_related('author')),
        'most_popular_posts': list(most_popular_posts.
                                   prefetch_related('author')),
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
