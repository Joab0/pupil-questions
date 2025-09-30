from django.urls import path

from . import views

urlpatterns = [
    path("", views.question_sets_view, name="question_sets"),
    path("add/", views.add_question_set_view, name="add_question_set"),
    path("<int:question_set_id>/", views.question_set_view, name="question_set"),
    path(
        "<int:question_set_id>/status", views.question_set_status_view, name="question_set_status"
    ),
]
