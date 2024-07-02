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
        mid = mall.MID
        mer_order_t_id = tools.generate_unique_order_number()
        money = request.data.get('money')
        channel_id = request.data.get('cid')
        remark = request.data.get('remark')
        notify_url = mall.NOTIFY_URL
        key = mall.KEY
        pay_target = mall.PAY_TARGET

        try:
            channel = ChannelModel.objects.get(cid=channel_id, is_del=False, is_valid=True)
        except ChannelModel.DoesNotExist:
            return Response(tools.api_response(404, '支付通道无效'))

        data = {
            'mid': mid,
            'merOrderTid': mer_order_t_id,
            'money': money,
            'channelCode': channel.channel_code,
            'notifyUrl': notify_url
        }

        sign_will_payload = tools.generate_query_string(data)
        sign_will = f'{sign_will_payload}&{key}'

        signature = tools.md5(sign_will)

        payload = f'{sign_will_payload}&sign={signature}'

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            response = requests.post(url=pay_target, data=payload, headers=headers)

            import logging

            logging.basicConfig(level=logging.DEBUG,#控制台打印的日志级别
                    filename='/opt/workspace/cashier_api_uwsgi/cashier_api.log',
                    filemode='a',##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
                    #a是追加模式，默认如果不写的话，就是追加模式
                    format=
                    '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
                    #日志格式
                    )
            logging.debug(response.text)

            if response.status_code == 200 and response.json()['status'] == 0:
                pay_result = response.json()['result']
                pay_status = pay_result['payOrderStatus']
                order = OrderModel(
                    order_no=mer_order_t_id,
                    status=5,
                    channel_id=channel.cid,
                    tid=pay_result['tid'],
                    amount=money,
                    remark=remark
                )
                order.save()

                pay_url = pay_result['payUrl']

                return Response(tools.api_response(
                    201,
                    '订单创建成功, 支付请求已发出',
                    {'pay_url': pay_url})
                )
        except Exception as e:
            print(e)

        return Response(tools.api_response(401, '支付请求发送失败，请检查支付参数'))
