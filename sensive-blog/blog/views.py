from blog.models import Post, Tag
from django.db.models import Count
from django.shortcuts import render, get_object_or_404


def get_most_popular_posts():
    """
    Prefetch and annotate functions so slow and hard for the single request.
    Good to fetch rational small result first and applying theirs after.
    """
    popular_posts_ids = [post.id for post in Post.objects.popular()]
    return Post.objects.filter(id__in=popular_posts_ids). \
        add_comments_count(). \
        prefetch_related('author'). \
        prefetch_with_tags_and_likes(). \
        order_by('likes_count')


def get_most_fresh_posts():
    """
    Prefetch and annotate functions so slow and hard for the single request.
    Good to fetch rational small result first and applying theirs after.
    """
    fresh_posts_ids = [post.id for post in Post.objects.fresh()]
    return Post.objects.filter(id__in=fresh_posts_ids). \
        add_comments_count(). \
        prefetch_related('author'). \
        prefetch_with_tags_and_likes()


def get_tag_related_posts(tag):
    """
    Prefetch and annotate functions so slow and hard for the single request.
    Good to fetch rational small result first and applying theirs after.
    """
    related_posts_ids = [post.id for post in tag.posts.all()[:20]]
    return Post.objects.filter(id__in=related_posts_ids). \
        add_comments_count(). \
        prefetch_related('author'). \
        prefetch_with_tags_and_likes()


def get_most_popular_tags():
    return Tag.objects.popular().order_by('-tag_posts_count')[:5]


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
            'posts_with_tag': tag.tag_posts_count
        }


def serialize_post(post):
    return {
        "title": post.title,
        "teaser_text": post.text[:200],
        "author": post.author.username,
        "comments_amount": post.comments_count,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": post.tags.all(),
        'first_tag_title': post.tags.first().title,
        'likes_amount': post.likes_count,
    }


def serialize_post_detail(post, comments):
    return {
        "title": post.title,
        "text": post.text,
        "author": post.author.username,
        "comments": list(serialize_comments(comments)),
        'likes_amount': post.likes_count,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": post.tags.all(),
    }


def index(request):
    most_popular_posts = get_most_popular_posts()
    most_fresh_posts = get_most_fresh_posts()
    most_popular_tags = get_most_popular_tags()

    context = {
        'most_popular_posts': [serialize_post(post) for post in
                               most_popular_posts],
        'page_posts': [serialize_post(post) for post in most_fresh_posts][::-1],
        'popular_tags': list(serialize_tags(most_popular_tags)),
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = get_object_or_404(Post.objects.select_related('author').
                             annotate(likes_count=Count('likes')), slug=slug)
    comments = post.post_comments.prefetch_related('author')

    serialized_post = serialize_post_detail(post, comments)
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
    tag_related_posts = get_tag_related_posts(tag)

    most_popular_tags = get_most_popular_tags()
    most_popular_posts = get_most_popular_posts()

    context = {
        "tag": tag.title,
        'popular_tags': list(serialize_tags(most_popular_tags)),
        'posts': [serialize_post(post) for post in tag_related_posts],
        'most_popular_posts': [serialize_post(post) for
                               post in most_popular_posts],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
