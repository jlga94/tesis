from django.shortcuts import render
from django.views.decorators.http import require_http_methods

# Create your views here.
def init(request):

	return render(request,'especialidades/especialidades.html')