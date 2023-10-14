from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
# from vestige.models import DistributionPoint, UserCoin as vCoin
from django.db import transaction
import pandas as pd
import random
from ecomApp.models import UserCoin as eCoin, coinHistory as ecHistory, Order as eOrder, User, CoinData as ecData, MoneyGenerate as emoneyG, Activation as eActivation, ModicareUser
from proteinWorld.models import UserCoin as pCoin, coinHistory as pcHistory, Order as pOrder, CoinData as pcData, MoneyGenerate as pmoneyG, Activation as pActivation, ProteinWorldUser
from amulyaHerbal.models import UserCoin as aCoin, coinHistory as acHistory, Order as aOrder, CoinData as acData, MoneyGenerate as amoneyG, Activation as aActivation, AmulyaHerbalUser
from hhi.models import UserCoin as hCoin, coinHistory as hcHistory, Order as hOrder, CoinData as hcData, MoneyGenerate as hmoneyG, Activation as hActivation, HHIUser
from vestige.models import UserCoin as vCoin, coinHistory as vcHistory, Order as vOrder, DistributionPoint, CoinData as vcData, MoneyGenerate as vmoneyG, Activation as vActivation, VestigeUser
from teamsbuilders.models import UserReferral

def create_new_ref_number():
    return str(random.randint(10000000, 99999999))

def InsertBatchDPCSV(request):
    df = pd.read_csv('teamsbuilders/media/vestige_dp.csv')
    dpLists = []
    mob = "",
    alt = "",
    for _ in range(len(df)):       
        try:
            print(_)
            if(len(str(df.iloc[_][2]))==20):
                mob = str(df.iloc[_][2])[:10]
                alt = str(df.iloc[_][2][10:])
            else:
                mob = df.iloc[_][2]
            dp = DistributionPoint.objects.filter(mob=df.iloc[_][2])
            if(len(dp) == 0):
                try:
                    print(df.iloc[_][0])
                    DistributionPoint.objects.create(
                        dpID = create_new_ref_number(),
                        dpName = df.iloc[_][0],
                        dpAddress = df.iloc[_][1],
                        cityName = df.iloc[_][4],
                        pincode = str(int(df.iloc[_][6])),
                        state = df.iloc[_][7],
                        mob = mob,
                        alternative_mob = df.iloc[_][3] or alt,
                        dp_branch_type = df.iloc[_][8]
                    )
                except Exception as e:
                    print(e)
                    print(_)
        except Exception as e:
            print(e)
            break
    return HttpResponse("Successfully added")

def ClearUserCoins(request):
    eCoin.objects.all().update(coin=0)
    vCoin.objects.all().update(coin=0)
    pCoin.objects.all().update(coin=0)
    hCoin.objects.all().update(coin=0)
    aCoin.objects.all().update(coin=0)
    return HttpResponse("Successfully cleared")

class BatchUpdate(APIView):
    def get(self, request, *args, **kwargs):
        user_modicare = ProteinWorldUser.objects.filter(mob=None)[:10]
        print(user_modicare)
        for count, m_user in enumerate(user_modicare):
            ProteinWorldUser.objects.filter(user=m_user.user).update(
                mob=m_user.user.mob, 
                email=m_user.user.email,
                first_name=m_user.user.first_name, 
                last_name=m_user.user.last_name,
                profile_picture = m_user.user.profile_picture
            )
            print(m_user.user.mob, m_user.user.first_name, m_user.user.last_name)
            print(count)
        return Response({"status":"ok"})
class DeleteUser(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    def delete(self, request, user_id):
        app_name = request.GET.get('appname')
        if app_name == "modicare":
            return Response(self.modicare(user_id))
        elif app_name == "Vestige":
            return Response(self.vestige(user_id))
        elif app_name == "hhi":
            return Response(self.hhi(user_id))
        elif app_name == "proteinWorld":
            return Response(self.protein_world(user_id))
        elif app_name == "amulyaHerbal":
            return Response(self.amulya_herbal(user_id))
        elif app_name == "all_app":
            return Response(
                        {
                            "status": "ok", 
                            "modicare": self.modicare(user_id),
                            "vestige": self.vestige(user_id),
                            "hhi": self.hhi(user_id),
                            "proteinWorld": self.protein_world(user_id),
                            "amulyaHerbal": self.amulya_herbal(user_id),
                            "user_status":self.teamsbuilders(user_id)
                        }, status=status.HTTP_200_OK
                    )
    def extracted_delete_user(self, user_id, coin, coin_history, order, coin_data, money_generate=None, activation=None, app_user=None):
        try:
            if(app_user.objects.filter(user=user_id).exists() == False):
                return {"status":"ok","message": "account doesn't exist!"}
            coin.objects.filter(user=user_id).delete()
            coin_history.objects.filter(user=user_id).delete()
            order.objects.filter(user=user_id).delete()
            coin_data.objects.filter(user=user_id).delete()
            if money_generate is not None:
                money_generate.objects.filter(user=user_id).delete()
            if activation is not None:
                activation.objects.filter(user=user_id).delete()
            app_user.objects.filter(user=user_id).delete()
            return {"status":"ok","message": "account deletion complete"}
        except Exception as e:
            return {"status":"failed", "message":f"{e}"}

    def modicare(self, user_id):
       return self.extracted_delete_user(user_id, eCoin, ecHistory, eOrder, ecData, emoneyG, eActivation, ModicareUser)

    def vestige(self, user_id):
        return self.extracted_delete_user(user_id, vCoin, vcHistory, vOrder, vcData, vmoneyG, vActivation, VestigeUser)

    def hhi(self, user_id):
        return self.extracted_delete_user(user_id, hCoin, hcHistory, hOrder, hcData, hmoneyG, hActivation, HHIUser)

    def protein_world(self, user_id):
        return self.extracted_delete_user(user_id, pCoin, pcHistory, pOrder, pcData, pmoneyG, pActivation, ProteinWorldUser)

    def amulya_herbal(self, user_id):
        return self.extracted_delete_user(user_id, aCoin, acHistory, aOrder, acData, amoneyG, aActivation, AmulyaHerbalUser)
    
    def teamsbuilders(self, user_id):
        try:
            with transaction.atomic():
                UserReferral.objects.filter(user=user_id).delete()
                User.objects.filter(id=user_id).delete()
                return {"message": "User Deleted successdully"}
        except Exception as e:
            return {"error": f"{e}"}



