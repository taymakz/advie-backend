from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from site_api.api_configuration.enums import ResponseMessage
from site_api.api_configuration.response import BaseResponse
from site_account.user_addresses.models import UserAddresses
from site_account.user_addresses.serializers import AddressSerializer


class AddressListCreateUpdateDestroyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        addresses = UserAddresses.objects.filter(user=request.user)
        serializer = AddressSerializer(addresses, many=True)
        response = BaseResponse(
            data=serializer.data,
            status=status.HTTP_200_OK,
            message=ResponseMessage.SUCCESS.value,
        )
        return response

    def post(self, request):
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():

            serializer.save(user=request.user)


            response = BaseResponse(
                data=serializer.data,
                status=status.HTTP_201_CREATED,
                message=ResponseMessage.USER_PANEL_ADDRESS_ADDED_SUCCESSFULLY.value,

            )
            return response

        response = BaseResponse(
            data=None,
            status=status.HTTP_400_BAD_REQUEST,
            message=serializer.errors,
        )
        return response

    def put(self, request):
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            address = UserAddresses.objects.filter(id=request.data.get('id'), user=request.user).first()
            if not address:
                response = BaseResponse(
                    data=None,
                    status=status.HTTP_404_NOT_FOUND,
                    message=ResponseMessage.USER_PANEL_ADDRESS_NOT_FOUND.value,
                )
                return response
            serializer.update(address, serializer.validated_data)

            response = BaseResponse(
                data=None,
                status=status.HTTP_204_NO_CONTENT,
                message=ResponseMessage.USER_PANEL_ADDRESS_EDITED_SUCCESSFULLY.value
            )
            return response

        response = BaseResponse(
            data=None,
            status=status.HTTP_400_BAD_REQUEST,
            message=serializer.errors,
        )
        return response

    def delete(self, request):
        item_id = request.data.get('id')

        try:
            order_detail = UserAddresses.objects.get(id=item_id, user=self.request.user)
            order_detail.delete()

            response = BaseResponse(data=None, status=status.HTTP_200_OK,
                                    message=ResponseMessage.USER_PANEL_ADDRESS_REMOVED_SUCCESSFULLY.value,
                                    )

            return response
        except:
            response = BaseResponse(data=None, status=status.HTTP_404_NOT_FOUND,
                                    message=ResponseMessage.USER_PANEL_ADDRESS_NOT_FOUND.value,
                                    )
            return response


class GetAddressByIdView(RetrieveAPIView):
    queryset = UserAddresses.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        address = self.get_object()
        if address.user != request.user:
            response = BaseResponse(
                data=None,
                status=status.HTTP_403_FORBIDDEN,
                message=ResponseMessage.ACCESS_DENIED.value,
            )
            return response
        serializer = self.get_serializer(address)
        response = BaseResponse(
            data=serializer.data,
            status=status.HTTP_200_OK,
            message=ResponseMessage.SUCCESS.value,
        )
        return response
