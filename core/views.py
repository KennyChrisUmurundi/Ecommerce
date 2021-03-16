from django.shortcuts import render,get_object_or_404,redirect
from .models import Item, OrderItem,Order,BillingAddress,Payment
from django.conf import settings
from django.views.generic import ListView,DetailView,View
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm
import stripe




class CheckoutView(View):
    def get(self,*args,**kwargs):
        form = CheckoutForm()
        context = {
        'form':form
        }
        return render(self.request,"checkout-page.html",context)
    def post(self,*args,**kwargs):

        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user,ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_adress =form.cleaned_data.get('apartment_adress')
                country =form.cleaned_data.get('country')
                zips = form.cleaned_data.get('zips')
                same_billing_address = form.cleaned_data.get('same_billing_address')
                save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')

                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address = street_address,
                    apartment_adress = apartment_adress,
                    country = country,
                    zips = zips
                )
                #billing_address.save()
                order.billing_address = billing_address
                messages.info(self.request,"Asante Saaanaaaa")
                if payment_option == 'S':
                    return redirect('core:payment',payment_option='Stripe')
                elif payment_option == 'P':
                    return redirect('core:payment',payment_option='Paypal')
                else:
                    return redirect('core:order-summary')
        except ObjectDoesNotExist:
            messages.error(self.request,"Failed!! please check your inputs again")
            return redirect('core:checkout')

        return redirect('core:checkout')

class PaymentView(View):
    def get(self,*args,**kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        context ={
            'order':order,
        }
        return render(self.request,'payment.html',context)

    def post(self,*args,**kwargs):

        token = self.request.POST.get('stripeToken')
        order = Order.objects.get(user=self.request.user, ordered=False)
        amount=int(order.get_total() * 100)

        try:
            stripe.api_key ="sk_test_pNre034ewYPh6rm8OK5MPUYm005DbF1Ivd"

            # `source` is obtained with Stripe.js; see https://stripe.com/docs/payments/accept-a-payment-charges#web-create-token
            charge = stripe.Charge.create(
            amount=amount,# fois 100 kuko ama value ari muma cents!!
            currency="usd",
            source=self.request.POST.get('stripeToken')
            )
            print('token isssssssssss',token)
            payment = Payment()
            payment.user = self.request.user
            payment.stripe_charge_id = charge['id']
            payment.amount = order.get_total()
            payment.timestamp = timezone.now
            payment.save()

            order.ordered = True
            order.save()
            messages.success(self.request,"Successfully")
            return redirect('/')

        except stripe.error.CardError as e:
            messages.error(self.request,"Failed.....cardError!!")
            return redirect('/')

        except stripe.error.RateLimitError as e:
            messages.error(self.request,"Failed............RateLimitError!!")
            return redirect('/')

        except stripe.error.InvalidRequestError as e:
            messages.error(self.request,"Failed.............InvalidResponseError!!")
            print('rabaaaaaaa waaaaanoooooooooooooo',e)
            return redirect('/')

        except stripe.error.AuthenticationError as e:
            messages.error(self.request,"Failed..........AuthError!!")
            return redirect('/')

        except stripe.error.APIConnectionError as e:
            messages.error(self.request,"Failed..........ApiConnection erro!!")
            return redirect('/')

        except stripe.error.StripeError as e:
            messages.error(self.request,"Failed!!")
            return redirect('/')

        except Exception as e:
            messages.error(self.request,"Failed!!")
            print('nooooppe')
            return redirect('/')
        #return render(self.request,'home-page.html')

class HomeView(ListView):
    model = Item
    template_name = 'home-page.html'
    paginate_by = 4

class ProductDetailView(DetailView):
    model = Item
    template_name = 'product.html'


class OrderSummaryView(LoginRequiredMixin,View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user,ordered=False)
            context = {
            'object':order
            }
            return render(self.request,'order_summary.html',context)
        except ObjectDoesNotExist:
            messages.warning(self.request,'No active orders,please add an item :)')
            return redirect("/")


@login_required
def add_to_cart(request,slug):

    item = get_object_or_404(Item,slug=slug)
    order_item,created= OrderItem.objects.get_or_create(item=item,user=request.user,ordered=False)# please understand exactly what this is
    order_qs = Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order table
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request,"Successfuly updated quantity to cart")
            return redirect('core:order-summary')
        else:
            order.items.add(order_item)
            messages.info(request,"Successfuly added to cart")
            return redirect('core:order-summary')
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user,ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request,"Successfuly added to cart")
    return redirect('core:order-summary')

@login_required
def remove_from_cart(request,slug):
    item = get_object_or_404(Item,slug=slug)
    order_qs = Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order table
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item,user=request.user,ordered=False)[0]
            order.items.remove(order_item)
            messages.info(request,"Successfuly removed from cart")
            return redirect('core:order-summary')
        else:
            messages.info(request,"This item is not in your cart")
            return redirect('core:order-summary')

    else:
        messages.info(request,"You do not have an active order")
        return redirect('core:order-summary')
    return redirect('core:order-summary')


@login_required
def remove_single_item_from_cart(request,slug):
    item = get_object_or_404(Item,slug=slug)
    order_qs = Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order table
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item,user=request.user,ordered=False)[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request,"Quantity updated")
            return redirect('core:order-summary')
        else:

            return redirect('core:product',slug=slug)

    else:
        messages.info(request,"You do not have an active order")
        return redirect('core:product',slug=slug)
    return redirect('core:product',slug=slug)


def sellItem(request):
    return render(request, 'sell.html')
