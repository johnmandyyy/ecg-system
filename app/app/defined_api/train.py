from app.defined_api.gru_algorithm import GatedRecurrentUnit
from rest_framework.views import APIView
from rest_framework.response import Response


class Training(APIView):

    def __init__(self):
        self.GRU = GatedRecurrentUnit()

    def get(self, request):
        self.GRU.algorithm()
        self.GRU.test_predict()

        return Response({
            "message": "Training of dataset was done."
        }, 200)
        
