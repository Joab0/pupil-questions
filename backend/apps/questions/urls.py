from django.urls import path

from . import views

urlpatterns = [
    path("add/", views.add_question_set_view, name="add_question_set"),
    path("<ulid:question_set_id>/", views.question_set_view, name="question_set"),
    path(
        "<ulid:question_set_id>/delete", views.question_set_delete_view, name="question_set_delete"
    ),
    path(
        "<ulid:question_set_id>/status", views.question_set_status_view, name="question_set_status"
    ),
    path(
        "<ulid:question_set_id>/start-practice",
        views.question_set_start_practice_view,
        name="question_set_start_practice",
    ),
    path(
        "practices",
        views.user_practices_view,
        name="user_practices",
    ),
    path(
        "<ulid:question_set_id>/practices/<ulid:session_id>",
        views.question_set_practice_view,
        name="question_set_practice",
    ),
    path(
        "<ulid:question_set_id>/practices/<ulid:session_id>/results",
        views.question_set_practice_results_view,
        name="question_set_practice_results",
    ),
]
