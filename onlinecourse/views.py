from django.shortcuts import render
from django.http import HttpResponseRedirect
# <HINT> Import any new Models here
from .models import Course, Enrollment, Lesson, Question, Choice, Submission
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic, View
from django.contrib.auth import login, logout, authenticate
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
# Create your views here.


def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


def check_if_enrolled(user, course):
    is_enrolled = False
    if user.id is not None:
        # Check if user enrolled
        num_results = Enrollment.objects.filter(user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled


# CourseListView
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


# class CourseDetailView(View):
#     """
#     Class for the course details view
#     """
#     def get(self, request, *args, **kwargs):
#         """
#         Here is the path:
#         path('<int:pk>/', views.CourseDetailView.as_view(), name='course_details')
#         """
#         context = {}
#         course_id = kwargs.get('pk')
#         course = Course.objects.get(pk=course_id)
#         context['course'] = course
#         lesson_id = Lesson.objects.filter(course_id=course_id).values('id')
#         question = Question.objects.filter(lesson_id=lesson_id)
#         context['question'] = question
#         choices = Choice.objects.filter(question_id=question.values('id'))
#         context['choices'] = choices
#         return render(request, 'onlinecourse/course_detail_bootstrap.html', context)



# This is not part of the above class!!
def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = check_if_enrolled(user, course)
    if not is_enrolled and user.is_authenticated:
        # Create an enrollment
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()

    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))


# <HINT> Create a submit view to create an exam submission record for a course enrollment,
# you may implement it based on following logic:
         # Get user and course object, then get the associated enrollment object created when the user enrolled the course
         # Create a submission object referring to the enrollment
         # Collect the selected choices from exam form
         # Add each selected choice object to the submission object
         # Redirect to show_exam_result with the submission id

# <HINT> A example method to collect the selected choices from the exam form from the request object
def extract_answers(request):
    submitted_anwsers = []
    for key in request.POST:
        if key.startswith('choice'):
            value = request.POST[key]
            choice_id = int(value)
            submitted_anwsers.append(choice_id)
    return submitted_anwsers



def submit(request, course_id):
    user = request.user
    course = get_object_or_404(Course, pk=course_id)
    enrollment = Enrollment.objects.get(user=user, course=course)
    choices = extract_answers(request)
    print("selected_choices", choices)
    submission = Submission(enrollment_id=enrollment)
    submission.save()

    this_choice = Choice.objects.get(question_id=1, is_correct=1)
    print('forced choice:', this_choice.__dict__)

    selected_choice = Choice.objects.get(pk=1)
    print("selected choice:", selected_choice.__dict__)

    for choice in choices:
        this_choice = Choice.objects.get(pk= +choice)
        print("this choice:", this_choice.__dict__)
        submission.choices.add(this_choice)

    return HttpResponseRedirect(reverse(viewname='onlinecourse:show_exam_result', args=(course.id, submission.id)))

 

# <HINT> Create an exam result view to check if learner passed exam and show their question results and result for each question,
# you may implement it based on the following logic:
        # Get course and submission based on their ids
        # Get the selected choice ids from the submission record
        # For each selected choice, check if it is a correct answer or not
        # Calculate the total score

def show_exam_result(request, course_id, submission_id):
    user = request.user
    course = get_object_or_404(Course, pk=course_id)
    print("course dict:", course.__dict__)

    # submission = get_object_or_404(Submission, pk=submission_id)
    submission = Submission.objects.get(pk=submission_id)

    print("submission:", submission)
    print("submission dict:", submission.__dict__)
    print("submission model meta:", Submission._meta.get_fields())

    # Get the course object and submission object based on their ids in view arguments
    # Get the selected choice ids from the submission record
    # For each selected choice, check if it is a correct answer or not
    # Calculate the total score by adding up the grades for all questions in the course
    # Add the course, selected_ids, and grade to context for rendering HTML page

    # For each selected choice, check if the answer was correct or not
    
    # Get the choices
    # choices = submission.choice_set.all()
    # choices = Choice.objects.filter(fk=submission.pk)
    # choices = submission.choice_set.all()
    # choices = submission.choices.all()

    choices = ""

    try:
        choices = Choice.objects.get(submission__id=submission.id).values()
    except:
        choices = Choice.objects.filter(submission__id=submission.id).values()

    print('choices', choices.__dict__)
    print('choices queryset:', choices)

    ids = []
    marks = []
    grades = []

    exam_result_text = []

    for choice in choices:
        print(choice)
        print('id:', choice['id'])
        ids.append(choice['id'])
        question = Question.objects.get(pk=choice['question_id_id'])
        grades.append(+question.grade)

        exam_object = {}
        exam_object['text'] = question.question_text
        # exam_object['answer'] = question.choice_set.get(is_correct=True)
        exam_object['answer'] = Choice.objects.filter(question_id=choice['question_id_id'],
         is_correct=True).values('choice_text')[0]

        exam_object['answer'] = exam_object['answer']['choice_text']

        exam_object['given_answer'] = Choice.objects.filter(pk=choice['id']).values('choice_text')[0]
        exam_object['given_answer'] = exam_object['given_answer']['choice_text']

        exam_result_text.append(exam_object)

        if choice['is_correct'] == True:
            marks.append(+question.grade)

    try:
        print('marks:', sum(marks))
        print('grade:', sum(grades))
        print('score:', sum(marks) / sum(grades))
    except:
        print("couldn't get score")


    # for choice in choices:
    #     choice_object = {}
    #     question = choice.question_set.all()
    #     question_text = question.text
    #     grade = +question.grade
    #     grades.append(grade)
    #     mark = 0
    #     if choice.is_correct == True:
    #         mark = +grade
    #     marks.append(mark)
    #     choice_object['text'] = question_text
    #     choice_object['mark'] = mark

    #     exam_result_text.append(choice_object)

    exam_result = ( sum(marks) / sum(grades) ) * 100
    # exam_result = 0


    context = {}
    context['submission'] = submission
    context['course'] = course
    context['ids'] = ids
    context['grade'] = exam_result
    context['exam_result_text'] = exam_result_text

    # We still need to find out which submissions were correct

    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)



