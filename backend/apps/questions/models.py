from django.db import models

from apps.accounts.models import User


class QuestionSet(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="question_sets", verbose_name="Usuário"
    )
    title = models.CharField(verbose_name="Título", max_length=128)
    description = models.CharField(verbose_name="Descrição", max_length=512, null=True)
    prompt = models.TextField(verbose_name="Prompt")
    model = models.CharField(verbose_name="Nome do modelo", max_length=100, null=True)
    created_at = models.DateTimeField(verbose_name="Data de criação", auto_now_add=True)
    status = models.CharField(
        verbose_name="Status",
        max_length=20,
        choices=[
            ("pending", "Pendente"),
            ("success", "Sucesso"),
            ("error", "Erro"),
        ],
    )

    class Meta:
        verbose_name = "Conjunto de questões"
        verbose_name_plural = "Conjuntos de questões"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title


class Question(models.Model):
    question_set = models.ForeignKey(
        QuestionSet,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Conjunto de Questões",
    )
    text = models.TextField(verbose_name="Texto")
    type = models.CharField(
        verbose_name="Tipo",
        max_length=20,
        choices=[
            ("multiple_choice", "Múltipla escolha"),
        ],
    )
    explanation = models.TextField(verbose_name="Explicação")
    created_at = models.DateTimeField(verbose_name="Data de criação", auto_now_add=True)

    class Meta:
        verbose_name = "Questão"
        verbose_name_plural = "Questões"

    def __str__(self) -> str:
        return self.text


class Choice(models.Model):
    question = models.ForeignKey(
        Question, related_name="choices", on_delete=models.CASCADE, verbose_name="Questão"
    )
    text = models.CharField(verbose_name="Texto", max_length=500)
    is_correct = models.BooleanField(verbose_name="Correta", default=False)

    class Meta:
        verbose_name = "Alternativa"
        verbose_name_plural = "Alternativas"

    def __str__(self) -> str:
        return self.text


class PracticeSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    question_set = models.ForeignKey(
        QuestionSet, on_delete=models.CASCADE, verbose_name="Conjunto de Questões"
    )
    questions_order = models.JSONField(verbose_name="Ordem das questões")  # ID list
    current_index = models.SmallIntegerField(verbose_name="Índice atual", default=0)
    created_at = models.DateTimeField(verbose_name="Criado em", auto_now_add=True)

    class Meta:
        verbose_name = "Sessão de prática"
        verbose_name_plural = "Sessões de práticas"

    def __str__(self) -> str:
        return self.question_set.title

    def get_unanswered_indexes(self):
        answered_ids = set(self.answers.values_list("question_id", flat=True))  # pyright: ignore
        unanswered_indexes = [
            i for i, q_id in enumerate(self.questions_order) if q_id not in answered_ids
        ]
        return unanswered_indexes

    def get_next_unanswered_index(self):
        unanswered = self.get_unanswered_indexes()
        return unanswered[0] if unanswered else None


class PracticeAnswer(models.Model):
    session = models.ForeignKey(
        PracticeSession, on_delete=models.CASCADE, related_name="answers", verbose_name="Sessão"
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name="Questão")
    choice = models.ForeignKey(
        Choice, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Alternativa"
    )

    class Meta:
        verbose_name = "Resposta da prática"
        verbose_name_plural = "Respostas das práticas"
