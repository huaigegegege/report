from django.shortcuts import render,redirect
from django.http import HttpRequest,HttpResponse
import requests
import json
from datetime import datetime
from app.display import display
from app.controls import controls

# Create your views here.

def query_month(request):
    assert isinstance(request, HttpRequest)
    type=''
    starttime=''
    endtime=''
    if request.method == "POST":
        type=request.POST.get('hidetype')
        starttime=request.POST.get('dtp_input1')
        endtime=request.POST.get('dtp_input2')
        type=type.replace(' ', '').lower()
        print(type)
    if type == "offerbymonth":  
        show=controls.offer_by_month(starttime, endtime)
    elif type=='publisherbymonth':
        show=controls.publisher_by_month(starttime, endtime)
    elif type=='s500customerbymonth':
        show=controls.s500_customer_by_month(starttime, endtime)
    show.type=type
    return render(request,'index.html', {'show':show})

def query(request, type):
    assert isinstance(request, HttpRequest)
    #type=''
    #if request.method == "POST":
    #    type=request.POST.get('type')
    #    print(type)
        
    if type=='allpublisher':
        show=controls.all_publisher()
    elif type=='blockedduetonompnidornooffer':
        show=controls.blocked_due_to_nompnid_or_nooffer()
    elif type=='havempnidbutnooffer':
        show=controls.have_mpnid_but_nooffer()
    elif type=='publishvmorarm':
        show=controls.publish_vm_or_arm()
    elif type=='onlypublishcs':
        show=controls.only_publish_cs()
    elif type == "offerbymonth":
        starttime=request.POST.get('starttime')
        endtime=request.POST.get('endtime')
        show=controls.offer_by_month(starttime, endtime)
    elif type=='publisherbymonth':
        starttime=request.POST.get('starttime')
        endtime=request.POST.get('endtime')
        show=controls.publisher_by_month(starttime, endtime)
    elif type=='s500customerbmonth':
        show=controls.s500_customer_by_month()
    show.type=type
    return render(request, 'index.html', {'show':show})

def sync(request):
    assert isinstance(request, HttpRequest)
    authority=''
    if request.method == 'POST':
        authority=request.POST.get('authrization')
    
    show=display()
    show.type='overview'
    if authority == '':
        show.emsg='Please input authrization !'
        return render(request, 'index.html', {
            'show': show
        }) 
    headers={
        'content-type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0',
        'Authorization': authority
    }
    try:
        resp = requests.get('https://cloudpartner.azure.cn/api/initialize?api-version=2016-08-01-preview', data=None, headers=headers)
        if resp.status_code == 200:
            controls.sync('https://cloudpartner.azure.cn/api/publishers?api-version=2016-08-01-preview',headers,'save_publisher')
            controls.sync('https://cloudpartner.azure.cn/api/offers?api-version=2016-08-01-preview&includeStatus=true',headers,'save_offer')
            controls.sync('https://cloudpartner.azure.cn/api/readableroleassignments?api-version=2016-08-01-preview',headers,'save_provider')
            show.msg='sync success'        
            show.emsg=''
        else:
            show.emsg = 'Please input the newest authrization !!!'
            show.msg='' 
    except Exception as e:
        show.emsg='Please input the newest authrization !!!'
        show.msg=''

    return render(request, 'index.html', {
        'show': show
    })


def index(request):
    return render(request, 'index.html', {
        'show': display
    })