from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Post, Comment
from .forms import PostModelForm, PostForm, CommentForm


# Post 삭제
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    return redirect('post_list')


# Post 수정
def post_edit(request, pk):
    # DB에서 해당 pk와 매칭되는 Post 객체를 가져온다.
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        # 수정처리
        form = PostModelForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            # title, text 필드의 값이 저장이 된다.
            post.author = User.objects.get(username=request.user.username)
            post.published_date = timezone.now()
            # DB에 등록됨
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        # 수정하기 전에 데이터 읽어옴
        form = PostModelForm(instance=post)
    return render(request, 'blog/post_edit1.html', {'form': form})


# Post 등록
@login_required
def post_new(request):
    if request.method == 'POST':
        # Form 데이터 입력하고 등록요청 했을때 save 버튼 눌럿을때
        form = PostForm(request.POST)
        # Form 데이터가 clean한 상태(조건에 맞게 입력된 경우)
        if form.is_valid():
            print(form.cleaned_data)
            post = Post.objects.create(author=User.objects.get(username=request.user.username),
                                       published_date=timezone.now(), title=form.cleaned_data['title'],
                                       text=form.cleaned_data['text'])
            # post = form.save(commit=False)
            # # title, text 필드의 값이 저장이 된다.
            # post.author = User.objects.get(username=request.user.username)
            # post.published_date = timezone.now()
            # # DB에 등록됨
            # post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        # 등록Form 보여주는 부분
        form = PostForm()
    return render(request, 'blog/post_edit1.html', {'form': form})


# Post 상세조회
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


# Post 목록
def post_list(request):
    # name: 'Django'
    # return HttpResponse('''<h2>Post List</h2>
    #     <p>웰컴 {name} !!!</p><p>{content}</p>'''.format(name=name, content=request.content))

    # QuerySet을 사용하여 DB에서 Post목록 가져오기
    # posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    # return render(request, 'blog/post_list.html', {'posts': posts})

    post_list = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    paginator = Paginator(post_list, 2)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post_list.html', {'posts': posts})



# Comment 등록
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment_to_post.html', {'form': form})

# Comment 승인
@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)

# Comment 삭제
@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('post_detail', pk=post_pk)