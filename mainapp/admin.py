from django.contrib import admin

from mainapp import models as mainapp_models

@admin.register(mainapp_models.News)
class NewsAdmin(admin.ModelAdmin):
    search_fields = ["title", "preambule", "body"] #find

@admin.register(mainapp_models.Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ["id", "num", "title", "deleted"]
    ordering = ["-course__name", "-num"]
    list_per_page = 5
    list_filter = ["course", "created", "deleted"] #created filter
    actions = ["mark_deleted"]

    def get_course_name(self, obj):
        return obj.course.name

    def mark_deleted(self, request, queryset):
        queryset.update(deleted=True)


