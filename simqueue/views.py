import logging

import matplotlib
from django.core.urlresolvers import reverse_lazy, reverse
from django.http.response import HttpResponseRedirect
from django.http import Http404
from django.views.generic.edit import CreateView
from django.views.generic import ListView, DetailView, DeleteView
from django.http import HttpResponse

from .tasks import schedule_simulation
from .models import Simulation
from .forms import SimulateForm
from .mixins import LoginRequiredMixin
from .config import generate_config

matplotlib.use('agg')
import aplpy


logger = logging.getLogger(__name__)


class SimulationList(ListView):
    model = Simulation


class SimulationDetail(DetailView):
    model = Simulation

    def get_context_data(self, **kwargs):
        context = super(SimulationDetail, self).get_context_data(**kwargs)
        context['config'] = generate_config(self.object)
        return context


class SimulationConfig(DetailView):
    model = Simulation
    template_name = 'simqueue/config.txt'
    content_type = 'text/plain'


class SimulationDelete(DeleteView):
    model = Simulation
    success_url = reverse_lazy('list')


class SimulationCreate(LoginRequiredMixin, CreateView):
    model = Simulation
    success_url = reverse_lazy('list')
    form_class = SimulateForm

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            self.object = form.save()
            self.object.save()
            schedule_simulation(self.object, request)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class Reschedule(LoginRequiredMixin, DetailView):
    model = Simulation

    def get(self, request, *args, **kwargs):
        super(Reschedule, self).get(self, request, *args, **kwargs)
        return HttpResponseRedirect(reverse('detail', args=(self.object.id,)))

    def post(self, request, *args, **kwargs):
            self.object = self.get_object()
            self.object.clear()
            schedule_simulation(self.object, request)
            return HttpResponseRedirect(reverse('detail',
                                                args=(self.object.id,)))


class SimulationFits(DetailView):
    """
    visualises Filefield model files using aplpy
    """
    model = Simulation
    fits_fields = ['dirty','psf','lwimager_dirty', 'lwimager_model', 'lwimager_residual', 'lwimager_restored',
    'casa_model', 'casa_residual', 'casa_restored',
    'wsclean_model', 'wsclean_residual', 'wsclean_restored',
    'moresane_model', 'moresane_residual', 'moresane_restored',]
    

    def render_to_response(self, context, **kwargs):
        field = self.kwargs['field'];
        if field not in self.fits_fields:
            raise Http404
        response = HttpResponse(content_type='image/png')
        fig = matplotlib.pyplot.figure()

        try:
            filename = str(getattr(self.object, 'results_' + field).file)
            plot = aplpy.FITSFigure(filename, figure=fig,
                                    auto_refresh=False)
        except IOError as e:
            matplotlib.pyplot.text(0.1, 0.8, str(e))
        else:
            plot.show_colorscale()
        fig.canvas.print_figure(response, format='png')
        return response
