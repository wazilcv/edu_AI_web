import datetime
import random
import smtplib

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import Group
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache

from myapp.classify_review import classify_with_vader
from myapp.classify_review_genai import run_analysis
from myapp.q_a_generator import generate_qa_from_text
from .models import *

# Create your views here.
static_path=r"C:\Users\LENOVO\PycharmProjects\edu_ai\myapp\static\\"

#   admin details
#   username : admin@gmail.com
#   password : siva@9119


def logoutt(request):
    logout(request)
    return redirect("/")

def log(request):
    return render(request, "login.html")

def log_post(request):
    un=request.POST['username']
    ps=request.POST['password']
    data=authenticate(request, username=un, password=ps)
    if data:
        login(request, data)
        if data.is_superuser:
            return HttpResponse("<script>alert('Welcome admin');window.location='/adm_home';</script>")
        else:
            request.session['fid']=faculty.objects.get(LOGIN_id=request.user.id).id
            return HttpResponse("<script>alert('Welcome faculty');window.location='/fac_home';</script>")
    else:
        return HttpResponse("<script>alert('Invalid details');window.location='/';</script>")


@login_required
@never_cache
def adm_home(request):
    return render(request, "admin/index.html")


@login_required
@never_cache
def adm_add_course(request):
    return render(request, "admin/add_course.html")

def adm_add_course_post(request):
    cname=request.POST['name']
    duration=request.POST['duration']
    if course.objects.filter(course_name=cname).exists():
        return HttpResponse("<script>alert('Course Exist');window.location='/adm_add_course';</script>")
    obj=course()
    obj.course_name=cname
    obj.duration=duration
    obj.save()
    return HttpResponse("<script>alert('Course Added');window.location='/adm_view_course';</script>")


@login_required
@never_cache
def adm_edit_course(request, id):
    data=course.objects.get(id=id)
    return render(request, "admin/edit_course.html", {"data":data})

def adm_edit_course_post(request, id):

    cname=request.POST['name']
    duration=request.POST['duration']
    if course.objects.filter(course_name = cname,duration = duration).exists():
        return HttpResponse("<script>alert('Course Exist');window.location='/adm_add_course';</script>")
    course.objects.filter(id=id).update(course_name = cname,duration = duration)

    return HttpResponse("<script>alert('Course updated');window.location='/adm_view_course';</script>")


@login_required
@never_cache
def adm_view_course(request):
    data=course.objects.all()
    return render(request, "admin/view_course.html", {"data":data})


@login_required
@never_cache
def adm_delete_course(request, id):
    course.objects.filter(id=id).delete()
    return HttpResponse("<script>alert('Course deleted');window.location='/adm_view_course';</script>")


@login_required
@never_cache
def adm_add_faculty(request):
    return render(request, "admin/add_faculty.html")

def adm_add_faculty_post(request):
    fname=request.POST['fname']
    gender=request.POST['gender']
    dob=request.POST['dob']
    email=request.POST['email']
    phone=request.POST['phone']
    place=request.POST['place']
    city=request.POST['city']
    state=request.POST['state']
    pincode=request.POST['pincode']
    experience=request.POST['experience']
    photo=request.FILES['photo']

    dt=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")+".jpg"
    fs=FileSystemStorage()
    fs.save(static_path + "images\\" + dt, photo)
    path = "/static/images/"+dt

    # random_password=random.randint(1000, 9999)
    random_password="11223344"
    if faculty.objects.filter(email=email).exists():
        return HttpResponse("<script>alert('faculty Exist');window.location='/adm_add_faculty';</script>")
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    # ✅ Gmail credentials (use App Password, not real password)
    sender_email = "service.edu.ai@gmail.com"
    print(sender_email)
    receiver_email = email  # change to actual recipient
    print(receiver_email)
    app_password = "gldb wolw ufgm ieed"  # App Password from Google
    pwd = str(random.randint(1100, 9999))
    print(pwd, "okkkk")  # Example password to send
    request.session['otp'] = pwd
    request.session['email'] = email

    # Setup SMTP
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, app_password)

    # Create the email
    msg = MIMEMultipart("alternative")
    msg["From"] = sender_email
    print(msg["From"])
    msg["To"] = receiver_email
    msg["Subject"] = "Your OTP"

    # Plain text (backup)
    # text = f"""
    # Hello,

    # Your password for Smart Donation Website is: {pwd}

    # Please keep it safe and do not share it with anyone.
    # """

    # HTML (attractive)
    html = f"""
               <html>
                 <body style="font-family: Arial, sans-serif; color: #333;">
                   <h2 style="color:#2c7be5;">Edu AI</h2>
                   <p>Hello,</p>
                   <p>Your Password is: </p>
                   <p style="padding:10px; background:#f4f4f4; 
                             border:1px solid #ddd; 
                             display:inline-block;
                             font-size:18px;
                             font-weight:bold;
                             color:#2c7be5;">
                     {pwd}
                   </p>
                   <p>Please keep it safe and do not share it with anyone.</p>
                   <hr>
                   <small style="color:gray;">This is an automated email from Edu AI System.</small>
                 </body>
               </html>
               """

    # Attach both versions
    # msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    # Send email
    server.send_message(msg)
    print("✅ Email sent successfully!")

    # Close connection
    server.quit()
    obj2=User()
    obj2.username=email
    obj2.password=make_password(str(random_password))
    obj2.save()
    obj2.groups.add(Group.objects.get(name="faculty"))

    obj = faculty()
    obj.name = fname
    obj.gender = gender
    obj.dob = dob
    obj.email = email
    obj.phone = phone
    obj.place = place
    obj.city = city
    obj.state = state
    obj.pin = pincode
    obj.experience = experience
    obj.image = path
    obj.LOGIN=obj2
    obj.save()
    return HttpResponse("<script>alert('Faculty Added');window.location='/adm_view_faculty';</script>")


@login_required
@never_cache
def adm_edit_faculty(request, id):
    data=faculty.objects.get(id=id)
    return render(request, "admin/edit_faculty.html", {"data":data})


def adm_edit_faculty_post(request, id):
    fname = request.POST['fname']
    gender = request.POST['gender']
    dob = request.POST['dob']
    email = request.POST['email']
    phone = request.POST['phone']
    place = request.POST['place']
    city = request.POST['city']
    state = request.POST['state']
    pincode = request.POST['pincode']
    experience = request.POST['experience']
    if 'photo' in request.FILES:
        photo = request.FILES['photo']
        dt = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg"
        fs = FileSystemStorage()
        fs.save(static_path + "images\\" + dt, photo)
        path = "/static/images/" + dt
        faculty.objects.filter(id=id).update(image = path)

    if faculty.objects.filter(name = fname, gender = gender, dob = dob, email = email,
        phone = phone, place = place, city = city, state= state, pin = pincode, experience = experience).exists():
        return HttpResponse("<script>alert('Faculty Exist');window.location='/adm_add_faculty';</script>")
    faculty.objects.filter(id=id).update(name = fname, gender = gender, dob = dob, email = email,
        phone = phone, place = place, city = city, state= state, pin = pincode, experience = experience)

    return HttpResponse("<script>alert('Faculty updated');window.location='/adm_view_faculty';</script>")


@login_required
@never_cache
def adm_view_faculty(request):
    data=faculty.objects.all()
    return render(request, "admin/view_faculty.html", {"data":data})


@login_required
@never_cache
def adm_delete_faculty(request, id):
    faculty.objects.filter(id=id).delete()
    return HttpResponse("<script>alert('Faculty deleted');window.location='/adm_view_faculty';</script>")


@login_required
@never_cache
def adm_allocate_subject(request, id):
    data=subject.objects.all()
    return render(request, "admin/allocate_subject.html", {"data":data, "id":id})

def adm_allocate_subject_post(request,id):
    subid=request.POST['select2']
    if sub_allocation.objects.filter(SUBJECT_id=subid, FACULTY_id=id).exists():
        return HttpResponse("<script>alert('alredy allocated');window.location='/adm_home';</script>")
    obj=sub_allocation()
    obj.SUBJECT_id=subid
    obj.FACULTY_id=id
    obj.save()
    return HttpResponse("<script>alert('Subject allocated');window.location='/adm_view_faculty';</script>")


@login_required
@never_cache
def adm_view_sub_allocation(request):
    data=sub_allocation.objects.all()
    return render(request, "admin/view_subject_allocation.html", {"data":data})


@login_required
@never_cache
def adm_delete_sub_allocation(request, id):
    sub_allocation.objects.filter(id=id).delete()
    return HttpResponse("<script>alert('Allocation deleted');window.location='/adm_view_sub_allocation';</script>")


@login_required
@never_cache
def adm_add_student(request):
    data = course.objects.all()
    return render(request, "admin/add_student.html", {"data":data})

def adm_add_student_post(request):
    name=request.POST['name']
    course=request.POST['select2']
    semester=request.POST['select']
    ad_num=request.POST['adm_num']
    gender=request.POST['gender']
    dob=request.POST['dob']
    email=request.POST['email']
    phone=request.POST['phone']
    place=request.POST['place']
    city=request.POST['city']
    state=request.POST['state']
    pincode=request.POST['pincode']
    photo=request.FILES['photo']

    dt = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg"
    fs = FileSystemStorage()
    fs.save(static_path + "images\\" + dt, photo)
    path = "/static/images/" + dt


    if User.objects.filter(username=email).exists():
        return HttpResponse("<script>alert('Student Exist');window.location='/adm_add_student';</script>")
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    # ✅ Gmail credentials (use App Password, not real password)
    sender_email = "service.edu.ai@gmail.com"
    print(sender_email)
    receiver_email = email  # change to actual recipient
    print(receiver_email)
    app_password = "gldb wolw ufgm ieed"  # App Password from Google
    pwd = str(random.randint(1100, 9999))
    print(pwd,"okkkk")# Example password to send
    request.session['otp'] = pwd
    request.session['email'] = email

    # Setup SMTP
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, app_password)

    # Create the email
    msg = MIMEMultipart("alternative")
    msg["From"] = sender_email
    print(msg["From"])
    msg["To"] = receiver_email
    msg["Subject"] = "Your OTP"

    # Plain text (backup)
    # text = f"""
    # Hello,

    # Your password for Smart Donation Website is: {pwd}

    # Please keep it safe and do not share it with anyone.
    # """

    # HTML (attractive)
    html = f"""
           <html>
             <body style="font-family: Arial, sans-serif; color: #333;">
               <h2 style="color:#2c7be5;">Edu AI</h2>
               <p>Hello,</p>
               <p>Your password is :</p>
               <p style="padding:10px; background:#f4f4f4; 
                         border:1px solid #ddd; 
                         display:inline-block;
                         font-size:18px;
                         font-weight:bold;
                         color:#2c7be5;">
                 {pwd}
               </p>
               <p>Please keep it safe and do not share it with anyone.</p>
               <hr>
               <small style="color:gray;">This is an automated email from Edu AI System.</small>
             </body>
           </html>
           """

    # Attach both versions
    # msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    # Send email
    server.send_message(msg)
    print("✅ Email sent successfully!")

    # Close connection
    server.quit()
    obj2 = User()
    obj2.username = email
    obj2.password = make_password(str(pwd))
    obj2.save()
    obj2.groups.add(Group.objects.get(name="student"))

    obj = student()
    obj.std_name = name
    obj.COURSE_id = course
    obj.semester = semester
    obj.ad_num = ad_num
    obj.gender = gender
    obj.dob = dob
    obj.email = email
    obj.phone = phone
    obj.place = place
    obj.city = city
    obj.state = state
    obj.pin = pincode
    obj.image = path
    obj.LOGIN=obj2
    obj.save()
    return HttpResponse("<script>alert('Student Added');window.location='/adm_view_student';</script>")


@login_required
@never_cache
def adm_edit_student(request , id):
    data = course.objects.all()
    data2=student.objects.get(id=id)
    return render(request, "admin/edit_student.html", {"data":data , "data2":data2})

def adm_edit_student_post(request, id):
    name=request.POST['name']
    course = request.POST['select2']
    semester = request.POST['select']
    ad_num=request.POST['adm_num']
    gender=request.POST['gender']
    dob=request.POST['dob']
    email=request.POST['email']
    phone=request.POST['phone']
    place=request.POST['place']
    city=request.POST['city']
    state=request.POST['state']
    pincode=request.POST['pincode']

    if 'photo' in request.FILES:
        photo = request.FILES['photo']
        dt = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg"
        fs = FileSystemStorage()
        fs.save(static_path + "images\\" + dt, photo)
        path = "/static/images/" + dt
        student.objects.filter(id=id).update(image = path)
    if student.objects.filter(std_name = name,COURSE_id = course,semester = semester,ad_num = ad_num,gender = gender,dob = dob,
        email = email,phone = phone,place = place,city = city,state = state,pin = pincode).exists():
        return HttpResponse("<script>alert('Student Exist');window.location='/adm_add_student';</script>")
    student.objects.filter(id=id).update(std_name = name,COURSE_id = course,semester = semester,ad_num = ad_num,gender = gender,dob = dob,
        email = email,phone = phone,place = place,city = city,state = state,pin = pincode)

    return HttpResponse("<script>alert('Student updated');window.location='/adm_view_student';</script>")


@login_required
@never_cache
def adm_view_student(request):
    data=student.objects.all()
    return render(request, "admin/view_student.html",   {"data":data})


@login_required
@never_cache
def adm_delete_student(request, id):
    student.objects.filter(id=id).delete()
    return HttpResponse("<script>alert('Student deleted');window.location='/adm_view_student';</script>")


@login_required
@never_cache
def adm_add_subject(request):
    data=course.objects.all()
    return render(request, "admin/add_subject.html", {"data":data})

def adm_add_subject_post(request):
    name=request.POST['name']
    semester=request.POST['select']
    course=request.POST['select2']
    if subject.objects.filter(sub_name = name,semester = semester,COURSE = course).exists():
        return HttpResponse("<script>alert('Subject Exist');window.location='/adm_add_subject';</script>")
    obj = subject()
    obj.sub_name = name
    obj.semester = semester
    obj.COURSE_id = course
    obj.save()
    return HttpResponse("<script>alert('Subject Added');window.location='/adm_view_subject';</script>")


@login_required
@never_cache
def adm_edit_subject(request, id):
    data = course.objects.all()
    data2=subject.objects.get(id=id)
    return render(request, "admin/edit_subject.html", {"data":data, "data2":data2})

def adm_edit_subject_post(request, id):
    name=request.POST['name']
    semester=request.POST['select']
    course=request.POST['select2']
    if subject.objects.filter(sub_name = name,semester = semester,COURSE = course).exists():
        return HttpResponse("<script>alert('Subject Exist');window.location='/adm_add_subject';</script>")
    subject.objects.filter(id=id).update(sub_name = name,semester = semester,COURSE = course)
    return HttpResponse("<script>alert('Subject updated');window.location='/adm_view_subject';</script>")


@login_required
@never_cache
def adm_view_subject(request):
    data=subject.objects.all()
    return render(request, "admin/view_subject.html",  {"data":data})


@login_required
@never_cache
def adm_delete_subject(request, id):
    subject.objects.filter(id=id).delete()
    return HttpResponse("<script>alert('Subject deleted');window.location='/adm_view_subject';</script>")


@login_required
@never_cache
def adm_view_suggestion(request):
    data=suggestion.objects.all()
    return render(request, "admin/view_suggestion.html", {"data":data})

@login_required
@never_cache
def adm_change_password(request):
    return render(request, "admin/change_password.html")

def adm_change_password_post(request):
    current=request.POST['cewp']
    new=request.POST['newp']
    cnew=request.POST['copsw']
    data=check_password( current, request.user.password)
    if data:
        if new == cnew:
            usr=request.user
            usr.password=make_password(cnew)
            usr.save()
            return HttpResponse("<script>alert('Password Changed');window.location='/';</script>")
        else:
            return HttpResponse("<script>alert('Password mismatch');window.location='/adm_change_password';</script>")
    else:
        return HttpResponse("<script>alert('Incorrect Password');window.location='/adm_change_password';</script>")


########################            FACULTY


@login_required
@never_cache
def fac_home(request):
    data = faculty.objects.get(id=request.session['fid'])
    request.session['fname']=data.name
    request.session['fmail']=data.email
    request.session['fimg']=data.image
    return render(request, "faculty/index.html",{'data':data})
    # return render(request, "faculty/homepage.html")


@login_required
@never_cache
def fac_view_assigned_subject(request):
    data=sub_allocation.objects.filter(FACULTY_id=request.session['fid'])
    return render(request, "faculty/view_assigned_subject.html", {"data":data})


@login_required
@never_cache
def fac_view_feedback(request):
    data=feedback.objects.filter(UNITS__SUB_ALLOCATION__FACULTY_id=request.session['fid'])
    return render(request, "faculty/view_feedback.html", {"data":data})


@login_required
@never_cache
def fac_add_internal_mark(request, id):
    sub_obj=subject.objects.get(id=id)
    data=student.objects.filter(COURSE=sub_obj.COURSE,semester=sub_obj.semester)
    return render(request, "faculty/add_internal_mark.html", {"data":data, "id":id})

def fac_add_internal_mark_post(request, id):
    sid = request.POST['select']
    i_mark = request.POST['mark']
    if internal_mark.objects.filter(STUDENT_id=sid,SUBJECT_id=id).exists():
        return HttpResponse("<script>alert('mark alredy given');window.location='/fac_view_internal_mark/" + str(id) + "';</script>")
    obj=internal_mark()
    obj.mark=i_mark
    obj.STUDENT_id=sid
    obj.SUBJECT_id=id
    obj.save()
    return HttpResponse(
        "<script>alert('Mark added');window.location='/fac_view_internal_mark/" + str(id) + "';</script>")


@login_required
@never_cache
def fac_view_internal_mark(request, id):
    data=internal_mark.objects.filter(SUBJECT_id=id)
    for i in data:
        i.perc = int(i.mark) * 100 / 20
    request.session['subid']=id
    return render(request, "faculty/view_internal_mark.html", {"data":data})


@login_required
@never_cache
def fac_delete_internal_mark(request, id):
    data = internal_mark.objects.filter(id=id).delete()
    sid=request.session['subid']
    return HttpResponse("<script>alert('Internal mark deleted');window.location='/fac_view_internal_mark/"+sid+"';</script>")


@login_required
@never_cache
def fac_view_reference_link(request, id):
    data=reference_link.objects.filter(UNITS_id=id)
    request.session['unitid']=id
    return render(request, "faculty/view_reference_link.html", {"data":data})


@login_required
@never_cache
def fac_delete_reference_link(request, id):
    data = reference_link.objects.filter(id=id).delete()
    unitid=request.session['unitid']
    return HttpResponse("<script>alert('Link deleted');window.location='/fac_view_reference_link/"+unitid+"';</script>")


@login_required
@never_cache
def fac_view_student(request):
    data=student.objects.all()
    return render(request, "faculty/view_student.html", {"data":data})


@login_required
@never_cache
def fac_view_units(request, id):
    request.session['allocid']=id
    data=units.objects.filter(SUB_ALLOCATION_id=id)
    return render(request, "faculty/view_units.html", {"data":data})


@login_required
@never_cache
def fac_view_exam_marks(request, id):
    unt=units.objects.get(id=id)
    studs=student.objects.filter(COURSE=unt.SUB_ALLOCATION.SUBJECT.COURSE)
    for i in studs:
        mrk=student_answer.objects.filter(QUESTION__UNITS=unt, STUDENT=i)
        if mrk.exists():
            tot=0
            for j in mrk:
                tot += int(j.score)
            i.marks=tot
        else:
            i.marks=0
    return render(request, "faculty/view_exam_mark.html", {"data":studs})

@login_required
@never_cache
def fac_add_qa(request, id):
    return render(request, "faculty/qa_generation.html", {"id": id})

def fac_add_qat_post(request, id):
    title=request.POST['title']
    qa_pairs = generate_qa_from_text(title, GEMINI_API_KEY)
    # Access questions and answers
    for item in qa_pairs:
        print(f"Q: {item['question']}")
        print(f"A: {item['answer']}")
        print()
        obj=questions()
        obj.question=item['question']
        obj.answer=item['answer']
        obj.UNITS_id=id
        obj.save()
    allocid= request.session['allocid']
    return HttpResponse("<script>alert('Questions Added');window.location='/fac_view_units/"+allocid+"';</script>")

@login_required
@never_cache
def fac_view_qa(request, id):
    # request.session['unitid']=id
    data=questions.objects.filter(UNITS_id=id)
    return render(request, "faculty/qa_view.html", {"data":data})

@login_required
@never_cache
def fac_add_unit(request, id):
    return render(request, "faculty/add_unit.html", {"id": id})

def fac_add_unit_post(request, id):
    name=request.POST['unitname']
    if units.objects.filter(unit_name=name,SUB_ALLOCATION_id=id).exists():
        return HttpResponse("<script>alert('unit alredy exist');window.location='/fac_add_unit/"+id+"';</script>")
    if len(units.objects.filter(SUB_ALLOCATION_id=id))>4:
        return HttpResponse("<script>alert('Cant add more than 5 units');window.location='/fac_add_unit/"+id+"';</script>")

    obj=units()
    obj.unit_name=name
    obj.SUB_ALLOCATION_id=id
    obj.save()
    return HttpResponse("<script>alert('Unit Added');window.location='/fac_view_units/"+id+"';</script>")

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
def piechart(stat, scor):
    # Pie chart, where the slices will be ordered and plotted counter-clockwise:
    # labels = 'Sale', 'Purchase'
    # sizes = [random.randint(10,30), random.randint(30,50)]
    explode = (0.1, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')

    fig1, ax1 = plt.subplots()
    if scor.count(0) == len(scor):
        scor[1]=1   #   if no feedbacks, highlight neutral as default
    print(scor)
    ax1.pie(scor, explode=explode, labels=stat, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    dt=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename=dt+".png"
    plt.savefig('C:/Users/LENOVO/PycharmProjects/edu_ai/myapp/static/graph/'+filename, dpi=100)
    print(filename)
    return filename


@login_required
@never_cache
def fac_view_feedback_unitwise(request, id):
    data=feedback.objects.filter(UNITS_id=id)
    pos_cnt=0
    neg_cnt=0
    neu_cnt=0
    ar=[]
    for i in data:
        res=classify_with_vader(i.feedback)
        if res=="negative":
            neg_cnt += 1
        elif res == "positive":
            pos_cnt += 1
        else:
            neu_cnt += 1
        i.feed_type=res
        ar.append(i.feedback)
    print(ar)
    res_txt=run_analysis(ar)        #   new code
    labels=["Positive", "Neutral", "Negative"]
    scores=[pos_cnt, neu_cnt, neg_cnt]
    print("REss")
    print(labels)
    print(scores)
    fname=piechart(labels, scores)
    return render(request, "faculty/view_feedback_unitwise.html", {"data":data, "graph_path":"/static/graph/"+fname, "res_txt":res_txt})


@login_required
@never_cache
def fac_add_reference_link(request, id):
    return render(request, "faculty/add_reference_link.html", {"id": id})

def fac_add_reference_link_post(request, id):
    title=request.POST['title']
    ref_link=request.POST['ref-link']

    if reference_link.objects.filter(date=datetime.datetime.now().date(),title=title,ref_link=ref_link,UNITS_id=id).exists():
        return HttpResponse("<script>alert('link alredy exist');window.location='/fac_home';</script>")
    obj=reference_link()
    obj.date=datetime.datetime.now().date()
    obj.title=title
    obj.ref_link=ref_link
    obj.UNITS_id=id
    obj.save()
    return HttpResponse("<script>alert('Added');window.location='/fac_home';</script>")


@login_required
@never_cache
def fac_view_students(request):
    data=student.objects.all()
    # sub = subject.objects.
    return render(request, "faculty/view_students.html",{'data':data})


@login_required
@never_cache
def fac_send_suggestion(request):
    return render(request, "faculty/send_suggestion.html")

def fac_send_suggestion_post(request):
    sugg=request.POST['sugg']
    if suggestion.objects.filter(date = datetime.datetime.now().date(),suggestion=sugg,FACULTY_id=request.session['fid']).exists():
        return HttpResponse("<script>alert('Suggestion Exist');window.location='/fac_send_suggestion';</script>")
    obj=suggestion()
    obj.date = datetime.datetime.now().date()
    obj.suggestion=sugg
    obj.FACULTY_id=request.session['fid']
    obj.save()
    return HttpResponse("<script>alert('Suggestion Added');window.location='/fac_home';</script>")


@login_required
@never_cache
def fac_change_password(request):
    return render(request, "faculty/change_password.html")

def fac_change_password_post(request):
    current=request.POST['cewp']
    new=request.POST['newp']
    cnew=request.POST['copsw']
    data=check_password( current, request.user.password)
    if data:
        if new == cnew:
            usr=request.user
            usr.password=make_password(cnew)
            usr.save()
            return HttpResponse("<script>alert('Password Changed');window.location='/';</script>")
        else:
            return HttpResponse("<script>alert('Password mismatch');window.location='/fac_change_password';</script>")
    else:
        return HttpResponse("<script>alert('Incorrect Password');window.location='/fac_change_password';</script>")






##################          STUDENT
def stud_login(request):
    un=request.POST['un']
    ps=request.POST['ps']
    data=authenticate(request, username=un, password=ps)
    if data:
        login(request, data)
        if data.groups.filter(name="student").exists():
            sid=student.objects.get(LOGIN_id=request.user.id).id
            sname=student.objects.get(LOGIN_id=request.user.id).std_name
            semail=student.objects.get(LOGIN_id=request.user.id).email
            return JsonResponse({"status": "ok", "sid": str(sid), "sname":sname, "semail":semail})
        else:
            return JsonResponse({"status": "no"})
    else:
        return JsonResponse({"status": "no"})



def stud_view_profile(request):
    sid=request.POST['sid']
    data=student.objects.filter(id=sid)
    ar=[]
    for i in data:
        ar.append({
            "id":i.id, "std_name":i.std_name, "course":i.COURSE.course_name, "semester":i.semester, "ad_num":i.ad_num,
            "gender":i.gender, "dob":i.dob, "email":i.email, "phone":i.phone, "place":i.place,
            "state":i.state, "city":i.city, "pin":i.pin, "image":i.image,
        })
    print(ar)
    return JsonResponse({"status":"ok", "data":ar})


def stud_view_subject(request):
    sid = request.POST['sid']
    stud_obj=student.objects.get(id=sid)
    data = sub_allocation.objects.filter(SUBJECT__COURSE=stud_obj.COURSE, SUBJECT__semester=stud_obj.semester)
    ar = []
    for i in data:
        ar.append({
            "id": i.id, "sid":i.SUBJECT.id, "sub_name": i.SUBJECT.sub_name, "semester": i.SUBJECT.semester, "course": i.SUBJECT.COURSE.course_name,
            "fname":i.FACULTY.name, 'fid':i.FACULTY.id
        })

    return JsonResponse({"status": "ok", "data": ar})

def stud_view_units(request):
    suballocid = request.POST['suballocid']
    data = units.objects.filter(SUB_ALLOCATION_id=suballocid)
    ar = []
    for i in data:
        ar.append({
            "id": i.id, "unit_name": i.unit_name
        })

    return JsonResponse({"status": "ok", "data": ar})

def stud_view_reference(request):
    unitid=request.POST['unitid']
    data = reference_link.objects.filter(UNITS_id=unitid)
    ar = []
    for i in data:
        ar.append({
            "id": i.id, "date": i.date, "title": i.title, "refer_link": i.ref_link ,
        })
    return JsonResponse({"status": "ok", "data": ar})

def stud_view_internal_mark(request):
    sid=request.POST['sid']
    subid=request.POST['subid']
    data=internal_mark.objects.filter(STUDENT_id=sid, SUBJECT_id=subid)
    ar = []
    for i in data:
        ar.append({
            "id": i.id, "mark": i.mark
        })

    return JsonResponse({"status": "ok", "data": ar})

def stud_view_qa(request):
    unitid=request.POST['unitid']
    data=questions.objects.filter(UNITS_id=unitid)
    ar = []
    for i in data:
        ar.append({
            "id": i.id, "question": i.question, "answer":i.answer
        })

    return JsonResponse({"status": "ok", "data": ar})

def stud_send_feedback(request):
    sid = request.POST['sid']
    unitid = request.POST['unitid']
    feed = request.POST['feed']
    data = feedback.objects.filter(UNITS_id=unitid, STUDENT_id=sid)
    if data.exists():
        data=data[0]
        data.date=datetime.datetime.now().date()
        data.feedback=feed
        data.save()
    else:
        data=feedback()
        data.UNITS_id=unitid
        data.STUDENT_id=sid
        data.date = datetime.datetime.now().date()
        data.feedback = feed
        data.save()
    return JsonResponse({"status": "ok"})

def stud_change_password(request):
    current=request.POST['cewp']
    new=request.POST['newp']
    cnew=request.POST['copsw']
    sid=request.POST['sid']
    stud_obj=student.objects.get(id=sid)
    data=check_password( current, stud_obj.LOGIN.password)
    if data:
        if new == cnew:
            usr=stud_obj.LOGIN
            usr.password=make_password(cnew)
            usr.save()
            return JsonResponse({"status": "ok"})
        else:
            return JsonResponse({"status": "mismatch"})
    else:
        return JsonResponse({"status": "no"})



def stud_sendchat(request):
    FROM_id=request.POST['sid']
    TOID_id=request.POST['fid']
    msg=request.POST['message']
    c=chat()
    c.STUDENT_id=FROM_id
    c.FACULTY_id=TOID_id
    c.chat=msg
    c.type="student"
    c.date=datetime.datetime.now()
    c.save()
    return JsonResponse({'status':"ok"})

def stud_viewchat(request):
    from_id=request.POST['sid']
    to_id=request.POST['fid']
    # print(to_id)

    l=[]
    data=chat.objects.filter(STUDENT=from_id,FACULTY=to_id).order_by('id')
    for res in data:
        l.append({'id':res.id,'from':res.STUDENT.id,'to':res.FACULTY.id,'msg':res.chat,'date':res.date,"type":res.type})



    return JsonResponse({'status':"ok",'data':l})


def view_student_chat(request):
    data = chat.objects.filter(FACULTY = request.session['fid']).order_by('-id')
    studentslist = []
    for i in data:
        if i.STUDENT.id not in studentslist:
            studentslist.append(i.STUDENT.id)
    print(studentslist,"okyyy")
    selected_student = []
    for i in studentslist:
        selected_student.append(
            student.objects.get(id=i)
        )
    print(selected_student,"op")
    return render(request,'faculty/view_student.html',{'data':selected_student})


@login_required
@never_cache
def fac_chatt(request, u):
    request.session['head'] = "CHAT"
    request.session['uid'] = u
    return render(request, 'faculty/chat.html', {'u': u})


@login_required
@never_cache
def fac_chatsnd(request, u):
    m = request.POST.get('m', '').strip()
    # Create and save chat message
    obj = chat(
        date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Added time
        type='faculty',
        FACULTY_id=request.session['fid'],
        STUDENT_id=request.session['uid'],
        chat=m
    )
    obj.save()

    return JsonResponse({"status": "ok", "message_id": obj.id})


@login_required
@never_cache
def fac_chatrply(request):
    last_id = request.POST.get('last_id', 0)
    try:
        last_id = int(last_id)
    except ValueError:
        last_id = 0

    # Get messages with proper ordering and filtering
    messages = chat.objects.filter(
        FACULTY=request.session['fid'],
        STUDENT=request.session['uid'],
        id__gt=last_id  # Only get messages newer than last_id
    ).order_by('id')  # Ensure chronological order

    v = []
    for i in messages:
        v.append({
            'id': i.id,  # Include message ID for tracking
            'type': i.type,
            'chat': i.chat,
            'selimage': '',  # You can add actual image paths here
            'uimage': '',  # You can add actual image paths here
            'date': i.date,
        })

    return JsonResponse({
        "status": "ok",
        "data": v,
        "count": len(v),
        "last_id": messages.last().id if messages else last_id
    })




def forgotpassword(request):
    return render(request,"forgotpassword.html")

def forgotpasswordbuttonclick(request):
    email = request.POST['textfield']
    print(email)
    if User.objects.filter(username=email).exists():
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        # ✅ Gmail credentials (use App Password, not real password)
        sender_email = "service.edu.ai@gmail.com"
        print(sender_email)
        receiver_email = email  # change to actual recipient
        print(receiver_email)
        app_password = "gldb wolw ufgm ieed"  # App Password from Google
        pwd = str(random.randint(1100,9999))  # Example password to send
        request.session['otp'] = pwd
        request.session['email'] = email

        # Setup SMTP
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)

        # Create the email
        msg = MIMEMultipart("alternative")
        msg["From"] = sender_email
        print( msg["From"] )
        msg["To"] = receiver_email
        msg["Subject"] = "Your OTP"

        # Plain text (backup)
        # text = f"""
        # Hello,

        # Your password for Smart Donation Website is: {pwd}

        # Please keep it safe and do not share it with anyone.
        # """

        # HTML (attractive)
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color:#2c7be5;">Edu AI</h2>
            <p>Hello,</p>
            <p>Your OTP is:</p>
            <p style="padding:10px; background:#f4f4f4; 
                      border:1px solid #ddd; 
                      display:inline-block;
                      font-size:18px;
                      font-weight:bold;
                      color:#2c7be5;">
              {pwd}
            </p>
            <p>Please keep it safe and do not share it with anyone.</p>
            <hr>
            <small style="color:gray;">This is an automated email from Edu AI System.</small>
          </body>
        </html>
        """

        # Attach both versions
        # msg.attach(MIMEText(text, "plain"))
        msg.attach(MIMEText(html, "html"))

        # Send email
        server.send_message(msg)
        print("✅ Email sent successfully!")

        # Close connection
        server.quit()
        return HttpResponse("<script>window.location='/otp'</script>")
    else:
        return HttpResponse("<script>alert('Email not found');window.location='/forgotpassword'</script>")


def otp(request):
    return render(request,"otp.html")
def otpbuttonclick(request):
    otp  = request.POST["textfield"]
    if otp == str(request.session['otp']):
        return HttpResponse("<script>window.location='/forgotpswdpswed'</script>")
    else:
        return HttpResponse("<script>alert('incorrect otp');window.location='/otp'</script>")

def forgotpswdpswed(request):
    return render(request,"forgotpswdpswed.html")
def forgotpswdpswedbuttonclick(request):
    np = request.POST["password"]
    User.objects.filter(username=request.session['email']).update(password=make_password(np))
    return HttpResponse("<script>alert('password has been changed');window.location='/' </script>")



#### flutter forgot ####################3



def forgotemail(request):
    import random
    import smtplib
    email = request.POST['email']
    print(email)
    data = User.objects.filter(username=email)
    print(data)
    if data.exists():
        otp = str(random.randint(000000, 999999))
        print(otp)
        # *✨ Python Email Codeimport smtplib*

        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        # ✅ Gmail credentials (use App Password, not real password)
        try:
            sender_email = "service.edu.ai@gmail.com"
            receiver_email = email  # change to actual recipient
            app_password = "gldb wolw ufgm ieed"
            # Setup SMTP
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, app_password)

            # Create the email
            msg = MIMEMultipart("alternative")
            msg["From"] = sender_email
            msg["To"] = receiver_email
            msg["Subject"] = "🔑 Forgot Password "

            # Plain text (backup)
            # text = f"""
            # Hello,

            # Your password for Smart Donation Website is: {pwd}

            # Please keep it safe and do not share it with anyone.
            # """

            # HTML (attractive)
            html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Password Reset OTP</title>
                </head>
                <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                            line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">

                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                        <h1 style="color: white; margin: 0; font-size: 28px;">
                            🔐 Edu AI
                        </h1>
                    </div>

                    <div style="background-color: #f9f9f9; padding: 40px 30px; border-radius: 0 0 10px 10px; 
                                border: 1px solid #eaeaea;">

                        <h2 style="color: #2d3748; margin-top: 0;">Password Reset Request</h2>

                        <p style="color: #4a5568; font-size: 16px;">
                            Hello,
                        </p>

                        <p style="color: #4a5568; font-size: 16px;">
                            You requested to reset your password. Use the OTP below to proceed:
                        </p>

                        <div style="background: white; border-radius: 8px; padding: 20px; 
                                    text-align: center; margin: 30px 0; border: 2px dashed #cbd5e0;">
                            <div style="font-size: 32px; font-weight: bold; letter-spacing: 10px; 
                                        color: #2c7be5; margin: 10px 0;">
                                {otp}
                            </div>
                            <div style="font-size: 14px; color: #718096; margin-top: 10px;">
                                (Valid for 10 minutes)
                            </div>
                        </div>

                        <p style="color: #4a5568; font-size: 16px;">
                            Enter this code on the password reset page to complete the process.
                        </p>

                        <div style="background-color: #fef3c7; border-left: 4px solid #d97706; 
                                    padding: 15px; margin: 25px 0; border-radius: 4px;">
                            <p style="color: #92400e; margin: 0; font-size: 14px;">
                                ⚠️ <strong>Security tip:</strong> Never share this OTP with anyone. 
                                Our team will never ask for your password or OTP.
                            </p>
                        </div>

                        <p style="color: #718096; font-size: 14px;">
                            If you didn't request this password reset, please ignore this email or 
                            contact our support team if you have concerns.
                        </p>

                        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;">

                        <p style="text-align: center; color: #a0aec0; font-size: 12px;">
                            This is an automated email from Edu AI System.<br>
                            © {datetime.datetime.now().year} Edu AI. All rights reserved.
                        </p>

                    </div>
                </body>
                </html>
                """

            # Attach both versions
            # msg.attach(MIMEText(text, "plain"))
            msg.attach(MIMEText(html, "html"))

            # Send email
            server.send_message(msg)
            print("✅ Email sent successfully!", otp)

            # Close connection
            server.quit()

        except Exception as e:
            print("❌ Error loading email credentials:", e)
            return JsonResponse({'status': "ok", 'otpp': otp})

        return JsonResponse({'status': 'ok', 'otpp': otp})
    return JsonResponse({'status': "not found"})


def forgotpass(request):
    email = request.POST['email']
    npass = request.POST['password']
    cpass = request.POST['confirmpassword']
    print(email, npass, cpass)
    if npass == cpass:
        User.objects.filter(username=email).update(password=make_password(npass))
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'invalid'})








#############################               student     performance analysis
from django.http import JsonResponse
from django.db.models import Avg, Count, Q
import json
import numpy as np


def student_get_study_plan(request):
    """
    Django view to generate study plan with analysis
    """
    if request.method == "POST":
        try:
            sid = request.POST.get("sid")

            # Get the student
            student_obj = student.objects.get(id=sid)
            current_course = student_obj.COURSE
            current_semester = student_obj.semester

            # Get all subjects for the student
            student_subjects = subject.objects.filter(
                semester=current_semester,
                COURSE=current_course
            )

            # Get classmates
            classmates = student.objects.filter(
                COURSE=current_course,
                semester=current_semester
            ).exclude(id=sid)

            study_plan = []
            subject_performance = {}

            # Analyze each subject
            for subj in student_subjects:
                # Get student's marks
                student_marks = internal_mark.objects.filter(
                    STUDENT=student_obj,
                    SUBJECT=subj
                )

                # Get classmates' marks
                class_marks = internal_mark.objects.filter(
                    SUBJECT=subj,
                    STUDENT__in=classmates
                )

                # Calculate averages
                student_avg = calculate_average(student_marks)
                class_avg = calculate_average(class_marks) if class_marks.exists() else 0

                # Determine study hours based on performance gap
                if student_avg == 0:
                    study_hours = 2.5
                elif student_avg >= class_avg + 10:
                    study_hours = 1.0
                elif student_avg >= class_avg:
                    study_hours = 1.5
                elif student_avg >= class_avg - 10:
                    study_hours = 2.0
                elif student_avg >= class_avg - 20:
                    study_hours = 3.0
                else:
                    study_hours = 4.0

                # Store data
                subject_performance[subj.sub_name] = {
                    'student_avg': student_avg,
                    'class_avg': class_avg,
                    'gap': class_avg - student_avg
                }

                # Add to study plan
                study_plan.append({
                    "subject_name": subj.sub_name,
                    "time": f"{study_hours} hours",
                    "student_score": student_avg,
                    "class_average": class_avg,
                    "performance_gap": round(class_avg - student_avg, 2),
                    "priority": "High" if study_hours >= 3 else "Medium" if study_hours >= 2 else "Low"
                })

            # Sort by study hours (descending)
            study_plan.sort(key=lambda x: float(x['time'].split()[0]), reverse=True)

            # Generate analysis
            analysis = generate_analysis(student_obj, subject_performance)

            # Prepare response
            response_data = {
                "status": "success",
                "data": study_plan,
                "analysis": analysis,
                "student_info": {
                    "name": student_obj.std_name,
                    "course": current_course.name if hasattr(current_course, 'name') else str(current_course),
                    "semester": current_semester,
                    "admission_no": student_obj.ad_num
                }
            }

            return JsonResponse(response_data)

        except student.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Student not found"}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)


def calculate_average(marks_queryset):
    """Calculate average marks"""
    total = 0
    count = 0

    for mark_record in marks_queryset:
        try:
            total += float(mark_record.mark)
            count += 1
        except:
            continue

    return round(total / count, 2) if count > 0 else 0


def generate_analysis(student_obj, subject_performance):
    """Generate performance analysis"""
    if not subject_performance:
        return {
            "overall_status": "No Data",
            "description": "No marks available for analysis",
            "strengths": [],
            "weaknesses": []
        }

    # Calculate overall performance
    student_scores = [data['student_avg'] for data in subject_performance.values()]
    class_scores = [data['class_avg'] for data in subject_performance.values()]

    student_overall = np.mean(student_scores) if student_scores else 0
    class_overall = np.mean(class_scores) if class_scores else 0

    # Identify strengths and weaknesses
    strengths = []
    weaknesses = []

    for subj, data in subject_performance.items():
        if data['student_avg'] > data['class_avg']:
            strengths.append({
                "subject": subj,
                "advantage": round(data['student_avg'] - data['class_avg'], 2)
            })
        elif data['student_avg'] < data['class_avg']:
            weaknesses.append({
                "subject": subj,
                "disadvantage": round(data['class_avg'] - data['student_avg'], 2)
            })

    # Determine status
    if student_overall >= class_overall + 10:
        status = "Excellent Performer"
        description = f"Your performance is outstanding! You're {round(student_overall - class_overall, 1)}% above class average."
    elif student_overall >= class_overall:
        status = "Above Average"
        description = f"You're performing better than average. Keep up the good work!"
    elif student_overall >= class_overall - 10:
        status = "Average"
        description = f"You're at par with classmates. Focus on improving weak areas."
    else:
        status = "Needs Improvement"
        description = f"Your performance is {round(class_overall - student_overall, 1)}% below class average. Focus on study plan."

    # Future risks
    future_risks = []
    for subj, data in subject_performance.items():
        if data['gap'] > 15:
            future_risks.append({
                "subject": subj,
                "gap": round(data['gap'], 2),
                "risk_level": "High"
            })
        elif data['gap'] > 5:
            future_risks.append({
                "subject": subj,
                "gap": round(data['gap'], 2),
                "risk_level": "Medium"
            })

    return {
        "overall_status": status,
        "description": description,
        "overall_score": round(student_overall, 2),
        "class_average": round(class_overall, 2),
        "strengths": strengths[:3],
        "weaknesses": weaknesses[:3],
        "future_risks": future_risks[:5],
        "recommendations": [
            "Follow the suggested study plan consistently",
            "Focus more on subjects with higher study hours",
            "Review class notes regularly",
            "Practice previous exam papers"
        ]
    }







##############              summary generiser
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
import os
import tempfile
from docx import Document
import spacy
import re
import string
import requests
import json
import time

# Initialize spaCy model for preprocessing
try:
    nlp = spacy.load("en_core_web_sm")
except:
    # Fallback - we'll install it if missing
    nlp = None

# Gemini API Configuration
GEMINI_API_KEY = "AIzaSyCIHagpTMb60QHutBYRJMND5jlzc-IowEs"  # Replace with your actual API key
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"


def initialize_spacy():
    """Initialize spaCy if not already loaded"""
    global nlp
    if nlp is None:
        try:
            nlp = spacy.load("en_core_web_sm")
        except:
            # Install if not present
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "pip", "install", "spacy"])
            subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            nlp = spacy.load("en_core_web_sm")


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from Word document"""
    try:
        doc = Document(file_path)
        full_text = []

        # Extract text from paragraphs
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                full_text.append(paragraph.text)

        # Extract text from tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        full_text.append(cell.text)

        return '\n'.join(full_text)
    except Exception as e:
        # Fallback method for older .doc files or corrupted .docx
        try:
            import zipfile
            import xml.etree.ElementTree as ET

            with zipfile.ZipFile(file_path, 'r') as docx:
                xml_content = docx.read('word/document.xml')
                root = ET.fromstring(xml_content)
                ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

                paragraphs = []
                for p in root.findall('.//w:p', ns):
                    texts = []
                    for t in p.findall('.//w:t', ns):
                        if t.text:
                            texts.append(t.text)
                    if texts:
                        paragraphs.append(''.join(texts))

                return '\n'.join(paragraphs)
        except:
            raise Exception(f"Cannot extract text: {str(e)}")


def preprocess_text_with_nlp(text: str) -> dict:
    """
    Preprocess text using NLP techniques to enhance Gemini's understanding
    """
    initialize_spacy()

    if not text or len(text.strip()) < 10:
        return {
            "cleaned_text": text,
            "entities": [],
            "key_themes": [],
            "sentence_count": 0,
            "word_count": len(text.split()),
            "preprocessed": False
        }

    try:
        doc = nlp(text)

        # Extract named entities
        entities = []
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            })

        # Extract key themes (noun phrases)
        key_themes = []
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) > 1:  # Only multi-word phrases
                key_themes.append(chunk.text)

        # Remove duplicates
        key_themes = list(set(key_themes))

        # Clean text - remove excessive whitespace and normalize
        cleaned_text = re.sub(r'\s+', ' ', text).strip()

        # Count sentences and words
        sentence_count = len(list(doc.sents))
        word_count = len([token for token in doc if not token.is_punct and not token.is_space])

        # Extract important sentences (for context)
        important_sentences = []
        for sent in doc.sents:
            # Simple heuristic: sentences with named entities are often important
            if any(ent.text in sent.text for ent in doc.ents):
                important_sentences.append(sent.text[:200])  # Limit length

        return {
            "cleaned_text": cleaned_text,
            "entities": entities[:10],  # Limit to 10 entities
            "key_themes": key_themes[:15],  # Limit to 15 themes
            "important_sentences": important_sentences[:5],
            "sentence_count": sentence_count,
            "word_count": word_count,
            "preprocessed": True
        }
    except Exception as e:
        # Fallback to basic preprocessing if NLP fails
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        word_count = len(cleaned_text.split())
        sentences = re.split(r'[.!?]+', cleaned_text)
        sentence_count = len([s for s in sentences if s.strip()])

        return {
            "cleaned_text": cleaned_text,
            "entities": [],
            "key_themes": [],
            "important_sentences": sentences[:3],
            "sentence_count": sentence_count,
            "word_count": word_count,
            "preprocessed": False
        }


def create_gemini_prompt(preprocessed_data: dict) -> str:
    """
    Create an optimized prompt for Gemini based on preprocessed text
    """
    text = preprocessed_data["cleaned_text"]
    entities = preprocessed_data["entities"]
    key_themes = preprocessed_data["key_themes"]
    important_sentences = preprocessed_data["important_sentences"]
    word_count = preprocessed_data["word_count"]

    # Determine summary length based on text size
    if word_count < 1000:
        summary_length = "brief (5-8 sentences)"
    elif word_count < 5000:
        summary_length = "concise (9-15 sentences)"
    else:
        summary_length = "comprehensive (16-20 sentences)"

    prompt = f"""Please analyze the following text and provide a {summary_length} summary.

TEXT TO SUMMARIZE:
{text[:10000]}  # Limit text to avoid token limits

"""

    # Add context from NLP preprocessing
    if entities:
        entity_list = ', '.join([f"{e['text']} ({e['label']})" for e in entities[:5]])
        prompt += f"\nKEY ENTITIES IDENTIFIED: {entity_list}\n"

    if key_themes:
        themes_list = ', '.join(key_themes[:10])
        prompt += f"\nMAIN THEMES: {themes_list}\n"

    if important_sentences:
        prompt += "\nIMPORTANT CONTEXT SENTENCES:\n"
        for i, sent in enumerate(important_sentences[:3], 1):
            prompt += f"{i}. {sent}\n"

    prompt += """
Please provide a well-structured summary that:
1. Captures the main purpose and key points
2. Highlights important findings or conclusions
3. Maintains the original context and meaning
4. Is easy to read and understand

SUMMARY:
"""

    return prompt


def call_gemini_api(prompt: str, max_retries: int = 3) -> dict:
    """
    Call Gemini API to generate summary
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
        raise Exception("Gemini API key not configured. Please add your API key.")

    headers = {
        "Content-Type": "application/json",
    }

    # Gemini request payload
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 1000,
        },
        "safetySettings": [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
    }

    url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"

    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()

                # Extract the generated text
                if "candidates" in result and result["candidates"]:
                    if "content" in result["candidates"][0]:
                        content = result["candidates"][0]["content"]
                        if "parts" in content and content["parts"]:
                            return {
                                "success": True,
                                "summary": content["parts"][0].get("text", ""),
                                "raw_response": result
                            }

                return {
                    "success": False,
                    "error": "No valid content in response",
                    "raw_response": result
                }

            elif response.status_code == 429:  # Rate limit
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Rate limited. Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                continue

            else:
                return {
                    "success": False,
                    "error": f"API error {response.status_code}: {response.text}",
                    "status_code": response.status_code
                }

        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                print(f"Timeout. Retrying ({attempt + 1}/{max_retries})...")
                continue
            else:
                return {
                    "success": False,
                    "error": "Request timeout after multiple retries"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Request failed: {str(e)}"
            }

    return {
        "success": False,
        "error": "Max retries exceeded"
    }


def generate_summary_with_gemini(preprocessed_data: dict) -> dict:
    """
    Generate summary using Gemini API
    """
    try:
        # Create optimized prompt
        prompt = create_gemini_prompt(preprocessed_data)

        # Call Gemini API
        gemini_result = call_gemini_api(prompt)

        if gemini_result["success"]:
            return {
                "success": True,
                "summary": gemini_result["summary"].strip(),
                "method": "gemini_ai",
                "prompt_length": len(prompt),
                "tokens_estimated": len(prompt.split()) // 0.75  # Rough estimate
            }
        else:
            # Fallback to extractive summarization if Gemini fails
            return generate_fallback_summary(preprocessed_data)

    except Exception as e:
        # Fallback if any error occurs
        return generate_fallback_summary(preprocessed_data)


def generate_fallback_summary(preprocessed_data: dict) -> dict:
    """
    Fallback summary generation using extractive methods
    """
    text = preprocessed_data["cleaned_text"]
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    # Simple extractive summarization
    if len(sentences) <= 3:
        summary = '. '.join(sentences) + '.'
    else:
        # Take first, middle, and last sentences
        first = sentences[0]
        middle = sentences[len(sentences) // 2]
        last = sentences[-1]
        summary = f"{first}. {middle}. {last}."

    return {
        "success": True,
        "summary": summary,
        "method": "extractive_fallback",
        "note": "Used fallback method as Gemini was unavailable"
    }


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_and_analyze_with_gemini(request):
    """
    Handle document upload, preprocess with NLP, and generate summary using Gemini
    """
    # Check if file is present
    if 'document' not in request.FILES:
        return Response(
            {
                'status': 'error',
                'message': 'No document file provided.',
                'error_code': 'NO_FILE'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    document_file = request.FILES['document']
    original_filename = document_file.name
    file_size = document_file.size

    # Validate file size
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    if file_size > MAX_FILE_SIZE:
        return Response(
            {
                'status': 'error',
                'message': f'File size ({file_size/1024/1024:.1f}MB) exceeds 10MB limit.',
                'error_code': 'FILE_TOO_LARGE'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate file extension
    file_ext = os.path.splitext(original_filename)[1].lower()
    allowed_extensions = ['.docx', '.doc']

    if file_ext not in allowed_extensions:
        return Response(
            {
                'status': 'error',
                'message': f'File type {file_ext} not supported. Use .doc or .docx',
                'error_code': 'INVALID_FILE_TYPE'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    temp_file_path = None

    try:
        # Create upload directory
        upload_dir = os.path.join(os.getcwd(), 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # Save file temporarily
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=file_ext,
            dir=upload_dir
        )

        for chunk in document_file.chunks():
            temp_file.write(chunk)

        temp_file_path = temp_file.name
        temp_file.close()

        # Validate .docx file structure
        if file_ext == '.docx':
            try:
                import zipfile
                with zipfile.ZipFile(temp_file_path, 'r') as zf:
                    if 'word/document.xml' not in zf.namelist():
                        raise ValueError("Invalid .docx structure")
            except:
                return Response(
                    {
                        'status': 'error',
                        'message': 'Invalid .docx file format.',
                        'error_code': 'INVALID_DOCX'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Step 1: Extract text
        print("Extracting text from document...")
        extracted_text = extract_text_from_docx(temp_file_path)

        if not extracted_text or len(extracted_text.strip()) < 50:
            return Response(
                {
                    'status': 'error',
                    'message': 'Document is empty or contains insufficient text.',
                    'error_code': 'EMPTY_DOCUMENT'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Step 2: Preprocess with NLP
        print("Preprocessing text with NLP...")
        preprocessed_data = preprocess_text_with_nlp(extracted_text)

        # Step 3: Generate summary with Gemini
        print("Generating summary with Gemini AI...")
        start_time = time.time()
        summary_result = generate_summary_with_gemini(preprocessed_data)
        processing_time = time.time() - start_time

        # Step 4: Prepare response
        response_data = {
            'status': 'success',
            'filename': original_filename,
            'file_size_bytes': file_size,
            'file_size_mb': f"{file_size/1024/1024:.2f}",

            # Text statistics
            'original_text_length': len(extracted_text),
            'cleaned_text_length': len(preprocessed_data['cleaned_text']),
            'word_count': preprocessed_data['word_count'],
            'sentence_count': preprocessed_data['sentence_count'],

            # NLP preprocessing results
            'nlp_preprocessed': preprocessed_data['preprocessed'],
            'entities_count': len(preprocessed_data['entities']),
            'key_themes_count': len(preprocessed_data['key_themes']),

            # Summary results
            'summary': summary_result['summary'],
            'summary_method': summary_result['method'],
            'summary_length': len(summary_result['summary']),

            # Processing info
            'processing_time_seconds': round(processing_time, 2),
            'timestamp': datetime.datetime.now().isoformat(),

            # Additional context
            'key_themes': preprocessed_data['key_themes'][:10],
            'important_entities': [
                f"{e['text']} ({e['label']})"
                for e in preprocessed_data['entities'][:5]
            ]
        }

        # Add fallback note if used
        if summary_result.get('note'):
            response_data['note'] = summary_result['note']

        # Clean up temp file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        # Clean up temp file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass

        error_msg = str(e)
        print(f"Error processing document: {error_msg}")

        return Response(
            {
                'status': 'error',
                'message': f'Document processing failed: {error_msg}',
                'error_code': 'PROCESSING_ERROR',
                'suggestion': 'Please ensure the document is a valid Word file and contains readable text.'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def health_check(request):
    """Health check endpoint with Gemini status"""
    gemini_status = "configured" if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY" else "not_configured"
    spacy_status = "loaded" if nlp else "not_loaded"

    return Response({
        'status': 'healthy',
        'service': 'Document Analysis with Gemini AI',
        'timestamp': datetime.datetime.now().isoformat(),
        'gemini_api': gemini_status,
        'spacy_nlp': spacy_status,
        'endpoints': {
            'upload': '/upload',
            'health': '/health'
        }
    }, status=status.HTTP_200_OK)



####        cosine similarity based evaluation
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import word_tokenize

# Download required NLTK data
# nltk.download('punkt')
# nltk.download('stopwords')


def cosine_similarity_tfidf(text1, text2):
    # Create TF-IDF vectorizer with NLTK's tokenizer and stopwords
    from nltk.corpus import stopwords

    vectorizer = TfidfVectorizer(
        tokenizer=word_tokenize,
        stop_words=stopwords.words('english'),
        lowercase=True
    )

    # Transform texts to TF-IDF vectors
    tfidf_matrix = vectorizer.fit_transform([text1, text2])

    # Calculate cosine similarity
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])

    return similarity[0][0]


# Example usage
text1 = "I love horror movies"
text2 = "Lights out is a horror movie"
similarity = cosine_similarity_tfidf(text1, text2)
print(f"Similarity: {similarity}")
def submit_answer(request):
    question_id=request.POST['question_id']
    student_id=request.POST['student_id']
    answer=request.POST['answer']
    max_mark=10
    correct_ans=questions.objects.get(id=question_id).answer
    sim_score=cosine_similarity_tfidf(correct_ans, answer)
    print("Similarity : ", sim_score)
    score=int(round(sim_score,2)*max_mark)
    obj=student_answer()
    obj.score=score
    obj.answer=answer
    obj.QUESTION_id=question_id
    obj.STUDENT_id=student_id
    obj.save()
    return JsonResponse({"status":"ok"})
