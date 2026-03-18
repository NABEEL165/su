


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.conf import settings

from .models import Payment, PaymentConfiguration
from customer_dashboard.models import CustomerWasteInfo

import json
import uuid
import razorpay

def create_razorpay_order(amount, currency="INR"):
    """Create a real Razorpay order"""
    try:
        # Get Razorpay configuration
        config = PaymentConfiguration.objects.filter(
            gateway_name="razorpay",
            is_active=True
        ).first()

        if not config or not config.api_key or not config.secret_key:
            raise Exception("Razorpay configuration not found or incomplete")

        # Initialize Razorpay client
        client = razorpay.Client(auth=(config.api_key, config.secret_key))

        # Create order data
        order_data = {
            'amount': int(amount * 100),  # Convert to paise
            'currency': currency,
            'payment_capture': '1',  # Auto capture payment
            'notes': {
                'created_by': 'SuchiGo Waste Management'
            }
        }

        # Create order with Razorpay
        order = client.order.create(data=order_data)

        return order

    except Exception as e:
        print(f"Razorpay order creation error: {e}")
        # For development/testing, create a mock order
        return {
            "id": f"order_{uuid.uuid4().hex[:10]}",
            "amount": int(amount * 100),  # paise
            "currency": currency,
            "receipt": f"receipt_{uuid.uuid4().hex[:8]}",
            "status": "created"
        }


def verify_razorpay_payment(order_id, payment_id, signature):
    """Verify Razorpay payment signature"""
    try:
        # Get Razorpay configuration
        config = PaymentConfiguration.objects.filter(
            gateway_name="razorpay",
            is_active=True
        ).first()

        if not config or not config.api_key or not config.secret_key:
            return False

        # Initialize Razorpay client
        client = razorpay.Client(auth=(config.api_key, config.secret_key))

        # Verify signature
        params = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }

        client.utility.verify_payment_signature(params)
        return True

    except Exception as e:
        print(f"Payment verification error: {e}")
        return False
@login_required
def initiate_payment(request, waste_info_id):
    # Role check
    if request.user.role == 1:
        waste_info = get_object_or_404(CustomerWasteInfo, id=waste_info_id)
    else:
        waste_info = get_object_or_404(
            CustomerWasteInfo,
            id=waste_info_id,
            user=request.user
        )

    # Fee calculation
    base_amount = 1.0
    bag_charge = 49.0 * (waste_info.number_of_bags or 1)
    total_amount = base_amount + bag_charge

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")

        if payment_method == "razorpay":
            try:
                order_data = create_razorpay_order(total_amount)

                payment = Payment.objects.create(
                    waste_info=waste_info,
                    user=request.user,
                    amount=total_amount,
                    currency="INR",
                    payment_method="razorpay",
                    payment_status="pending",
                    gateway_order_id=order_data["id"],
                    transaction_id=f"txn_{uuid.uuid4().hex[:12]}"
                )

                config = PaymentConfiguration.objects.filter(
                    gateway_name="razorpay",
                    is_active=True
                ).first()

                return render(request, "payments/razorpay_checkout.html", {
                    "waste_info": waste_info,
                    "payment": payment,
                    "order_data": order_data,
                    "razorpay_key": config.api_key if config else "",
                    "total_amount_in_paise": int(total_amount * 100)
                })

            except Exception as e:
                messages.error(request, str(e))
                return redirect("customer:waste_profile_detail", pk=waste_info.id)

        messages.error(request, "Invalid payment method")
        return redirect("customer:waste_profile_detail", pk=waste_info.id)

    return render(request, "payments/payment_options.html", {
        "waste_info": waste_info,
        "total_amount": total_amount
    })


@login_required
def initiate_payment_by_user(request, user_id):
    waste_info = CustomerWasteInfo.objects.filter(
        user_id=user_id
    ).order_by("-created_at").first()

    if not waste_info:
        messages.error(request, "Customer has no waste record")
        return redirect("waste_collector:waste_collect_create")

    return initiate_payment(request, waste_info.id)
@csrf_exempt
def razorpay_webhook(request):
    if request.method != "POST":
        return HttpResponse(status=200)

    try:
        payload = json.loads(request.body)
        event = payload.get("event")

        payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
        order_id = payment_entity.get("order_id")

        payment = Payment.objects.filter(gateway_order_id=order_id).first()
        if not payment:
            return HttpResponse(status=200)

        if event == "payment.captured":
            payment.payment_status = "completed"
            payment.transaction_id = payment_entity.get("id")
            payment.gateway_response = json.dumps(payment_entity)
            payment.save()

            payment.waste_info.status = "confirmed"
            payment.waste_info.save()

        elif event == "payment.failed":
            payment.payment_status = "failed"
            payment.gateway_response = json.dumps(payment_entity)
            payment.save()

        return HttpResponse(status=200)

    except Exception as e:
        print("Webhook Error:", e)
        return HttpResponse(status=500)
@login_required
def payment_success(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)

    # If payment is still pending, check if we have Razorpay response data
    if payment.payment_status == 'pending':
        razorpay_payment_id = request.POST.get('razorpay_payment_id')

        if razorpay_payment_id:
            try:
                # Get Razorpay configuration
                config = PaymentConfiguration.objects.filter(
                    gateway_name="razorpay",
                    is_active=True
                ).first()

                if config and config.api_key and config.secret_key:
                    # Initialize Razorpay client
                    client = razorpay.Client(auth=(config.api_key, config.secret_key))

                    # Fetch payment details from Razorpay
                    razorpay_payment = client.payment.fetch(razorpay_payment_id)

                    # Update payment record
                    payment.transaction_id = razorpay_payment_id
                    payment.gateway_response = json.dumps(razorpay_payment)
                    payment.payment_status = 'completed'
                    payment.save()

                    # Update waste info status
                    payment.waste_info.status = 'confirmed'
                    payment.waste_info.save()

                    messages.success(request, "Payment completed successfully!")
                else:
                    messages.warning(request, "Payment completed but verification failed. Please contact support.")

            except Exception as e:
                print(f"Payment verification error: {e}")
                messages.warning(request, "Payment completed but verification failed. Please contact support.")

    return render(request, "payments/payment_success.html", {"payment": payment})


@login_required
def payment_failure(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    return render(request, "payments/payment_failure.html", {"payment": payment})
def calculate_waste_collection_fee(waste_info):
    base_amount = 100.0
    bag_charge = 40.0 * (waste_info.number_of_bags or 1)

    surcharge_types = [
        "Sanitary Pad",
        "Kids & Adult Diaper",
        "Expiry Medicine",
        "Hair Waste"
    ]

    waste_type_surcharge = 50.0 if waste_info.waste_type in surcharge_types else 0.0
    distance_charge = 15.0 if waste_info.latitude and waste_info.longitude else 0.0

    total = base_amount + bag_charge + waste_type_surcharge + distance_charge
    return round(total, 2)


