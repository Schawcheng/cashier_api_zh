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

import logging


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
            logging.basicConfig(level=logging.DEBUG,  # 控制台打印的日志级别
                                filename='/Users/misaka/Desktop/workspace_fn/cashier_api/cashier_api.log',
                                filemode='a',  ##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
                                # a是追加模式，默认如果不写的话，就是追加模式
                                format=
                                '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
                                # 日志格式
                                )

            trade_no = request.data.get('trade_no')
            product_id = request.data.get('product_id')
            app_id = request.data.get('app_id')
            out_trade_no = request.data.get('out_trade_no')
            trade_status = request.data.get('trade_status')
            amount = request.data.get('amount')
            real_amount = request.data.get('real_amount')
            complete_time = request.data.get('complete_time')
            desc = request.data.get('desc')
            time_ = request.data.get('time')
            sign = request.data.get('sign')

            data = {
                'trade_no': trade_no,
                'product_id': product_id,
                'app_id': app_id,
                'out_trade_no': out_trade_no,
                'trade_status': trade_status,
                'amount': amount,
                'real_amount': real_amount,
                'complete_time': complete_time,
                'desc': desc,
                'time': time_
            }

            sign_will_payload = tools.generate_query_string(data)
            sign_will = f'{sign_will_payload}&key={mall.KEY}'

            signature = tools.md5(sign_will)

            logging.debug(f'{sign}=={signature}')
            logging.debug(f'trade_status={trade_status}')

            if signature == sign:
                order = OrderModel.objects.get(order_no=out_trade_no)
                order.status = trade_status
                order.order_no = trade_no
                order.save(update_fields=['trade_no', 'status'])

                return Response('success')
        except Exception as e:
            print(e)

        return Response('failed')
