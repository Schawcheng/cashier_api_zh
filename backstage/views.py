from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings

from backstage.models import ChannelModel, BackstageUserModel, OrderModel
from backstage.serializers import ChannelSerializer, ChannelCreateSerializer, OrderSerializer

from backstage.CustomTokenAuthentication import TokenAuthentication

import tools

from config import mall
import config.common


class Login(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        captcha_code = request.data.get('captcha_code')

        # TODO: 验证图形验证码

        user = BackstageUserModel.objects.filter(username=username, password=tools.md5(password)).first()
        if not user:
            return Response(tools.api_response(404, '用户不存在或密码错误'))

        token = tools.generate_jwt(user.uid, user.username, settings.SECRET_KEY)

        return Response(tools.api_response(200, '登录成功', {'token': token}))


class Channel(APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        channels = ChannelModel.objects.filter(is_del=False)
        count = channels.count()

        current = request.GET.get('current')
        page_size = request.GET.get('page_size')

        start_index, end_index = tools.get_pagination(current, page_size)
        channels = channels[start_index:end_index]

        serializer = ChannelSerializer(channels, many=True)

        # return Response({'code': 200, 'total': 0, 'data': serializer.data})
        return Response(tools.api_response(200, 'ok', serializer.data, count))

    def post(self, request):
        serializer = ChannelCreateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(tools.api_response(201, 'created', serializer.data))
        return Response(tools.api_response(401, 'bad request', {}))


class ChannelDtail(APIView):
    authentication_classes = [TokenAuthentication]

    def delete(self, request, cid):
        try:
            channel = ChannelModel.objects.get(cid=cid)
            channel.is_del = True
            channel.save()
        except ChannelModel.DoesNotExist:
            return Response(tools.api_response(404, '通道不存在'))
        except Exception:
            return Response(tools.api_response(500, '操作失败，请检查参数后重试'))

        return Response(tools.api_response(200, '删除成功'))

    def put(self, request, cid):
        try:
            status = request.GET.get('status')
            channel = ChannelModel.objects.get(cid=cid)
            channel.is_valid = True if int(status) == 1 else False
            channel.save()
        except ChannelModel.DoesNotExist:
            return Response(tools.api_response(404, '通道不存在'))
        except Exception:
            return Response(tools.api_response(500, '操作失败，请检查参数后重试'))

        return Response(tools.api_response(200, '状态修改成功'))


class ChannelPayUrl(APIView):
    authentication_classes = [TokenAuthentication]

    def put(self, request, cid):
        try:
            channel = ChannelModel.objects.get(cid=cid, is_del=False, is_valid=True)
            channel.pay_url = tools.generate_pay_url(cid)
            channel.save()
        except ChannelModel.DoesNotExist:
            return Response(tools.api_response(404, '无效的支付通道'))
        except Exception:
            return Response(tools.api_response(500, '支付链接生成失败', {}))

        return Response(tools.api_response(200, '支付链接生成成功', {}))


class ChannelQRCode(APIView):
    authentication_classes = [TokenAuthentication]

    def put(self, request, cid):
        try:
            channel = ChannelModel.objects.get(cid=cid)
            filename = tools.generate_qrcode(cid)
            file_url = f"{config.common.QRCODE_URL_ROOT}/{filename}"
            channel.qrcode = file_url
            channel.save()
        except ChannelModel.DoesNotExist:
            return Response(tools.api_response(404, '无效的支付通道'))
        except Exception as e:
            return Response(tools.api_response(500, '生成收款码失败'))

        return Response(tools.api_response(200, '生成收款码成功'))


class Orders(APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        current = request.GET.get('current')
        page_size = request.GET.get('page_size')

        orders = OrderModel.objects.all()
        count = orders.count()

        start_index, end_index = tools.get_pagination(current, page_size)

        orders = orders[start_index:end_index]

        serializer = OrderSerializer(orders, many=True)

        return Response(tools.api_response(200, 'ok', serializer.data, count))


class Notify(APIView):
    def post(self, request):
        try:
            mer_order_t_id = request.data.get('merOrderTid')
            tid = request.data
            money = request.data.get('money')
            status = request.data.get('status')
            sign = request.data.get('sign')

            data = {
                'merOrderTid': mer_order_t_id,
                'tid': tid,
                'money': money,
                'status': status
            }

            sign_will_payload = tools.generate_query_string(data)
            sign_will = f'{sign_will_payload}&{mall.KEY}'

            signature = tools.md5(sign_will)

            if signature == sign:
                order = OrderModel.objects.get(order_no=mer_order_t_id)
                order.status = status
                order.save()

                return Response('success')
        except Exception as e:
            print(e)

        return Response('failed')
