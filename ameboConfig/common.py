from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
import os, json

def error_handler(e):
    msg = ''
    if hasattr(e, 'detail'):
        if isinstance(e.detail, dict):
            for q in e.detail.items():
                msg += f"{q[0]}: {q[1][0]} "
                break
        elif isinstance(e.detail, list):
            for q in e.detail:
                msg += f"{q} "
                break
        else:
            msg = str(e.detail)
    elif hasattr(e, 'message'):
        if isinstance(e.message, dict):
            for q in e.message.items():
                msg += f"{q[0]}: {q[1][0]} "
                break
        elif isinstance(e.message, list):
            for q in e.message:
                msg += f"{q} "
                break
        elif isinstance(e.message, str):
            msg = e.message
        else:
            msg = str(e)
    else:
        msg = str(e)
    return msg

class ResponseInfo(object):
    def __init__(self, user=None, **args):
        self.response = {
            "status": args.get('status', 'success'),
            "data": args.get('data', []),
            "message": args.get('message', 'success')
        }
        self.status_code = status.HTTP_200_OK

class ResponseModelViewSet(ModelViewSet):
    """A custom viewset for every response sent by the server"""
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        self.status_code = ResponseInfo().status_code
        super().__init__(**kwargs)

    def list(self, request, *args, **kwargs):
        # for get request
        try:
            response_data = super().list(request, *args, **kwargs)
            self.response_format["data"] = response_data.data
            self.response_format["status"] = 'success'
            self.status_code = response_data.status_code
            if not response_data.data:
                self.response_format["message"] = "List empty"
            
        except Exception as e:
            self.response_format['status'] = 'failed'
            self.response_format['message'] = error_handler(e)
            self.status_code = status.HTTP_400_BAD_REQUEST
        return Response(self.response_format, status=self.status_code)

    def create(self, request, *args, **kwargs):
        # for post request
        try:
            response_data = super().create(request, *args, **kwargs)
            self.response_format["data"] = response_data.data
            self.response_format["status"] = 'success'
            self.status_code = response_data.status_code
        except Exception as e:
            self.response_format["status"] = 'failed'
            self.response_format['message'] = error_handler(e)
            self.status_code = status.HTTP_400_BAD_REQUEST
        return Response(self.response_format, status=self.status_code)

    def retrieve(self, request, *args, **kwargs):
        # for get request (by id)
        try:
            response_data = super().retrieve(request, *args, **kwargs)
            self.response_format["data"] = response_data.data
            self.response_format["status"] = 'success'
            self.status_code = response_data.status_code
            if not response_data.data:
                self.response_format["message"] = "Empty"
        except Exception as e:
            self.response_format['status'] = 'failed'
            self.response_format['message'] = error_handler(e)
            self.status_code = status.HTTP_400_BAD_REQUEST
        return Response(self.response_format, status=self.status_code)

    def update(self, request, *args, **kwargs):
        # for patch request
        try:
            kwargs['partial'] = True    # signifies it is a patch request, only update the necessary field(s)
            response_data = super().update(request, *args, **kwargs)
            self.response_format["data"] = response_data.data
            self.response_format["status"] = 'success'
            self.status_code = response_data.status_code
        except Exception as e:
            self.response_format['status'] = 'failed'
            self.response_format['message'] = error_handler(e)
            self.status_code = status.HTTP_400_BAD_REQUEST
        return Response(self.response_format, status=self.status_code)

    def destroy(self, request, *args, **kwargs):
        # for delete request
        try:
            obj = vars(self.get_object())
            obj.pop('_state', None)
            obj.pop('password', None)
            obj.pop('is_staff', None)
            obj.pop('is_superuser', None)
            response_data = super().destroy(request, *args, **kwargs)
            self.response_format["data"] = obj
            self.response_format["status"] = 'success'
            self.status_code = response_data.status_code
        except Exception as e:
            msg = error_handler(e)
            self.response_format['message'] = msg
            self.response_format['status'] = 'failed'
            self.status_code = status.HTTP_400_BAD_REQUEST
        return Response(self.response_format, status=self.status_code)

class CustomResponse():
    """A custom view for every response sent by the server"""
    @staticmethod
    def success(data=None, message=None):
        response_data = {
            "status": "success",
            "data": data or [],
            "message": message or ""
        }
        return Response(response_data, status=status.HTTP_200_OK)

    @staticmethod
    def failed(data=None, message=None):
        response_data = {
            "status": "failed",
            "data": data or [],
            "message": message or ""
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


def CustomValidationError(err):
    """Returns the error message only"""
    error = list(err.messages)[0]
    error = error.replace("non_field_errors:", "").strip()
    return error

