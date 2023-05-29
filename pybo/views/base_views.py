from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.db.models import Count

from pybo.models import Question


def index(request):
    page = request.GET.get('page', '1')  # 페이지
    kw = request.GET.get('kw', '')  # 검색어
    question_list = Question.objects.order_by('-create_date')
    if kw:
        question_list = question_list.filter(
            Q(subject__icontains=kw) |  # 제목
            Q(content__icontains=kw) |  # 내용
            Q(answer__content__icontains=kw) |  # 답변 내용
            Q(author__username__icontains=kw) |  # 질문 글쓴이
            Q(answer__author__username__icontains=kw)  # 답변 글쓴이
        ).distinct()
    paginator = Paginator(question_list, 10)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)
    context = {'question_list': page_obj, 'page': page, 'kw': kw}
    return render(request, 'pybo/question_list.html', context)


def detail(request, question_id):
    page = request.GET.get('comment_page', '1')
    comment_sort = request.GET.get('comment_sort', None)
    question = get_object_or_404(Question, pk=question_id)
    comment_question_list = question.comment_set.all()
    # 정렬
    if comment_sort == 'recent':  # 최신순
        comment_question_list = comment_question_list.order_by('-create_date')
    if comment_sort == 'vote':  # 추천순 , 최신순)
        comment_question_list = comment_question_list.annotate(vote_count=Count('voter')).order_by('-vote_count','-create_date')
    paginator = Paginator(comment_question_list, 5)
    page_obj = paginator.get_page(page)
    context = {'question': question , 'comment_list': page_obj, 'comment_sort': comment_sort}
    return render(request, 'pybo/question_detail.html', context)
