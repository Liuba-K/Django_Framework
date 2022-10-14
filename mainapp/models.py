from django.db import models


class News(models.Model):
    title = models.CharField(max_length=256, verbose_name='Title')
    body = models.TextField(blank=False, null=False, verbose_name='Body')
    body_as_markdown = models.BooleanField(
        default=False,
        verbose_name='As markdown'
    )
    #rate_of_exchange = models.DecimalField(verbose_name='Exchange')
    #euro = models.ForeignKey()
    #five = models.ManyToManyField()
    create_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Date of creating', editable=False
    )
    update_date = models.DateTimeField(
        auto_now=True,
        verbose_name='Date of editing',
        editable=False
    )
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def delete(self, *args):
        self.deleted = True
        self.save()
