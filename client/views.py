import time
import traceback
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from backstage.models import ChannelModel, OrderModel
from client.serializers import ChannelSerializer
import tools
from config import mall


class ChannelDetail(APIView):
    def get(self, request, cid):
        try:
            channel = ChannelModel.objects.get(cid=cid, is_del=False, is_valid=True)
            serializer = ChannelSerializer(channel)
            return Response(tools.api_response(200, 'ok', serializer.data))
        except ChannelModel.DoesNotExist:
            return Response(tools.api_response(401, '此支付通道无效，请切换后再试'))


class Pay(APIView):
    def post(self, request):
        app_id = mall.APP_ID
        product_id = request.data.get('cid')
        out_trade_no = tools.generate_unique_order_number()
        notify_url = mall.NOTIFY_URL
        amount = request.data.get('money')
        t_time = int(time.time())
        desc = request.data.get('remark')
        key = mall.KEY
        pay_target = mall.PAY_TARGET

        try:
            channel = ChannelModel.objects.get(cid=product_id, is_del=False, is_valid=True)
        except ChannelModel.DoesNotExist:
            traceback.print_exc()
            return Response(tools.api_response(404, '支付通道无效'))

        data = {
            'app_id': app_id,
            'product_id': product_id,
            'out_trade_no': out_trade_no,
            'notify_url': notify_url,
            'amount': amount,
            'time': t_time,
            # 'desc': desc
        }

        sign_will_payload = tools.generate_query_string(data)

        sign_will = f'{sign_will_payload}&key={key}'

        signature = tools.md5(sign_will)

        payload = f'{sign_will_payload}&sign={signature}'

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            response = requests.post(url=pay_target, data=payload, headers=headers)

            import logging

            logging.basicConfig(level=logging.DEBUG,  # 控制台打印的日志级别
                                filename='/Users/misaka/Desktop/workspace_fn/cashier_api/cashier_api.log',
                                filemode='a',  ##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
                                # a是追加模式，默认如果不写的话，就是追加模式
                                format=
                                '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
                                # 日志格式
                                )

            if response.status_code == 200 and response.json()['code'] == 200:
                if response.json()['code'] == 200:
                    order = OrderModel(
                        order_no=out_trade_no,
                        status=5,
                        channel_id=channel.cid,
                        tid='-1',
                        amount=amount,
                        remark=desc
                    )
                    order.save()

                    pay_url = response.json()['data']['url']

                    return Response(tools.api_response(201,'订单创建成功, 支付请求已发出',{'pay_url': pay_url}))
                else:
                    return Response(tools.api_response(401, response.json()['message']))

            else:
                logging.debug(response.text)
                return Response(tools.api_response(500, '支付失败，请稍后再试'))
        except Exception as e:
            traceback.print_exc(e)
            return Response(tools.api_response(401, '支付请求发送失败，请检查支付参数'))
