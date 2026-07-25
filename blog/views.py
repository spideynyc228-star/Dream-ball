from django.shortcuts import get_object_or_404,render
from .models import Article
def index(request):
    query = request.GET.get("q", "").strip()
    articles = Article.objects.all()
    if query:
        from django.db.models import Q
        articles = articles.filter(Q(title__icontains=query) | Q(excerpt__icontains=query) | Q(category__icontains=query))
    return render(request,"blog/index.html",{"articles":articles, "query":query})


def detail(request,slug):
    article = get_object_or_404(Article,slug=slug)
    related = Article.objects.exclude(pk=article.pk).filter(category=article.category)[:3]
    if not related:
        related = Article.objects.exclude(pk=article.pk)[:3]
    return render(request,"blog/detail.html",{"article":article, "related":related})
