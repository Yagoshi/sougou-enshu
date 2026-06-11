from django.shortcuts import render

def login(request):
    return render(request, 'accounts/login.html')

def registerUser(request):
    return render(request, 'accounts/registerUser.html')

def registerUserConfirm(request):
    return render(request, 'accounts/registerUserConfirm.html')

def registerUserCommit(request):
    return render(request, 'accounts/registerUserCommit.html')

def userInfo(request):
    return render(request, 'accounts/userInfo.html')

def updateUser(request):
    return render(request, 'accounts/updateUser.html')

def updateUserConfirm(request):
    return render(request, 'accounts/updateUserConfirm.html')

def updateUserCommit(request):
    return render(request, 'accounts/updateUserCommit.html')

def withdrawConfirm(request):
    return render(request, 'accounts/withdrawConfirm.html')

def withdrawCommit(request):
    return render(request, 'accounts/withdrawCommit.html')