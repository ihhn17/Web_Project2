from django.shortcuts import render, get_object_or_404, render_to_response
from django.template.context_processors import csrf
from .models import Category, Product, Comment
from cart.forms import CartAddProductForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import CommentCreateForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from django import forms
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.urls import reverse

from online_shop.settings import ADMIN_EMAIL

def ProductList(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    order_by = request.GET.get("order_by", "")
    if order_by in ("name", "price", "created", "updated"):
        products = products.order_by(order_by)
        if request.GET.get("reverse", "") == '1':
            products = products.reverse()
    else:
        products = products.order_by("created").reverse()

    paginator = Paginator(products, 3)
    page = request.GET.get("page")
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'shop/product/list.html', {
        'category': category,
        'categories': categories,
        'products': products
    })

def ProductDetail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    cart_product_form = CartAddProductForm()
    form = CommentCreateForm()
    context = {
        'product': product,
        'cart_product_form': cart_product_form,
        'form': form,
        'comments': Comment.objects.filter(product=product)
    }
    context.update(csrf(request))
    if request.method == 'POST':
        form = CommentCreateForm(request.POST)
        if form.is_valid():
            Comment.objects.create(product=product, username=form.data['username'], text=form.data['text'])
            return render_to_response('shop/product/detail.html', context)
    return render_to_response('shop/product/detail.html', context)

class ContactForm(forms.Form):
    def __init__(self, *args, **kwargs):
        # call original initializator
        super(ContactForm, self).__init__(*args, **kwargs)

        # this helper object allows us to customize form
        self.helper = FormHelper()

        # form tag attributes
        self.helper.form_class = 'horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('contact_admin')

        # bootstrap styles
        self.helper.help_text_inline = True
        self.helper.html5_required = True
        self.helper.label_class = 'col-sm-2 control-label'
        self.helper.field_class = 'col-sm-10'

        # form buttons
        self.helper.add_input( Submit('send_button', 'Send') )

    from_email = forms.EmailField(
        label="Your email"
    )
    subject = forms.CharField(
        label="Email title",
        max_length=128
    )
    message = forms.CharField(
        label="Message",
        max_length=2048,
        widget=forms.Textarea
    )

def contact_admin(request):
    # check if forn was posted
    if request.method == 'POST':
        # create form instance
        form = ContactForm(request.POST)
        #check whether user data is valid
        if form.is_valid():
            # send email
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            from_email = form.cleaned_data['from_email']

            try:
                send_mail(subject, message, from_email, [ADMIN_EMAIL])
            except Exception:
                message = "Unexpected error has occurred.\nPlease try later"
            else:
                message = "Message was sended successfuly"

            # redirect to the same page with status message
            return HttpResponseRedirect("%s?status_message=%s" %(reverse('contact_admin'), message))
    # if there was not POST render blank form
    else:
        form = ContactForm()
    return render(request, 'contact_admin.html', {'form': form})
