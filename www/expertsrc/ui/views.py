from django.core.context_processors import csrf
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from ui.dbaccess import *
from ui.models import *
from django.utils import simplejson
from django.conf import settings

import datetime
import logging
import random
import dbaccess

def dict_to_json_response(response_dict):
    return HttpResponse(simplejson.dumps(response_dict), mimetype='application/json')

def index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/user/')
    else:
        return HttpResponseRedirect('/login/')

def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/login/')

def login_user(request):
    status = username = ''
    # TODO: write login form class
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if 'next' in request.POST:
                    return HttpResponseRedirect(request.POST['next'])
                else: 
                    return redirect('ui.views.implicit_overview')
            else:
                status = 'Your account has been disabled.'
        else:
            status = 'You entered an incorrect username or password.'
    return render_to_response('expertsrc/login.html',
                              {'msg':status, 'username':username},
                              context_instance=RequestContext(request))

@login_required
def next_review(request):
    """
    TODO: get rid of this and replace it with something less awful.
    """
    user = request.user
    jobs = user.get_review_jobs()

    if(len(jobs) == 0):
        return HttpResponseRedirect('/review/')

    question_info = []

    for job in jobs:
        answer = job.answer.schemamapanswer
        info = [answer.local_field_id, answer.global_attribute_id, answer.is_match]
        question_info.append(':'.join([str(x) for x in info]))

    redirect_base_url = '%s/doit/%s/fields/map?is_review=1&reviewer_id=%s&question_info=%s'
    redirect_url = redirect_base_url % (settings.TAMER_URL, settings.TAMER_DB, user.id, ','.join(question_info))

    return HttpResponseRedirect(redirect_url)

@login_required
def review_home(request):
    user = request.user
    num_jobs = ReviewAssignment.objects.filter(reviewer=user, completed=False).count()
    return render_to_response('expertsrc/review.html', locals())

@login_required
def next_question(request):
    """
    TODO:
    This currently falsely assumes that all questions in the jobs queue will
    have the same type.

    One acceptable, though not optimal, workaround would be do scan through
    the jobs queue and batch together all jobs of the first encountered type
    then return the gui for that question batch.
    """
    user = request.user
    jobs = user.get_jobs()
    if len(jobs) > 0:
        QuestionModel = jobs[0].question.question_type.question_class.model_class() 
        redirect_url = QuestionModel.get_gui_url(user.id, jobs)
        return HttpResponseRedirect(redirect_url)
    else:
        return HttpResponseRedirect('/answer/')

@login_required
def answer_home(request):
    user = request.user
    num_questions = Assignment.objects.filter(answerer=user, completed=False).count()
    return render_to_response('expertsrc/answer.html', locals())

@login_required
def implicit_overview(request):
    username = request.user.username
    return HttpResponseRedirect('/user/name/%s/' % username)

@login_required
def overview_by_uid(request, uid):
    user = get_object_or_404(User, pk=uid)
    return HttpResponseRedirect('/user/name/%s/' % user.username)

#changeme
@login_required
def overview(request, username):
    user = get_object_or_404(User, username=username)
    overview = []
    is_answerer = user.get_profile().user_class == 'ANS'

    if is_answerer:
        overview = get_answerer_domain_overview(user)

    profile_form = UserProfileForm(instance=user.get_profile())
    expertise_form = ExpertiseForm()
    expertise_form.fields["domain"].queryset = \
        Domain.objects.exclude(expertise__user__id__exact=user.get_profile().id)
    full_up = expertise_form.fields["domain"].queryset.count() == 0
    c = {
        'user':user,
        'profile':user.get_profile(),
        'allow_add_domain': is_answerer and not full_up,
        'profile_form':profile_form,
        'expertise_form':expertise_form,
        'overview':overview,
    }
    return render_to_response('expertsrc/userhq.html', c,
                              context_instance=RequestContext(request))

@login_required
def update_profile(request, username):
    user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user.get_profile())
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
    return HttpResponseRedirect('/user/name/%s/' % username)

@login_required
def add_expertise(request, username):
    user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        form = ExpertiseForm(request.POST)
        if form.is_valid():
            expertise = form.save(commit=False)
            expertise.user = user.get_profile()
            expertise.domain = form.cleaned_data['domain']
            expertise.save()
    return HttpResponseRedirect('/user/name/%s/' % username)

@login_required
def user_batches(request):
    user = request.user
    is_answerer = user.get_profile().user_class == 'ANS'
    if is_answerer:
        messages.error(request, 'You are not an asker!')
        return render_to_response('expertsrc/user_batches.html', 
                                  context_instance=RequestContext(request))
    batches = list(Batch.objects.filter(owner=user).order_by('-create_time'))
    check = False
    if 'check' in request.GET:
        check = True
    if batches:
        most_recent = batches[0]
    else:
        messages.error(request, 'You have not imported any batches from Data Tamer.')
    c=locals()
    return render_to_response('expertsrc/user_batches.html', c, 
                              context_instance=RequestContext(request))

@login_required
def batch_panel(request, batch_id):
    user = request.user
    batch = get_object_or_404(Batch, pk=batch_id)

    # TODO: make sure that this model has a batch attribute first....
    QuestionModel = batch.question_type.question_class.model_class()
    questions = QuestionModel.objects.filter(batch=batch)

    c = locals()

    return render_to_response('expertsrc/batch_panel.html', c)

@login_required
def check_for_new_batches(request):
    if request.is_ajax():
        if request.method == 'POST':
            most_recent = request.POST.get('most_recent', False)
            uid = request.POST.get('uid', False)
            owner = User.objects.get(pk=int(uid))

            if most_recent:
                most_recent_dt = datetime.datetime.strptime(most_recent, "%Y-%m-%dT%H:%M:%S.%f")
                batches = list(Batch.objects.filter(create_time__gt=most_recent_dt,owner=owner).order_by('create_time'))
            else:
                batches = list(Batch.objects.filter(owner=owner).order_by('create_time'))

            if len(batches) == 0:
                return HttpResponse('None') 

            c = locals()

            return render_to_response('expertsrc/batch_rows.html', c)

@login_required
def get_allocation_suggestions(request):
    response = dict()
    if request.is_ajax():
        if request.method == 'POST':

            batch = get_object_or_404(Batch, pk=request.POST['batch_id'])
            question_ids = request.POST.getlist('question_ids[]')
            batch_size = len(question_ids)

            sample_size = batch_size * 10

            allocs = get_allocations_by_domain(int(request.POST['domain_id']), 
                                               sample_size=sample_size,
                                               min_size=int(request.POST['min_size']),
                                               max_size=int(request.POST['max_size']),
                                               min_confidence=float(request.POST.get('confidence')),
                                               max_price=float(request.POST.get('price')),)
            if len(allocs) < batch_size:
                response['status'] = 'error'
                response['msg'] = 'Could not allocate users for all questions.'
                return dict_to_json_response(response)

            # select indexes of suggested allocations
            idxs = random.sample(range(len(allocs)), batch_size)
            idx_set = set(idxs)
            response['unused'] = list()
            response['status'] = 'OK'

            for x in range(len(allocs)):
                alloc = allocs[x].get_dict()
                if x in idx_set:
                    # distribute them in no particular order...
                    qid = random.choice(question_ids)
                    question_ids.remove(qid)
                    response[qid] = alloc
                else:
                    response['unused'].append(alloc)

            return dict_to_json_response(response)
    else:
        response['status'] = 'error'
        return dict_to_json_response(response)

@login_required
def commit_allocations(request):
    if request.is_ajax():
        if request.method == 'POST':
            user = request.user

            question_ids = request.POST.getlist('question_ids[]', False)
            allocs = request.POST.getlist('allocs[]', False)
            batch_id = request.POST.get('batch_id', False)
            price = request.POST.get('price', False)

            response = dict()

            if not all([allocs, question_ids, batch_id, price]):
                response['status'] = 'failure'
                response['msg'] = 'Missing inputs.'
                return dict_to_json_response(response)

            if len(question_ids) != len(allocs):
                response['status'] = 'failure'
                response['msg'] = 'Numbers of questions and allocations do not match.'
                return dict_to_json_response(response)

            batch = Batch.objects.get(pk=int(batch_id))

            try:
                user.pay_out(batch, float(price))
            except InsufficientFundsException as e:
                response['status'] = 'failure'
                response['msg'] = str(e) # TODO: change this.
                return dict_to_json_response(response)

            for x in range(len(question_ids)):
                q = BaseQuestion.objects.get(pk=int(question_ids[x]))
                for uid in allocs[x].split(','):
                    assn = Assignment()
                    assn.answerer = User.objects.get(pk=int(uid))
                    assn.question = q
                    assn.agreed_price = get_overview_record(assn.answerer, q.domain)['price']
                    assn.complete = False
                    assn.save()

            batch.is_allocated = True
            batch.save()
            response['status'] = 'success'
            response['msg'] = 'Committed successfully.'
            return dict_to_json_response(response)

def update_prices(request):
    return dict_to_json_response(dbaccess.update_prices())

# TODO:
# deep-six import_schema_map_questions and import_schema_map_answers
def import_schema_map_questions(request):
    return HttpResponseRedirect('/batches/')

def import_schema_map_answers(request):
    return HttpResponseRedirect('/answer/')
###

def redirect_to_tamer(request):
    return HttpResponseRedirect("%s/tamer/%s" % (settings.TAMER_URL, settings.TAMER_DB,))

def global_user_overview(request):
    overview = get_global_user_overview()
    c = locals()
    return render_to_response('expertsrc/user_overview.html' , c)

def batch_overview(request, batch_id):
    batch = get_object_or_404(Batch, pk=batch_id)
    overview = list()
    for record in get_batch_overview(batch.id):
        new_rec = dict()
        new_rec['local_field_name'] = record['local_field_name']
        new_rec['number_allocated'] = record['number_allocated']
        new_rec['progress'] = float(record['number_completed']) / record['number_allocated'] * 100
        new_rec['confidence'] = record['conf']
        overview.append(new_rec)
    c = locals()
    return render_to_response('expertsrc/batch_overview.html', c)

