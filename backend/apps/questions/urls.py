from django.urls import path

from . import views

urlpatterns = [
    path("", views.question_sets_view, name="question_sets"),
    path("add/", views.add_question_set_view, name="add_question_set"),
    path("<int:question_set_id>/", views.question_set_view, name="question_set"),
    path(
        "<int:question_set_id>/delete", views.question_set_delete_view, name="question_set_delete"
    ),
    path(
        "<int:question_set_id>/status", views.question_set_status_view, name="question_set_status"
    ),
    path(
        "<int:question_set_id>/practice",
        views.question_set_practice_view,
        name="question_set_practice",
    ),
    path(
        "<int:question_set_id>/practice/<int:session_id>",
        views.question_set_practice_results_view,
        name="question_set_practice_results",
    ),
]
