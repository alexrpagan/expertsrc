import csv
import datetime
import logging

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404, render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from django.conf import settings

from ui.workerstats.allocations import conf
import ui.workerstats.allocations as allc
import ui.pricing.dynprice as dp

from ui.dbaccess import *
from ui.models import *


logger = logging.getLogger(__name__)


def dict_to_json_response(response_dict):
    return HttpResponse(simplejson.dumps(response_dict), mimetype='application/json')


def index(request):
    if request.user.is_authenticated():
        return redirect('resolve_user')
    else:
        return redirect('login')


def logout_user(request):
    logout(request)
    return redirect('login')


def expose_urls(urllist):
    ret = []
    for u in urllist:
        if isinstance(u, str):
            ret.append((u, reverse(u)))
        elif isinstance(u, (list, tuple)):
            ret.append((u[0], reverse(u, args=u[1])))
    return ret


def login_user(request):
    status = username = ''
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if 'next' in request.POST:
                    # make sure this works with prefix
                    return HttpResponseRedirect(request.POST['next'])
                else:
                    return redirect('resolve_user')
            else:
                status = 'Your account has been disabled.'
        else:
            status = 'You entered an incorrect username or password.'
    return render(request, 'expertsrc/login.html', {'msg': status, 'username': username})


@login_required
def next_question(request, domain_id):
    user = request.user
    domain = get_object_or_404(Domain, id=domain_id)
    jobs = user.get_jobs(domain)
    jobs_by_type = {}
    if len(jobs) > 0:
        for job in jobs:
            QuestionModel = job.question.question_type.question_class.model_class()
            l = jobs_by_type.setdefault(QuestionModel, [])
            l.append(job)
        for model_class in jobs_by_type.keys():
            if len(jobs_by_type[model_class]) > 0:
                cands = sorted(jobs_by_type[model_class], key=lambda x: x.question.batch.id)
                batch_id = cands[0].question.batch.id
                for x in range(len(cands)):
                    if cands[x].question.batch.id != batch_id:
                        break
                page_limit = 10
                idx = x
                if x >= page_limit:
                    idx = page_limit
                elif x == len(cands) - 1:
                    idx = x + 1
                redirect_url = model_class.get_gui_url(user.id, cands[:idx])
                return HttpResponseRedirect(redirect_url)
    else:
        return redirect('index')


@login_required
def answer_home(request):
    user = request.user
    context = {}
    num_questions = Assignment.objects.filter(answerer=user, completed=False).count()
    context['num_questions'] = num_questions
    context['user'] = user
    context['display_interview'] = 0
    if user.get_profile().has_been_assigned and num_questions == 0:
# uncomment to get interview form
#        context['display_interview'] = 1
        pass
    if request.method == 'POST':
        context['form'] = form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = Feedback()
            feedback.user = user
            feedback.sentiment = form.cleaned_data['sentiment']
            feedback.improvements = form.cleaned_data['improvements']
            feedback.comments = form.cleaned_data['comments']
            feedback.save()
            return redirect('thanks')
        return render(request, 'expertsrc/answer.html', context)
    context['form'] = FeedbackForm()
    return render(request, 'expertsrc/answer.html', context)


@login_required
def thanks_and_goodbye(request):
    user = request.user
    profile = user.get_profile()
    profile.has_been_assigned = False
    profile.save()
    #TODO: set to true and test
    disable_account = True
    logout(request)
    if disable_account:
        user.is_active = False
        user.save()
    return render(request, 'expertsrc/thanks_and_goodbye.html')


@login_required
def implicit_overview(request):
    return redirect('user_by_name', username=request.user.username)


@login_required
def overview_by_uid(request, uid):
    user = get_object_or_404(User, pk=uid)
    return redirect('user_by_name', username=user.username)


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
#    full_up = expertise_form.fields["domain"].queryset.count() == 0
    c = {
        'user': user,
        'profile': user.get_profile(),
        'is_answerer': is_answerer,
        'allow_add_domain': False,
#        'allow_add_domain': is_answerer and not full_up,
        'profile_form': profile_form,
        'expertise_form': expertise_form,
        'overview': overview,
    }
    return render(request, 'expertsrc/userhq.html', c)


@login_required
def update_profile(request, username):
    user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user.get_profile())
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
    return redirect('user_by_name', username=username)


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
    return redirect('user_by_name', username=username)


@login_required
def user_batches(request):
    user = request.user
    is_answerer = user.get_profile().user_class == 'ANS'
    if is_answerer:
        messages.error(request, 'You are not an asker!')
        return render(request, 'expertsrc/user_batches.html')
    batches = list(Batch.objects.filter(owner=user).order_by('-create_time'))
    check = False
    if 'check' in request.GET:
        check = True
    if not batches:
        messages.error(request, 'You have not imported any batches from Data Tamer.')
    url_context = expose_urls(('check_for_new_batches',))
    c = {
        'user': user,
        'check': check,
        'batches': batches,
        'url_context': url_context
    }
    return render(request, 'expertsrc/user_batches.html', c)


@login_required
def batch_panel(request, batch_id):
    user = request.user
    batch = get_object_or_404(Batch, pk=batch_id)
    # TODO: make sure that this model has a batch attribute first....
    QuestionModel = batch.question_type.question_class.model_class()
    questions = QuestionModel.objects.filter(batch=batch)
    profile = user.get_profile()
    url_context = expose_urls(('get_allocation_suggestions', 'commit_allocations',))
    c = {
        'user': user,
        'batch': batch,
        'profile': profile,
        'questions': questions,
        'url_context': url_context
    }
    return render(request, 'expertsrc/batch_panel.html', c)


@login_required
def check_for_new_batches(request):
    if request.is_ajax():
        if request.method == 'POST':
            most_recent = request.POST.get('most_recent', False)
            uid = request.POST.get('uid', False)
            owner = User.objects.get(pk=int(uid))
            if most_recent:
                most_recent_dt = datetime.datetime.strptime(most_recent, "%Y-%m-%dT%H:%M:%S.%f")
                batches = list(Batch.objects.filter(create_time__gt=most_recent_dt, owner=owner).order_by('create_time'))
            else:
                batches = list(Batch.objects.filter(owner=owner).order_by('create_time'))
            if len(batches) == 0:
                return HttpResponse('None')
            c = {'batches': batches}
            return render(request, 'expertsrc/batch_rows.html', c)


@login_required
def get_allocation_suggestions(request):
    response = {}
    if request.is_ajax():
        if request.method == 'POST':
            get_object_or_404(Batch, pk=request.POST['batch_id'])
            alg_type = request.POST.get('alg_type')
            domain_id = request.POST.get('domain_id')
            question_ids = request.POST.getlist('question_ids[]')
            batch_size = len(question_ids)
            allocs = []
            if alg_type == 'max_conf':
                max_price = request.POST.get('price')
                allocs = max_conf(domain_id, float(max_price), batch_size)
            elif alg_type == 'min_price':
                min_conf = request.POST.get('confidence')
                allocs = min_price(domain_id, float(min_conf) / 100.0, batch_size)
            else:
                response['status'] = 'error'
                response['msg'] = 'Unrecognized allocation selection algorithm.'
                return dict_to_json_response(response)
            if len(allocs) < batch_size:
                response['status'] = 'error'
                response['msg'] = 'Could not allocate users for all questions.'
                return dict_to_json_response(response)
            response['status'] = 'OK'
            response['unused'] = []
            for idx in xrange(batch_size):
                response[question_ids[idx]] = allocs[idx].get_dict()
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
            domain_id = None
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
                response['msg'] = str(e)  # TODO: change this.
                return dict_to_json_response(response)
            for x in range(len(question_ids)):
                q = BaseQuestion.objects.get(pk=int(question_ids[x]))
                if domain_id is None:
                    domain_id = q.domain_id
                for uid in allocs[x].split(','):
                    assn = Assignment()
                    assn.answerer = User.objects.get(pk=int(uid))
                    assn.question = q
                    assn.agreed_price = get_overview_record(assn.answerer, q.domain)['price']
                    assn.complete = False
                    assn.save()
                    # remove after initial demo
                    profile = assn.answerer.get_profile()
                    profile.has_been_assigned = True
                    profile.save()
            batch.is_allocated = True
            batch.save()
            # TODO: get rid of this.
            assert domain_id is not None
            if settings.LOG_MARKET_STATS:
                log_market_stats(domain_id)
            if settings.DYNPRICING:
                # update prices in level records
                dp.update_prices()
                # update prices in allocation stems
                allc.update_prices(domain_id)
            response['status'] = 'success'
            response['msg'] = 'Committed successfully. Redirecting...'
            return dict_to_json_response(response)


def import_schema_map_questions(request):
    return HttpResponseRedirect('/batches/?check')


def about(request):
    user = request.user
    c = {'user': user}
    return render(request, 'expertsrc/about.html', c)


def redirect_to_tamer(request):
    return HttpResponseRedirect("%s/tamer/%s" % (settings.TAMER_URL, settings.TAMER_DB,))


def global_user_overview(request):
    user = request.user
    overview = get_global_user_overview()
    c = {'user': user, 'overview': overview}
    return render(request, 'expertsrc/user_overview.html', c)


def batch_overview(request, batch_id):
    user = request.user
    batch = get_object_or_404(Batch, pk=batch_id)
    overview = list()
    for record in get_batch_overview(batch.id):
        new_rec = dict()
        number_allocated = len(record['user_confs'])
        new_rec['question_id'] = record['question_id']
        new_rec['number_allocated'] = number_allocated
        new_rec['progress'] = float(record['number_completed']) / number_allocated * 100
        new_rec['confidence'] = conf(record['user_confs'])
        new_rec['price'] = record['total_price']
        overview.append(new_rec)
    c = {
        'user': user,
        'batch': batch,
        'overview': overview
    }
    return render(request, 'expertsrc/batch_overview.html', c)


@login_required
def domain_overview(request):
    user = request.user
    domains = Domain.objects.all()
    c = {
        'user': user,
        'domains': domains
    }
    return render(request, 'expertsrc/domain_overview.html', c)


@login_required
def domain_details(request, domain_id):
    user = request.user
    domain = get_object_or_404(Domain, pk=domain_id)
    overview = get_user_overview(domain_id)
    acc_data = ','.join([str(o['accuracy']) for o in overview])
    c = {
        'user': user,
        'domain': domain,
        'overview': overview,
        'acc_data': acc_data
    }
    return render(request, 'expertsrc/domain_details.html', c)


def avail_data(request, domain_id):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename="avail-data.csv"'
    writer = csv.writer(response)
    avail_raw = get_avail_data(domain_id)
    for row in avail_raw:
        writer.writerow(row)
    return response


def price_data(request, domain_id):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename="price-data.csv"'
    writer = csv.writer(response)
    price_raw = get_price_data(domain_id)
    for row in price_raw:
        writer.writerow(row)
    return response
