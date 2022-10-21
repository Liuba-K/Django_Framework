from django.views.generic import TemplateView

from .models import News

class MainPageView(TemplateView):
    template_name = "mainapp/index.html"

class NewsPageView(TemplateView):
    template_name = "mainapp/news.html"

    def get_context_data(self, **kwargs):
    # Get all previous data
        context = super().get_context_data(**kwargs)

        context["news"] = News.objects.all()

        return context

class NewsWithPaginatorView(NewsPageView):

    def get_context_data(self, page, **kwargs):
        context = super().get_context_data(page=page, **kwargs)
        context["page_num"] = page
        return context

class CoursesPageView(TemplateView):
    template_name = "mainapp/courses_list.html"

class ContactsPageView(TemplateView):
    template_name = "mainapp/contacts.html"

class DocSitePageView(TemplateView):
    template_name = "mainapp/doc_site.html"


