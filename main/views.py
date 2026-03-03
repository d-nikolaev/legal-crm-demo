from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from .models import CaseEvent, Case, Client
from .forms import QuickCaseForm, ClientForm
from datetime import date
from django.db.models import Q

# --- ДНЕВНИК ДЕЛ ---
class CaseListView(ListView):
    model = CaseEvent
    template_name = 'main/index.html'
    context_object_name = 'events'

    def get_queryset(self):
        # Показываем задачи: сначала невыполненные, затем по дате
        queryset = CaseEvent.objects.select_related('case', 'case__client', 'case__defendant').all()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(case__title__icontains=q) | 
                Q(case__client__name__icontains=q) |
                Q(case__defendant__name__icontains=q)
            )
        return queryset.order_by('is_completed', 'date_planned')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = date.today()
        return context

# --- КЛИЕНТЫ ---
def client_list(request):
    clients = Client.objects.all().order_by('-id')
    return render(request, 'main/clients.html', {'clients': clients})

def client_modal(request, pk=None):
    instance = get_object_or_404(Client, pk=pk) if pk else None
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            clients = Client.objects.all().order_by('-id')
            return render(request, 'main/partials/client_table.html', {'clients': clients})
    else:
        form = ClientForm(instance=instance)
    return render(request, 'main/partials/client_form_modal.html', {'form': form, 'instance': instance})

# --- ДЕЛА ---
def case_all_list(request):
    cases = Case.objects.select_related('client', 'defendant').all().order_by('-id')
    return render(request, 'main/cases.html', {'cases': cases})

def case_modal(request, pk=None):
    instance = get_object_or_404(Case, pk=pk) if pk else None
    if request.method == 'POST':
        form = QuickCaseForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            cases = Case.objects.select_related('client', 'defendant').all().order_by('-id')
            return render(request, 'main/partials/case_table.html', {'cases': cases})
    else:
        form = QuickCaseForm(instance=instance)
    return render(request, 'main/partials/case_full_modal.html', {'form': form, 'instance': instance})

# --- HTMX ACTIONS ---
def toggle_event_status(request, pk):
    event = get_object_or_404(CaseEvent, pk=pk)
    event.is_completed = not event.is_completed
    event.save()
    return render(request, 'main/partials/event_card.html', {'event': event, 'today': date.today()})

def create_case_modal(request):
    if request.method == 'POST':
        form = QuickCaseForm(request.POST)
        if form.is_valid():
            form.save()
            # После создания дела возвращаем обновленный список событий для дневника
            events = CaseEvent.objects.select_related('case', 'case__client', 'case__defendant').all().order_by('is_completed', 'date_planned')
            return render(request, 'main/partials/event_list.html', {'events': events, 'today': date.today()})
    else:
        form = QuickCaseForm()
    return render(request, 'main/partials/case_form_modal.html', {'form': form})