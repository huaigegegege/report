import json
from app.models import offer,publisher,provider
from app.display import display
import requests
from multiprocessing import Pool
import pyodbc
from app.sqlutils import SqlUtils
from django.db.models import Q,Count
import pandas as pd

class controls(object):
     
    @classmethod
    def request_cpp(cls, url, headers, type):
        res = requests.get(url, data=None, headers=headers) 
        resp = res.json()
        json_str = json.dumps(resp)
        params_json = json.loads(json_str)
        if type == "save_offer": 
            offer.objects.all().delete()
            for ch in params_json:
                offer.objects.create(
                    offerid=ch['id'],
                    publisher_id=ch['publisherId'],
                    display_text=ch['displayText'],
                    publisher_name=ch['publisherName'] if 'publisherName' in ch else '',
                    offer_type_name=ch['offerTypeName'],
                    status=ch['status'],
                    version=ch['version'],
                    change_time = ch['changedTime'],
                ).save()
        elif type == "save_publisher":
            publisher.objects.all().delete()
            for ch in params_json:
                publisher.objects.create(
                    version=ch['version'],
                    publisher_id=ch['id'],
                    display_text=ch['definition']['displayText'],
                    microsoft_partner_network_id=ch['definition']['microsoftPartnerNetworkId'],
                    public_publisher_id=ch['definition']['publicPublisherId'],
                    legacy_publisher_id= ch['definition']['legacyPublisherId'] if 'legacyPublisherId' in ch['definition'] else '',
                    expired_time=ch['definition']['expiredTime'],
                    changed_time=ch['changedTime'],
                ).save()
        elif type == 'save_provider':
            provider.objects.all().delete()
            for ch in params_json:
                provider.objects.create(
                    upn=ch['upn'],
                    scope=ch['scope'],
                    publisher_name=ch['publisherName'] if 'publisherName' in ch else '',
                    role_name=ch['roleName'],
                    role_type=ch['roleType'],
                    manageable=ch['manageable'],
                ).save()
        return 1

    @classmethod
    def callback(cls, args):
        print(args)

    @classmethod                      
    def sync(cls, url, headers, type):
        pool = Pool(3)
        pool.apply_async(func=cls.request_cpp(url, headers,type), callback=cls.callback)

    @classmethod
    def offer_by_month(cls, starttime, endtime):
        alloffers = offer.objects.filter(Q(status='notStarted') | Q(status='succeeded') | Q(status='waitingForPublisherReview')).count()        
        sql="""
select [Name],[DeploymentTypeName] OffType,[PublisherId],[CompanyName],RequestType,SumOfNewOffer,TotalOfNewOffer,{AllOfOffer} AllOfOffer,dateofapproval PublishedTime  from
(SELECT [Name],[ISVId],[DeploymentTypeName],[PublisherId],[CompanyName],[VhdId],[Status],min([RequestType]) [RequestType],max(dateofapproval) dateofapproval
  FROM [dbo].[V_Requests] where [DateOfApproval]>'{starttime}' and [DateOfApproval]<'{endtime}' and Status=3 
  group by [Name],[ISVId],[DeploymentTypeName],[PublisherId],[CompanyName],[VhdId],[Status]) a left join (select count(*) SumOfNewOffer from 
  (SELECT [Name],[ISVId],[DeploymentTypeName],[PublisherId],[CompanyName],[VhdId],[Status],min([RequestType]) [RequestType]
  FROM [dbo].[V_Requests] where [DateOfApproval]>'{starttime}' and [DateOfApproval]<'{endtime}' and Status=3 
  group by [Name],[ISVId],[DeploymentTypeName],[PublisherId],[CompanyName],[VhdId],[Status]) b where RequestType='New Offer') bx on 1=1 left join((select count(*) TotalOfNewOffer from 
  (SELECT [Name],[ISVId],[DeploymentTypeName],[PublisherId],[CompanyName],[VhdId],[Status],min([RequestType]) [RequestType]
  FROM [dbo].[V_Requests] where [DateOfApproval]>'{starttime}' and [DateOfApproval]<'{endtime}' and Status=3 
  group by [Name],[ISVId],[DeploymentTypeName],[PublisherId],[CompanyName],[VhdId],[Status]) b) ) bxx on 1=1""".format(
    starttime=starttime, endtime=endtime, AllOfOffer=alloffers)
        show=display()
        ds = SqlUtils.query(sql)
        if len(ds) > 0:
            for col in ds[0].cursor_description:
                show.header.append(col[0])
            show.body = ds
        return show
    
    @classmethod
    def publisher_by_month(cls, starttime, endtime):
        sql='''
        select DisplayName,PublisherID,PublicPublisherid,MPNID,SumOfNewPublisher,{list_publisher} allPublisher,CreateTime from (
select DisplayName,PublisherID,CreateTime,PublicPublisherid,MPNID from isvs where CreateTime between '{starttime}' and '{endtime}') a
left join (select count(1) SumOfNewPublisher from isvs where CreateTime between '{starttime}' and '{endtime}') b on 1=1'''.format(
    starttime=starttime, endtime=endtime, list_publisher=publisher.objects.count()
)
        show=display()
        ds=SqlUtils.query(sql)
        if len(ds) > 0:
            for col in ds[0].cursor_description:
                show.header.append(col[0])
            show.body = ds
        return show
    
    @classmethod
    def s500_customer_by_month(cls, starttime, endtime):
        url="https://powerbi4excel.blob.core.chinacloudapi.cn/powerbi/EA-SubscriptionID.xlsx?sp=r&st=2019-12-22T07:05:04Z&se=2050-12-23T15:05:04Z&spr=https&sv=2019-02-02&sr=b&sig=IpQiSBCogl0Xq95QoUXLQLF%2BRnf9RUPLcT6ALme4Jvk%3D"
        data = pd.read_excel(url)
        #header =  data.columns.values
        #for item in data.values:
        
        isExists=[]
        for dpt in publisher.objects.values('publisher_id','display_text'):
            for gname in data.values:
                if dpt['display_text'] in gname[2]:
                    isExists.append(dpt['publisher_id'])
        
        show=display()
        show.header=['publisher_id', 'publisher_name', 'display_text', 'offer_type_name','offerid','allS500Offer','change_time']
        ds_total=offer.objects.values('publisher_id', 'publisher_name', 'display_text', 'offer_type_name','offerid','change_time').filter(publisher_id__in=isExists)
        ds_total_count=ds_total.count()
        ds=ds_total.filter(Q(change_time__gt=starttime)&Q(change_time__lt=endtime)).order_by('-change_time')

        for item in ds:
            arr=[item['publisher_id'], item['publisher_name'], item['display_text'], item['offer_type_name'], item['offerid'],ds_total_count, item['change_time']]
            show.body.append(arr)
        return show

    @classmethod
    def all_publisher(cls):
        show=display()
        for col in publisher._meta.get_fields():
            show.header.append(col.column)
        for r in ['id','version','changed_time']:
            show.header.remove(r)
        for child in publisher.objects.values():
            obj=[]
            for t in show.header:
                obj.append(child[t])
            show.body.append(obj)
        return show
    
    @classmethod
    def blocked_due_to_nompnid_or_nooffer(cls):
        obj_publisher=SqlUtils.all_publisher()
        sql='''select * from (select ax.ID,ax.DisplayName,ax.PublisherID,ax.CreateTime,ax.PublicPublisherid,ax.MPNID from 
(select ID,DisplayName,PublisherID,CreateTime,PublicPublisherid,MPNID from ISVs)ax right join (
select max(ID) ID,PublisherID from (
select ID,a.PublisherID,CreateTime,MPNID,isvid from
(select ID,DisplayName,PublisherID,CreateTime,PublicPublisherid,MPNID from isvs) a left join OnBoardOffers b on a.id=b.isvid) ax
 where isvid is null and publisherid!='AzureChinaMarketplace' and datediff(dd, CreateTime, getdate())>60 group by publisherid) bx on ax.ID=bx.id and ax.PublisherId=bx.PublisherId
 and ax.publisherid in ('{list_publisher}')) axx where axx.id is not null
 '''.format(list_publisher="','".join(obj_publisher['publisher_id']))
        show=display()
        ds = SqlUtils.query(sql)
        if len(ds) > 0:
            for col in ds[0].cursor_description:
                show.header.append(col[0])
            show.body = ds
        return show
    
    @classmethod
    def have_mpnid_but_nooffer(cls):
        from django.db.models import Count

        ds=publisher.objects.values('publisher_id','microsoft_partner_network_id','display_text').exclude(publisher_id__in=
            offer.objects.values('publisher_id').annotate(ct=Count('publisher_id')).values('publisher_id')
        )

        show=display()
        show.header=['publisher_id','microsoft_partner_network_id','display_text']
        for item in ds:
            arr=[item['publisher_id'], item['microsoft_partner_network_id'], item['display_text']]
            show.body.append(arr)
            
        return show

    
    @classmethod
    def publish_vm_or_arm(cls):
        ds=publisher.objects.values('publisher_id','microsoft_partner_network_id', 'display_text').filter(
            publisher_id__in=offer.objects.filter(Q(offer_type_name='OfferType_VM_Type_Name') |
             Q(offer_type_name='OfferType_AzApp_Type_Name')).values('publisher_id').annotate(
                 ct=Count('publisher_id')).values('publisher_id'))
        show=display()
        show.header=['publisher_id','microsoft_partner_network_id','display_text']
        for item in ds:
            arr=[item['publisher_id'], item['microsoft_partner_network_id'], item['display_text']]
            show.body.append(arr)
        return show

    
    @classmethod
    def only_publish_cs(cls):
        ds=publisher.objects.values('publisher_id','microsoft_partner_network_id', 'display_text').filter(
            publisher_id__in=offer.objects.filter(offer_type_name='OfferType_CS_Type_Name').values('publisher_id').exclude(publisher_id__in=offer.objects.filter(offer_type_name__in=['OfferType_VM_Type_Name','OfferType_AzApp_Type_Name']).annotate(ct=Count('publisher_id')).values('publisher_id')).distinct()
        )
        show=display()
        show.header=['publisher_id','microsoft_partner_network_id','display_text']
        for item in ds:
            arr=[item['publisher_id'], item['microsoft_partner_network_id'], item['display_text']]
            show.body.append(arr)
        return show
