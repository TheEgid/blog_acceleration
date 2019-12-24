from operator import itemgetter

from blog.models import Post, Tag
from django.shortcuts import render, get_object_or_404


def get_most_popular_posts():
    return Post.objects.popular(). \
        prefetch_with_tags(). \
        add_comments_count(). \
        prefetch_related('likes'). \
        prefetch_related('author'). \
        prefetch_related('tags')


def get_most_fresh_posts():
    return Post.objects.fresh(). \
        prefetch_with_tags(). \
        add_comments_count(). \
        prefetch_related('likes'). \
        prefetch_related('author'). \
        prefetch_related('tags')


def get_most_popular_posts_sorted_serialized():
    most_popular_posts_serialized = \
        list(serialize_posts(get_most_popular_posts()))
    return sorted(most_popular_posts_serialized, key=itemgetter('likes_amount'),
                  reverse=True)


def get_most_popular_tags():
    return Tag.objects.popular().prefetch_tags_count().order_by('-tags_count')[:5]


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
            'likes_amount': post.likes.count(),
        }


def serialize_post(post, comments):
    return {
        "title": post.title,
        "text": post.text,
        "author": post.author.username,
        "comments": list(serialize_comments(comments)),
        'likes_amount': post.likes.count(),
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": post.tags.all()
    }


def index(request):
    most_popular_posts = get_most_popular_posts_sorted_serialized()
    most_fresh_posts = get_most_fresh_posts()
    most_popular_tags = get_most_popular_tags()

    context = {
        'most_popular_posts': most_popular_posts,
        'page_posts': list(serialize_posts(most_fresh_posts))[::-1],
        'popular_tags': list(serialize_tags(most_popular_tags)),
    }

    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = get_object_or_404(Post.objects.select_related('author'), slug=slug)
    comments = post.post_comments.prefetch_related('author')
    serialized_post = serialize_post(post, comments)

    most_popular_posts = get_most_popular_posts()
    most_popular_tags = get_most_popular_tags()

    context = {
        'post': serialized_post,
        'popular_tags': list(serialize_tags(most_popular_tags)),
        'most_popular_posts': most_popular_posts,
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)

    related_posts = tag.posts.all()[:20]. \
        prefetch_related('author').prefetch_with_tags()
    most_popular_posts = get_most_popular_posts()
    most_popular_tags = get_most_popular_tags()

    context = {
        "tag": tag.title,
        'popular_tags': list(serialize_tags(most_popular_tags)),
        'posts': list(related_posts.prefetch_related('author').
                      prefetch_related('tags').
                      prefetch_related('likes')
                      ),
        'most_popular_posts': list(most_popular_posts),
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
