from django.shortcuts import render, redirect, HttpResponse
from . import forms
import urllib.request as request
import json


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
    return render(request, 'cheforces/base.html')


# codeforces open page
def cf_openpage(request):
    form = forms.codeforcesform(request.POST or None)
    if request.method == "POST":
        form = forms.codeforcesform(request.POST)
        if form.is_valid():
            handle = form.cleaned_data.get('CF_handle')
            return redirect('/cfuser/' + handle)
        else:
            form = forms.codeforcesform()

    return render(request, 'cheforces/home.html', {'form': form})


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
    for i in range(len(user_submissions)):
        verdicts[user_submissions[i]['verdict']] = verdicts.get(user_submissions[i]['verdict'], 0) + 1
        if "rating" in user_submissions[i]["problem"] and user_submissions[i]['verdict']=="OK" :
            ratings[user_submissions[i]['problem']['rating']] = ratings.get(user_submissions[i]['problem']['rating'], 0) + 1
            for j in range(len(user_submissions[i]['problem']['tags'])):
                question_tags[user_submissions[i]['problem']['tags'][j]] = question_tags.get(user_submissions[i]['problem']['tags'][j],0)+1



    tags_labels = list(question_tags.keys())
    tags_data= list(question_tags.values())
    verdicts_labels = list(verdicts.keys())
    verdicts_data = list(verdicts.values())

    ratings_labels = list(ratings.keys())
    ratings_data = list(ratings.values())
    return render(request, 'cheforces/cfhome.html', {'userinfo': userinfo[0],
                                                     "verdicts_labels": verdicts_labels,
                                                     "verdicts_data": verdicts_data,
                                                     "ratings_label":ratings_labels,
                                                     "ratings_data":ratings_data,
                                                     "tags_label": tags_labels,
                                                     "tags_data": tags_data,
                                                     })
