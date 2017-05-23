from django.contrib import admin
from .models import *
from django import forms
from .difference_storage import *
from ingester.tests.ingester_tools import get_pub_dict
from django_admin_row_actions import AdminRowActionsMixin
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from .ingest_task import ingest_task
from datetime import  date


class ConfigForm(forms.ModelForm):

    def clean_limit(self):
        if self.cleaned_data["limit"] is None:
            return None

        limit = int(self.cleaned_data["limit"])
        if limit >= 0:
            return limit
        else:
            raise forms.ValidationError(
                _("Limit cannot be negative"),
            )

    def clean_module_name(self):
        try:
            mod = __import__(self.cleaned_data["module_path"], fromlist=[self.cleaned_data["module_name"]])
            getattr(mod, self.cleaned_data["module_name"])
        except Exception as e:
            raise forms.ValidationError(
                _(str(e)),
            )
        return self.cleaned_data["module_name"]


def test(modeladmin, request, queryset):
    for config in queryset.all():
        ingest_task(config.module_path,config.module_name,config.id)
    test.short_description = 'test'


def create_test_dataset(modeladmin,requst,queryset):
    # Medium
    med,x = pub_medium.objects.get_or_create(main_name="Important Journal",
                                           block_name= "important journal",
                                           journal="Important Journal")

    gurl = global_url.objects.get(id=1)
    gurl1,x = global_url.objects.get_or_create(domain="DBLP", url="http:golem.de")
    gurl2,x = global_url.objects.get_or_create(domain="Arxiv", url="google.de")
    lurl1,x = local_url.objects.get_or_create(global_url=gurl1, url="test1", medium=med)
    lurl2,x = local_url.objects.get_or_create(global_url=gurl2, url="test1")

    # publication
    clus,x = cluster.objects.get_or_create(name="test title")
    # differences
    store = generate_diff_store(get_pub_dict(url_id=lurl1.id,
                                             title="TeSt TiTlE",
                                             abstract="This text is common among all sources",
                                             volume="33",
                                             number="66",
                                             doi="http://dblp.uni-trier.de",
                                             note="DBLP NOte",
                                             pages="1-2"))
    added_values1 = get_pub_dict(url_id=lurl2.id,
                                 title="Test title.",
                                 abstract="This text is common among all sources",
                                 note="Arxiv Note",
                                 pages="1-2")
    insert_diff_store(added_values1, store)
    serialized = serialize_diff_store(store)
    pub,x = publication.objects.get_or_create(cluster=clus,
                                            title="TeSt TiTlE",
                                            pages="1-2",
                                            note="DBLP Note",
                                            abstract="This text is common among all sources",
                                            date_published=date(1990,4,17),
                                            volume="33",
                                            number="66",
                                            doi="http://dblp.uni-trier.de",
                                            differences=serialized)

    pubUrl,x = local_url.objects.get_or_create(global_url=gurl, url="BIMBIMBIM", publication=pub, medium=med)
    # Authors
    aut1,x = authors_model.objects.get_or_create(main_name="Trick Wolf", block_name="trick wolf")
    aut2,x = authors_model.objects.get_or_create(main_name="Track Wolf", block_name="track wolf")
    aut3,x = authors_model.objects.get_or_create(main_name="Truck Wolf", block_name="truck wolf")

    alias1,x = author_aliases.objects.get_or_create(alias="Trick Wolf",author=aut1)
    alias2,x = author_aliases.objects.get_or_create(alias="Track Wolf", author=aut2)
    alias3,x = author_aliases.objects.get_or_create(alias="TRACK Wolf", author=aut2)
    alias4,x = author_aliases.objects.get_or_create(alias="Truck Wolf", author=aut3)

    author_alias_source.objects.get_or_create(alias=alias1, url=lurl1)
    author_alias_source.objects.get_or_create(alias=alias2, url=lurl1)
    author_alias_source.objects.get_or_create(alias=alias3, url=lurl2)
    author_alias_source.objects.get_or_create(alias=alias4, url=lurl2)

    publication_author.objects.get_or_create(url=lurl1, author=aut1, priority=1)
    publication_author.objects.get_or_create(url=lurl1, author=aut2, priority=0)
    publication_author.objects.get_or_create(url=lurl2, author=aut2, priority=0)
    publication_author.objects.get_or_create(url=lurl2, author=aut3, priority=1)

    publication_author.objects.get_or_create(url=pubUrl, author=aut1, priority=1)
    publication_author.objects.get_or_create(url=pubUrl, author=aut2, priority=0)
    publication_author.objects.get_or_create(url=pubUrl, author=aut3, priority=2)


    # Keywords
    key1,x = keywordsModel.objects.get_or_create(main_name="Key1", block_name="key1")
    key2, x = keywordsModel.objects.get_or_create(main_name="Key2", block_name="key2")
    key3, x = keywordsModel.objects.get_or_create(main_name="Key3", block_name="key3")
    publication_keyword.objects.get_or_create(url=lurl1, keyword=key1)
    publication_keyword.objects.get_or_create(url=lurl1, keyword=key2)
    publication_keyword.objects.get_or_create(url=lurl1, keyword=key3)
    publication_keyword.objects.get_or_create(url=pubUrl, keyword=key1)
    publication_keyword.objects.get_or_create(url=pubUrl, keyword=key2)
    publication_keyword.objects.get_or_create(url=pubUrl, keyword=key3)

    # references
    # publication
    clus2,x = cluster.objects.get_or_create(name="reference title")
    # differences
    store2 = generate_diff_store(get_pub_dict(url_id=lurl2.id,
                                             title="Reference Title",
                                             abstract="Reference Abstract",
                                             volume="33",
                                             number="66",
                                             doi="http://dblp.uni-trier.de",
                                             note="DBLP NOte",
                                             pages="1-2"))
    serialized2 = serialize_diff_store(store2)
    pub2,x = publication.objects.get_or_create(cluster=clus2,
                                            title="Reference Title",
                                            pages="1-2",
                                            note="Ref Note",
                                            abstract="Reference Abstract",
                                            date_published=date(1990,4,17),
                                            volume="33",
                                            number="66",
                                            doi="http://dblp.uni-trier.de",
                                            differences=serialized2)
    pubUrl2, x = local_url.objects.get_or_create(global_url=gurl, url="Reference1", publication=pub2, medium=med)

    PubReference.objects.get_or_create(source=pubUrl, reference=clus2)




class ConfigAdmin(AdminRowActionsMixin,admin.ModelAdmin):
    form = ConfigForm
    model = Config
    # welche attribute sollen in der listenansicht gezeigt werden
    list_display = ('__str__', 'enabled','limit','module_path', 'module_path')
    """Admin-interface for Ingester Configs."""
    def get_row_actions(self, obj):
        row_actions = [
            {
                'label': 'Log',
                'url': reverse('ingester:config_log', args=[obj.id]),
                'enabled': True,
                'tooltip': "Display ingester Log"
            }
        ]
        row_actions += super(ConfigAdmin, self).get_row_actions(obj)
        return row_actions
    fieldsets = (
        ("General", {
            'fields': ('name','enabled', 'limit',),
            'classes': ('extrapretty', 'wide'),
        }),
        ("Task", {
            'fields': ('schedule', 'module_path', 'module_name',),
            'classes': ('extrapretty', 'wide'),
        }),
    )

    actions = [test,create_test_dataset]



admin.site.register(Config, ConfigAdmin)
