from django.contrib import admin
from .models import Post, Comment, Author

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'status', 'created_on')
    list_filter = ('status',)
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug':('title',)}

    def get_form(self, request, obj=None, **kwargs):
        kwargs['help_texts'] = {'content': 'Markdown: blank line between paragraphs, ## heading, - list, **bold**, '
                                           '[link](https://…), ```python fenced code```. Raw HTML also works.'}
        return super().get_form(request, obj, **kwargs)

admin.site.register(Post, PostAdmin)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'body', 'post', 'parent', 'created_on', 'active')
    list_filter = ('active', 'created_on')
    search_fields = ('name', 'email', 'body')
    actions = ['approve_comment']
    def approve_comment(self, request, queryset):
        queryset.update(active=True)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'email', 'phone')


# Register your models here.
