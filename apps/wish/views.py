import datetime
import bcrypt

from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages

from .models import Users, Wishes, Likes


def index(request):
    return render(request, 'wish/index.html')


def register(request):

    errors = Users.objects.check_registration_data(request.POST)
    extra_tags = 'registration_message'
    if len(errors) > 0:
        for _, value in errors.items():
            messages.error(request, value, extra_tags=extra_tags)
        return redirect('/')
    else:
        password_hash = bcrypt.hashpw(
            request.POST['password'].encode(), bcrypt.gensalt())

        new_user = Users.objects.create(
            first_name=request.POST['first_name'], last_name=request.POST['last_name'], email=request.POST['email'], password=password_hash.decode())

        request.session['user_id'] = new_user.id

        messages.success(request, "Thanks for joining us!")
        return redirect('/wishes')


def login(request):
    extra_tags = 'login_message'

    # Step 1 Check Email
    user_list = Users.objects.filter(email=request.POST['email'])

    if not user_list:
        messages.error(request, 'Email not registered', extra_tags=extra_tags)
        return redirect('/')

    # Step 2 Email found, check password
    user = user_list[0]
    password_matched = bcrypt.checkpw(
        request.POST['password'].encode('utf-8'), user.password.encode('utf-8'))

    if not password_matched:
        messages.error(request, 'Password not correct',
                       extra_tags=extra_tags)
        return redirect('/')

    # Step 3 Email and Password all matched, logging in now!
    request.session['user_id'] = user.id

    return redirect('/wishes')


def logout(request):
    del request.session['user_id']
    return redirect('/')


def dash_board(request):
    current_user = Users.objects.get(id=int(request.session['user_id']))
    # display user pending wishes
    user_wishes_pending = Wishes.objects.filter(
        user=current_user, wish_stage=0)
    # display all wishes granted
    all_wished_granted = Wishes.objects.filter(wish_stage=1)

    user_likes = current_user.likes.all()
    user_liked_wishes_id_list = []
    for like in user_likes:
        user_liked_wishes_id_list.append(like.wishes.id)

    context = {
        'current_user': current_user,
        'user_wishes_pending': user_wishes_pending,
        'all_wished_granted': all_wished_granted,
        'user_liked_wishes_id_list': user_liked_wishes_id_list
    }

    return render(request, 'wish/main.html', context)


def new(request):
    current_user = Users.objects.get(id=int(request.session['user_id']))
    context = {
        'current_user': current_user
    }
    return render(request, 'wish/add.html', context)


def add(request):
    extra_tags = 'newwish_message'

    # Check Title
    if len(request.POST['title']) == 0:
        messages.error(
            request, 'A wish must be provided!', extra_tags=extra_tags)
    elif len(request.POST['title']) < 3:
        messages.error(
            request, 'A wish must consist of at least 3 characters!', extra_tags=extra_tags)

    # Check Description
    if len(request.POST['desc']) == 0:
        messages.error(
            request, 'A description must be provided!', extra_tags=extra_tags)
    elif len(request.POST['desc']) < 3:
        messages.error(
            request, 'A description must consist of at least 3 characters!', extra_tags=extra_tags)

    if len(messages.get_messages(request)) > 0:
        return redirect('/wishes/new')

    # The input is valid, continue
    current_user = Users.objects.get(id=int(request.session['user_id']))

    new_wish = Wishes.objects.create(
        title=request.POST['title'], desc=request.POST['desc'], user=current_user)
    return redirect('/wishes')


def edit(request, wish_id):

    current_user = Users.objects.get(id=int(request.session['user_id']))
    this_wish = Wishes.objects.get(id=wish_id)

    context = {
        'current_user': current_user,
        'this_wish': this_wish
    }
    return render(request, 'wish/edit.html', context)


def edit_process(request):
    extra_tags = 'newwish_message'

    # Check Title
    if len(request.POST['title']) == 0:
        messages.error(
            request, 'A wish must be provided!', extra_tags=extra_tags)
    elif len(request.POST['title']) < 3:
        messages.error(
            request, 'A wish must consist of at least 3 characters!', extra_tags=extra_tags)

    # Check Description
    if len(request.POST['desc']) == 0:
        messages.error(
            request, 'A description must be provided!', extra_tags=extra_tags)
    elif len(request.POST['desc']) < 3:
        messages.error(
            request, 'A description must consist of at least 3 characters!', extra_tags=extra_tags)

    if len(messages.get_messages(request)) > 0:
        return redirect('/wishes/edit/' + request.POST['wish_id'])

    # The input is valid, continue

    this_wish = Wishes.objects.get(id=request.POST['wish_id'])
    this_wish.title = request.POST['title']
    this_wish.desc = request.POST['desc']
    this_wish.save()
    return redirect('/wishes')


def remove_process(request):
    this_wish = Wishes.objects.get(id=str(request.POST['wish_id']))
    this_wish.delete()
    return redirect('/wishes')


def granted_process(request):
    this_wish = Wishes.objects.get(id=str(request.POST['wish_id']))
    this_wish.wish_stage = 1
    this_wish.save()
    return redirect('/wishes')


def like_process(request):
    current_user = Users.objects.get(id=int(request.session['user_id']))
    this_wish = Wishes.objects.get(id=str(request.POST['wish_id']))

    new_like = Likes.objects.create(
        likes=1, user=current_user, wishes=this_wish)

    return redirect('/wishes')


def unlike_process(request):
    current_user = Users.objects.get(id=int(request.session['user_id']))
    this_wish = Wishes.objects.get(id=str(request.POST['wish_id']))

    like_list = Likes.objects.filter(user=current_user, wishes=this_wish)
    for like in like_list:
        like.delete()

    return redirect('/wishes')


def stats(request):
    current_user = Users.objects.get(id=int(request.session['user_id']))
    # display user pending wishes
    user_wishes_pending = Wishes.objects.filter(
        user=current_user, wish_stage=0)
    user_wishes_granted = Wishes.objects.filter(
        user=current_user, wish_stage=1)

    # display all wishes granted
    all_wished_granted = Wishes.objects.filter(wish_stage=1)

    context = {
        'current_user': current_user,
        'user_granted_num': str(len(user_wishes_granted)),
        'user_pending_num': str(len(user_wishes_pending)),
        'all_granted_num': str(len(all_wished_granted))

    }
    return render(request, 'wish/stats.html', context)
