from django.shortcuts import render, redirect, HttpResponse
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
        print("wow")


def homepage(request):

    return render(request, 'cheforces/base.html',)


# codeforces open page
def cf_openpage(request):
    #upcoming contests
    url = "https://codeforces.com/api/contest.list?gym=false"
    upcoming_contest = get_api_response(url)
    upcoming_contest=upcoming_contest[0:20]
    before=[]
    completed=[]
    for i in range(len(upcoming_contest)):
        upcoming_contest[i]['startTimeSeconds']=datetime.datetime.fromtimestamp(int(upcoming_contest[i]['startTimeSeconds'])).strftime('%Y-%m-%d %H:%M:%S')
        if upcoming_contest[i]['phase']=="BEFORE":
            before.append(upcoming_contest[i])
        else :
            completed.append(upcoming_contest[i])




    #search form
    form = forms.codeforcesform(request.POST or None)
    if request.method == "POST":
        form = forms.codeforcesform(request.POST)
        if form.is_valid():
            handle = form.cleaned_data.get('CF_handle')
            return redirect('/cfuser/' + handle)
        else:
            form = forms.codeforcesform()

    return render(request, 'cheforces/home.html', {'form': form,
                                                   "before":before,
                                                   "completed" : completed[0:min(len(completed),7)]})


# codeforces homepage


def cf_home(request, handle):
    # getting basic user info
    url = "https://codeforces.com/api/user.info?handles=" + handle

    # getting user submission info
    userinfo = get_api_response(url)
    url = "https://codeforces.com/api/user.status?handle=" + handle
    user_submissions = get_api_response(url)

    # extracting data for verdicts and ratings pie chart

    verdicts = {}
    ratings = {}
    question_tags={}
    langs = {}
    for i in range(len(user_submissions)):
        if 'verdict' in user_submissions[i]:
            verdicts[user_submissions[i]['verdict']] = verdicts.get(user_submissions[i]['verdict'], 0) + 1
            if "rating" in user_submissions[i]["problem"]  and  user_submissions[i]['verdict']=="OK":
                ratings[user_submissions[i]['problem']['rating']] = ratings.get(user_submissions[i]['problem']['rating'], 0) + 1
                for j in range(len(user_submissions[i]['problem']['tags'])):
                    question_tags[user_submissions[i]['problem']['tags'][j]] = question_tags.get(user_submissions[i]['problem']['tags'][j],0)+1
            if user_submissions[i]['verdict']=="OK":
                if user_submissions[i]['programmingLanguage'] in langs :                
                    langs[user_submissions[i]['programmingLanguage']]+=1 
                else :
                    langs[user_submissions[i]['programmingLanguage']]=1




    #tags and verdicts labels for drawing pie chart
    
    ratings_data  = [['RATING','COUNT']]
    ratings_data.extend(dict_to_list(ratings))

    tags_data = [['TAGS','DATA']]
    tags_data.extend(dict_to_list(question_tags))

    verdicts_data = [['VERDICTS', 'COUNT']]
    verdicts_data.extend(dict_to_list(verdicts))

    langs_data = [['LANGUAGE','COUNT']]
    langs_data.extend(dict_to_list(langs))

    return render(request, 'cheforces/cfhome.html', {'userinfo': userinfo[0],
                                                     "verdicts_data": verdicts_data,
                                                     "ratings_data":ratings_data,
                                                     "tags_data": tags_data,
                                                     "langs_data": langs_data
                                                     })



def dict_to_list(dict):
    l=[]
    for i,j in dict.items():
        l.append([str(i),j])
    l = sorted(l, key=lambda x: x[1],reverse=True)
    return l