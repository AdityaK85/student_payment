import datetime
import json
import traceback
from django.contrib import messages
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from Project_utilty.phonepe import Payment_Request, checkPhonePayStatus
from Project_utilty.send_emails import send_html_email
from course.models import Fee
from .models import *
from enrollment.models import *
from payment.models import *
from . import forms
import threading
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.http import JsonResponse

def index(request):
    students = Student.objects.all()
    return render(request, 'student/index.html', {'students': students})

def student_login(request):
    return render(request, 'student_panel/stu_login.html')

@csrf_exempt
def login_handler(request):
    email = request.POST.get("email")
    password = request.POST.get("password")
    if Student.objects.filter(email=email).exists():
        user = Student.objects.filter(email=email).last()
        if user.password == password:
            request.session['Stu_userId'] = user.id
            request.session['Stu_name'] = user.name
            request.session['user_type'] = "Student"
            return JsonResponse({"status": 1, "msg": "Login Successfull.", 'user_id': user.id})
        else:
            return JsonResponse({"status": 0, "msg": "Invalid Credentials"})
    else:
        return JsonResponse({"status": 0, "msg": "Email id is not register."})

def student_index(request):
    user_id = request.session.get('Stu_userId')
    if user_id:
        students = Student.objects.filter(id = user_id).last()
        enrolls = Enroll.objects.filter(student_id = user_id).order_by('-id')
        payments = Payment.objects.filter(enroll_id__student_id = user_id )
        return render(request, 'student_panel/stu_index.html', {'students': students, 'enrolls' : enrolls , 'payments' : payments })
    return redirect('/student/student_login')

def create(request):
    form = forms.CreateStudentForm()
    return render(request, 'student/create.html', {'form': form})

def send_student_id_mail(username , email , password ):
    subject = "Regsitered Successfully"
    context = { "username" : username, "email":email,"password":password}
    html_str = render_to_string('mail.html',context)
    to_email = email
    send_html_email(subject, html_str, to_email)

def store(request):
    if request.method == 'POST':
        form = forms.CreateStudentForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            name = form.cleaned_data.get('name')
            student = form.save()
            password = student.password
            threading.Thread(target=send_student_id_mail, args=(name, email, password,)).start()
            messages.success(request, 'Student created successfully')
            return redirect('student.index')
        else:
            return render(request, 'student/create.html', {'form': form})
    else:
        return redirect('student.create')


def edit(request, sid):
    try:
        student = Student.objects.get(id=sid)
        form = forms.CreateStudentForm(instance=student)
        return render(request, 'student/edit.html', {'form': form})
    except Student.DoesNotExist:
        return redirect('student.index')


def update(request, sid):
    if request.method == 'POST':
        try:
            student = Student.objects.get(id=sid)
            form = forms.CreateStudentForm(request.POST, instance=student)
            if form.is_valid():
                form.save()
                messages.success(request, 'Student updated successfully')
                return redirect('student.index')
            else:
                return render(request, 'student/edit.html', {'form': form})
        except Student.DoesNotExist:
            return redirect('student.index')
    else:
        return redirect('student.index')


def delete(request, sid):
    if request.method == 'POST':
        try:
            student = Student.objects.get(id=sid)
            student.delete()
            messages.success(request, 'Student deleted successfully')
            return redirect('student.index')
        except Student.DoesNotExist:
            return redirect('student.index')
    else:
        return redirect('student.index')


def invoice(request, pid):
    try:
        current = Payment.objects.get(id=pid)
        fees = Fee.objects.filter(course_id=current.enroll_id.course_id)
        history = Payment.objects.filter(enroll_id=current.enroll_id, id__lte=current.id)
        return render(request, 'payment/invoicebody.html', {'pay_current': current, 'pay_history': history, 'fees': fees})
    except Payment.DoesNotExist:
        messages.error(request, 'Payment does not exist')
        return redirect('student.index')



@csrf_exempt
def make_payment_aj(request):
    data = request.POST.dict()
    enroll_id = request.POST.get('enroll_id')
    amount = request.POST.get('amount')
    remarks = request.POST.get('remark')
    print("---------", enroll_id , amount , remarks)

    transaction_id = f"TRANSID{random.randint(1000000000000, 9999999999000)}"
    merchantuser_id = f"USERID{random.randint(1000000000000, 9999999999000)}"

    
    redirect_url = f"{request.build_absolute_uri().rsplit('/', 2)[0]}/phonepe_payment_redirect/"    # redirect url 
    callback_url = f"{request.build_absolute_uri().rsplit('/', 2)[0]}/phonepe_callback_redirect/"  # callback url 
    amount = round((float(amount)))
    
    amount = amount * 100
    phonepe_redirecturl = ""
    response = Payment_Request(amount,transaction_id,merchantuser_id,redirect_url,callback_url) # call phone pe payment function
    print("::::response ::::", response)
    if response[0] == False:
        return JsonResponse({'stutus':0,"msg":response[1]})
    else:
        response = json.loads(response[1])

        request.session['transaction_id'] = transaction_id   # set transaction id on session
        request.session['isPaymentInitiated'] = 'Yes'   # set transaction id on session    
        
        
        phonepe_redirecturl = response['data']["instrumentResponse"]["redirectInfo"]["url"]
        phone_payment_status = "PAYMENT_PENDING"
    amount = amount / 100
    Payment.objects.create(enroll_id_id = enroll_id , amount = amount , remarks = remarks , payment_intiated = 'Student' , payment_status = 'PENDING' , transaction_id = transaction_id)
    return JsonResponse({'status':1,"msg":"Success","phonepe_redirecturl":phonepe_redirecturl})


@csrf_exempt
def remove_payment_session(request):
    data = {}
    transaction_id = None
    try:
        transaction_id = request.session.get("transaction_id")
        isPaymentInitiated = request.session.get("isPaymentInitiated")

        del request.session['transaction_id']
        del request.session['isPaymentInitiated']
    except:
        traceback.print_exc()

    
    next_time = (datetime.datetime.now()+ datetime.timedelta(minutes=1)).time()

    while datetime.datetime.now().time() < next_time:
        func_status,response = checkPhonePayStatus(transaction_id)
        print("***********",func_status,response)
        if func_status == True:
            
            
            if response['code'] == "PAYMENT_SUCCESS":
                providerReferenceId = response['data']['transactionId']
                payment_status = response['code']
                transaction_id = response['data']['merchantTransactionId']
                Payment.objects.filter(transaction_id = transaction_id).update(payment_status = 'SUCCESS')
                
                data = {'status':"1","msg":"Your payment was successful! Thank you for your payment"}
                break
            elif response['code'] == "PAYMENT_PENDING":
                # print("payment status---:",response['code'])
                Payment.objects.filter(transaction_id = transaction_id).delete()
                data = {"status":"2","msg":"Your payment is currently being processed. You will receive a notification via email once the payment is complete."}

            elif response['code'] == "PAYMENT_ERROR":
                Payment.objects.filter(transaction_id = transaction_id).delete()
                # print("payment status---:",response['code'])
                data = {'status':"0","msg":"Unfortunately, your payment could not be processed,Please check your payment information and try again."}
                break

            elif response['code'] == "INTERNAL_SERVER_ERROR":
                Payment.objects.filter(transaction_id = transaction_id).delete()
                print("payment status---:",response['code'])

            else:
                Payment.objects.filter(transaction_id = transaction_id).delete()
                print("-----------------------------",response['code'])
                data = {'status':"0","msg":"Something went wrong."}
                break
        else:
            # msg = response['message']
            Payment.objects.filter(transaction_id = transaction_id).delete()
            data = {'status':"0","msg":"Something went wrong."}
            break
        
        datetime.time.sleep(0.6)
    
    return JsonResponse(data)


@csrf_exempt
def phonepe_payment_redirect(request):
    response = request.POST.dict()
    providerReferenceId = response['providerReferenceId']
    payment_status = response['code']
    transaction_id = response['transactionId']
    checksum = response['checksum']
    get_usr = Payment.objects.filter(transaction_id = transaction_id).last()
    return redirect('/student/student-index/')


@csrf_exempt
def phonepe_callback_redirect(request):
    
    return redirect('/')