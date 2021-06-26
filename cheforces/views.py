from django.shortcuts import render, redirect, HttpResponse
from django.http import Http404
from . import forms
import urllib.request as request
import json
import datetime


# getting api response
def get_api_response(url):
    try:
        with request.urlopen(url) as response:

            source = response.read()
            data = json.loads(source)
            data = data['result']
            return data    

    except:
        raise Http404('Codeforces Handle Not Found!!!')


def homepage(request):
    return render(request, 'cheforces/base.html', )


# codeforces open page
def cf_openpage(request):
    # upcoming contests
    url = "https://codeforces.com/api/contest.list?gym=false"
    upcoming_contest = get_api_response(url)
    upcoming_contest = upcoming_contest[0:20]
    before = []
    completed = []
    for i in range(len(upcoming_contest)):
        upcoming_contest[i]['startTimeSeconds'] = datetime.datetime.fromtimestamp(
            int(upcoming_contest[i]['startTimeSeconds']))
        if upcoming_contest[i]['phase'] == "BEFORE":
            before.append(upcoming_contest[i])
        else:
            completed.append(upcoming_contest[i])
            
    # search form
    form = forms.codeforcesform(request.POST or None)
    if request.method == "POST":
        form = forms.codeforcesform(request.POST)
        if form.is_valid():
            handle = form.cleaned_data.get('CF_handle')
            return redirect('/cfuser/' + handle)
        else:
            form = forms.codeforcesform()

    return render(request, 'cheforces/home.html', {'form': form,
                                                   "before": before,
                                                   "completed": completed[0:min(len(completed), 7)]})


# codeforces homepage


def cf_home(request, handle):
    # getting basic user info
    url = "https://codeforces.com/api/user.info?handles=" + handle

    # getting user submission info
    userinfo = get_api_response(url)
    url = "https://codeforces.com/api/user.status?handle=" + handle
    user_submissions = get_api_response(url)


    #getting  user  contest rating data
    url ="https://codeforces.com/api/user.rating?handle="+handle
    d=get_api_response(url)
    # extracting data for verdicts and ratings pie chart

    verdicts = {}
    ratings = {}
    question_tags = {}
    langs = {}
    w_ans = {}
    c_ans = {}
    for i in range(len(user_submissions)):
        if 'verdict' in user_submissions[i]:
            key = '{}/problem/{}/'.format(user_submissions[i]['problem']['contestId'], user_submissions[i]['problem']['index'])
            value = '{}_{}'.format(user_submissions[i]['problem']['contestId'], user_submissions[i]['problem']['index'])
            if user_submissions[i]['verdict'] == "OK":
                if key in w_ans:
                    del(w_ans[key])
                c_ans[key] = value
            else:
                w_ans[key] = value
                if key in c_ans:
                    del(w_ans[key])
            verdicts[user_submissions[i]['verdict']] = verdicts.get(user_submissions[i]['verdict'], 0) + 1
            if "rating" in user_submissions[i]["problem"] and user_submissions[i]['verdict'] == "OK":
                ratings[user_submissions[i]['problem']['rating']] = ratings.get(
                    user_submissions[i]['problem']['rating'], 0) + 1
                for j in range(len(user_submissions[i]['problem']['tags'])):
                    question_tags[user_submissions[i]['problem']['tags'][j]] = question_tags.get(
                        user_submissions[i]['problem']['tags'][j], 0) + 1
            if user_submissions[i]['verdict'] == "OK":
                if user_submissions[i]['programmingLanguage'] in langs:
                    langs[user_submissions[i]['programmingLanguage']] += 1
                else:
                    langs[user_submissions[i]['programmingLanguage']] = 1

    # tags and verdicts labels for drawing pie chart

    ratings_data = [['RATING', 'COUNT']]
    ratings_data.extend(sorted(dict_to_list(ratings),key=lambda x:int(x[0])))

    tags_data = [['TAGS', 'DATA']]
    tags_data.extend(dict_to_list(question_tags))

    verdicts_data = [['VERDICTS', 'COUNT']]
    verdicts_data.extend(dict_to_list(verdicts))

    langs_data = [['LANGUAGE', 'COUNT']]
    langs_data.extend(dict_to_list(langs))

    con_stats = {}
    con_stats['total'] = len(d)
    con_stats['best_rank'] = 10000 * 10000
    con_stats['worst_rank'] = 0
    con_stats['max_plus'] = -1
    con_stats['max_minus'] = 5000

    ratings_timeline = []

    for con in d:
        con_stats['worst_rank'] = max(con['rank'], con_stats['worst_rank'])
        con_stats['best_rank'] = min(con['rank'], con_stats['best_rank'])
        con_stats['max_plus'] = max(con['newRating'] - con['oldRating'], con_stats['max_plus'])
        con_stats['max_minus'] = min(con['newRating'] - con['oldRating'], con_stats['max_minus'])

        date = datetime.date.fromtimestamp(con['ratingUpdateTimeSeconds'])
        newRating = con['newRating']
        rating_change = con['newRating'] - con['oldRating']
        if rating_change >= 0:
            rating_change_str = '+' + str(rating_change)
        else:
            rating_change_str = str(rating_change)
        con_name = con['contestName']
        rank = con['rank']
        tooltip_text = "'Rating: {} ({})\\nRank: {}\\n{}\\n{}'".format(
            newRating,
            rating_change_str,
            rank,
            con_name,
            date.strftime('%Y-%m-%d %H:%M'),
        )
        ratings_timeline.append([con['ratingUpdateTimeSeconds'],newRating,tooltip_text])





    return render(request, 'cheforces/cfhome.html', {'userinfo': userinfo[0],
                                                     "verdicts_data": verdicts_data,
                                                     "ratings_data": ratings_data,
                                                     "tags_data": tags_data,
                                                     "langs_data": langs_data,
                                                     "w_ans": w_ans,
                                                     "solved": len(c_ans),
                                                     "con_stats" : con_stats,
                                                     "ratings_timeline": ratings_timeline
                                                     })


def dict_to_list(dict):
    l = []
    for i, j in dict.items():
        l.append([str(i), j])
    l = sorted(l, key=lambda x: x[1], reverse=True)
    return l
