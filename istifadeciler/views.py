from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.http import HttpResponse








def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Giriş uğurlu olduqda mesajı göstəririk
            messages.success(request, 'Uğurla giriş olundu. 3 saniyə sonra əsas səhifəyə yönləndiriləcəksiniz.')
            # 3 saniyə sonra əsas səhifəyə yönləndirmək üçün
            return redirect('main')
        else:
            messages.error(request, 'İstifadəçi adı və ya şifrə yanlışdır.')

    return render(request, 'login.html')
