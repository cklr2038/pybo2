from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count

from ..models import Question, Answer, Category

def index(request, category_name='qna'):
    ''''''

    ''''''
    # 입력 인자
    page = request.GET.get('page', '1')     # 페이지
    kw = request.GET.get('kw', '')          # 검색어
    so = request.GET.get('so', 'recent')    # 정렬 기준

    category_list = Category.objects.all()
    category = get_object_or_404(Category, name=category_name)
    question_list = Question.objects.filter(category=category)

    # 정렬
    if so == 'recommend':
        question_list = question_list.annotate(
            num_voter=Count('voter')).order_by('-num_voter', '-create_date')
    elif so == 'popular':
        question_list = question_list.annotate(
            num_answer=Count('answer')).order_by('-num_answer', '-create_date')
    else:   # recent
        question_list = question_list.order_by('-create_date')

    # 조회
    if kw:
        question_list = question_list.filter(
            Q(subject__icontains=kw) |                  # 제목 검색
            Q(content__icontains=kw) |                  # 내용 검색
            Q(author__username__icontains=kw) |         # 질문 글쓴이 검색
            Q(answer__author__username__icontains=kw)   # 답변 글쓴이 검색
        ).distinct()

    # 페이징 처리
    paginator = Paginator(question_list, 10) # 페이지당 10개씩 보여 주기
    page_obj = paginator.get_page(page)

    context = {'question_list': page_obj, 'page': page, 'kw': kw, 'so': so,
               'category_list': category_list, 'category_name': category_name}
    return render(request, 'pybo/question_list.html', context)
    return HttpResponse("안녕하세요 pybo에 오신것을 환영합니다.")

def detail(request, question_id):
    ''''''

    ''''''
    question = get_object_or_404(Question, pk=question_id)

    # 입력
    page = request.GET.get('page', '1')
    so = request.GET.get('so', 'recent')

    if so == 'popular':
        answer_list = Answer.objects.filter(question=question).annotate(num_voter=Count('voter')).order_by('-num_voter',
                                                                                                           '-create_date')
    else:  # recent
        answer_list = Answer.objects.filter(question=question).order_by('-create_date')

    paginator = Paginator(answer_list, 10) # 10개씩 보여주기
    page_obj = paginator.get_page(page)

    question.view_count += 1
    question.save()

    context = {'question': question, 'answer_list': page_obj, 'page': page, 'so': so, 'category': question.category}
    return render(request, 'pybo/question_detail.html', context)